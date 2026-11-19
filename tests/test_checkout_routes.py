import json
import threading

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.core.security import create_access_token
from app.main import app
from app.models.cart import CartAdd
from app.models.customer import Customer
from app.models.menu_item_requests import MenuItemUpdate
from app.repositories.cart_repository import CartRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.menu_repository import MenuRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.services.cart_service import CartService
from app.services.checkout_service import CheckoutService
from app.services.menu_services import MenuService

# Real services and JSON files end to end: only the data folder is temporary.


@pytest.fixture
def settings(tmp_path):
    settings = Settings(data_dir=tmp_path)
    restaurants = [dict(id=1, name="Cafe", cuisine="Other", address="Here", rating=4)]
    menus = [dict(restaurant_id=1, items=[
        dict(item_id=1, restaurant_id=1, name="Soup", price=0.10),
        dict(item_id=2, restaurant_id=1, name="Bread", price=2.50),
    ])]
    for name, records in [("restaurants", restaurants), ("menus", menus),
                          ("customers", []), ("carts", []), ("orders", [])]:
        (tmp_path / f"{name}.json").write_text(json.dumps(records), encoding="utf-8")
    CustomerRepository(settings).create(
        Customer(id=0, name="C", email="c@example.com", password_hash="unused", address="Here"))
    return settings


@pytest.fixture
def checkout_client(settings):
    app.dependency_overrides[get_settings] = lambda: settings
    with TestClient(app) as client:
        client.headers["Authorization"] = f"Bearer {create_access_token(1, settings)}"
        yield client
    app.dependency_overrides.clear()


def add_to_cart(checkout_client, item_id, quantity):
    response = checkout_client.post("/cart/items", json=dict(restaurant_id=1, item_id=item_id, quantity=quantity))
    assert response.status_code == 200


def update_item(settings, item_id, **changes):
    menus = MenuService(MenuRepository(settings), RestaurantRepository(settings))
    menus.update_menu_item(1, item_id, MenuItemUpdate(**changes))


def test_checkout_places_the_order_and_empties_the_cart(checkout_client, settings):
    add_to_cart(checkout_client, 1, 3)
    add_to_cart(checkout_client, 2, 1)

    response = checkout_client.post("/checkout")

    assert response.status_code == 201
    order = response.json()
    assert [(line["name"], line["line_total"]) for line in order["lines"]] == [("Soup", 0.3), ("Bread", 2.5)]
    assert order["total"] == 2.8
    assert checkout_client.get("/cart").json()["items"] == []
    assert checkout_client.get(f"/orders/{order['id']}").json() == order
    assert OrderRepository(settings).get(order["id"]) is not None  # saved to orders.json


def test_checkout_uses_the_price_at_checkout_and_the_order_keeps_it(checkout_client, settings):
    add_to_cart(checkout_client, 2, 2)
    update_item(settings, 2, price=3.00)  # price rises after it was added to the cart

    order = checkout_client.post("/checkout").json()
    update_item(settings, 2, price=9.99)  # and again after the order was placed

    assert order["total"] == 6.0
    assert checkout_client.get(f"/orders/{order['id']}").json()["total"] == 6.0


def test_item_that_became_unavailable_is_409_and_cart_is_kept(checkout_client, settings):
    add_to_cart(checkout_client, 1, 1)
    update_item(settings, 1, available=False)

    response = checkout_client.post("/checkout")

    assert response.status_code == 409
    assert response.json() == {"detail": "Menu item 1 is unavailable or deactivated"}
    assert len(checkout_client.get("/cart").json()["items"]) == 1
    assert OrderRepository(settings).list_all() == []


def test_empty_cart_is_409(checkout_client):
    response = checkout_client.post("/checkout")
    assert response.status_code == 409
    assert response.json() == {"detail": "Your cart is empty"}


def test_checkout_requires_a_token(checkout_client):
    del checkout_client.headers["Authorization"]
    assert checkout_client.post("/checkout").status_code == 401


class PausingMenuService(MenuService):
    """Stops checkout part-way through, after it has read the cart but before it clears it."""

    def __init__(self, *args):
        super().__init__(*args)
        self.inside, self.proceed = threading.Event(), threading.Event()

    def get_orderable_item(self, restaurant_id, item_id):
        self.inside.set()
        assert self.proceed.wait(timeout=5)
        return super().get_orderable_item(restaurant_id, item_id)


class SignallingMenuService(MenuService):
    """Lets the test know add_item has passed its menu check and is about to take the cart lock."""

    def __init__(self, *args):
        super().__init__(*args)
        self.checked = threading.Event()

    def get_orderable_item(self, restaurant_id, item_id):
        item = super().get_orderable_item(restaurant_id, item_id)
        self.checked.set()
        return item


def run_in_thread(target):
    results, errors = [], []
    thread = threading.Thread(target=lambda: _capture(target, results, errors))
    thread.start()
    return thread, results, errors


def _capture(target, results, errors):
    try:
        results.append(target())
    except Exception as error:  # surfaced by the test, not lost inside the thread
        errors.append(error)


def test_item_added_during_checkout_is_kept_for_the_next_order(settings):
    # Real services, not HTTP: two requests at once need two threads, which TestClient doesn't do safely.
    def menu(service_class=MenuService):
        return service_class(MenuRepository(settings), RestaurantRepository(settings))

    cart_menu = menu(SignallingMenuService)
    carts = CartService(CartRepository(settings), CustomerRepository(settings), cart_menu)
    paused_menu = menu(PausingMenuService)
    checkout = CheckoutService(OrderRepository(settings), carts, paused_menu)
    customer = CustomerRepository(settings).get(1)
    carts.add_item(1, CartAdd(restaurant_id=1, item_id=1, quantity=1))
    cart_menu.checked.clear()

    checkout_thread, placed, checkout_errors = run_in_thread(lambda: checkout.checkout(customer))
    assert paused_menu.inside.wait(timeout=5)

    add_thread, _, add_errors = run_in_thread(
        lambda: carts.add_item(1, CartAdd(restaurant_id=1, item_id=2, quantity=1)))
    assert cart_menu.checked.wait(timeout=5)
    add_thread.join(timeout=0.2)
    assert add_thread.is_alive()  # waiting on the cart lock that checkout holds

    paused_menu.proceed.set()
    for thread in (checkout_thread, add_thread):
        thread.join(timeout=5)
        assert not thread.is_alive(), "deadlock: a thread never finished"
    assert checkout_errors == [] and add_errors == []

    # The order has what was in the cart when checkout started; the late item waits in the cart.
    assert [line.item_id for line in placed[0].lines] == [1]
    assert [line.item_id for line in carts.get_or_create_active(1).items] == [2]
