import json

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.core.security import create_access_token
from app.main import app
from app.models.customer import Customer
from app.models.menu_item_requests import MenuItemUpdate
from app.repositories.customer_repository import CustomerRepository
from app.repositories.menu_repository import MenuRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.restaurant_repository import RestaurantRepository
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
def client(settings):
    app.dependency_overrides[get_settings] = lambda: settings
    with TestClient(app) as client:
        client.headers["Authorization"] = f"Bearer {create_access_token(1, settings)}"
        yield client
    app.dependency_overrides.clear()


def add_to_cart(client, item_id, quantity):
    response = client.post("/cart/items", json=dict(restaurant_id=1, item_id=item_id, quantity=quantity))
    assert response.status_code == 200


def update_item(settings, item_id, **changes):
    menus = MenuService(MenuRepository(settings), RestaurantRepository(settings))
    menus.update_menu_item(1, item_id, MenuItemUpdate(**changes))


def test_checkout_places_the_order_and_empties_the_cart(client, settings):
    add_to_cart(client, 1, 3)
    add_to_cart(client, 2, 1)

    response = client.post("/checkout")

    assert response.status_code == 201
    order = response.json()
    assert [(line["name"], line["line_total"]) for line in order["lines"]] == [("Soup", 0.3), ("Bread", 2.5)]
    assert order["total"] == 2.8
    assert client.get("/cart").json()["items"] == []
    assert client.get(f"/orders/{order['id']}").json() == order
    assert OrderRepository(settings).get(order["id"]) is not None  # saved to orders.json


def test_checkout_uses_the_price_at_checkout_and_the_order_keeps_it(client, settings):
    add_to_cart(client, 2, 2)
    update_item(settings, 2, price=3.00)  # price rises after it was added to the cart

    order = client.post("/checkout").json()
    update_item(settings, 2, price=9.99)  # and again after the order was placed

    assert order["total"] == 6.0
    assert client.get(f"/orders/{order['id']}").json()["total"] == 6.0


def test_item_that_became_unavailable_is_409_and_cart_is_kept(client, settings):
    add_to_cart(client, 1, 1)
    update_item(settings, 1, available=False)

    response = client.post("/checkout")

    assert response.status_code == 409
    assert response.json() == {"detail": "Menu item 1 is unavailable or deactivated"}
    assert len(client.get("/cart").json()["items"]) == 1
    assert OrderRepository(settings).list_all() == []


def test_empty_cart_is_409(client):
    response = client.post("/checkout")
    assert response.status_code == 409
    assert response.json() == {"detail": "Your cart is empty"}


def test_checkout_requires_a_token(client):
    del client.headers["Authorization"]
    assert client.post("/checkout").status_code == 401
