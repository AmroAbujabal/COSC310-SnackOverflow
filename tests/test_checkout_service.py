import time
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import pytest

from app.models.customer import Customer
from app.models.menu_item import MenuItem
from app.services.checkout_service import CheckoutService
from app.services.exceptions import BusinessRuleError, EmptyCartError

# Fakes mirror Al-Munther's CartService (get_or_create_active, clear) and
# MenuService.get_orderable_item, so these tests isolate the checkout rules.
# tests/test_checkout_routes.py runs checkout against the real services.


class FakeCartService:
    def __init__(self, cart):
        self.cart = cart
        self.cleared = []

    def get_or_create_active(self, customer_id):
        return self.cart

    def clear(self, customer_id):
        self.cleared.append(customer_id)


class FakeMenuService:
    def __init__(self, items, unavailable=()):
        self.items = {item.item_id: item for item in items}
        self.unavailable = set(unavailable)

    def get_orderable_item(self, restaurant_id, item_id):
        if item_id in self.unavailable:
            raise BusinessRuleError(f"Menu item {item_id} is unavailable or deactivated")
        return self.items[item_id]


class FakeRestaurantService:
    def get_restaurant(self, restaurant_id):
        return SimpleNamespace(id=restaurant_id, name="Pretty Pizza")


def make_cart(lines):
    return SimpleNamespace(
        restaurant_id=1,
        items=[SimpleNamespace(item_id=item_id, quantity=qty) for item_id, qty in lines],
    )


MENU = [
    MenuItem(item_id=1, restaurant_id=1, name="Butter Chicken", price=15.99),
    MenuItem(item_id=2, restaurant_id=1, name="Naan", price=0.1),
]
CUSTOMER = Customer(id=1, name="C", email="c@example.com", password_hash="h", address="1 St")


def make_service(order_repo, cart, unavailable=()):
    carts = FakeCartService(cart)
    return CheckoutService(order_repo, carts, FakeMenuService(MENU, unavailable), FakeRestaurantService()), carts


def test_checkout_saves_an_order_at_current_prices_and_clears_the_cart(order_repo):
    service, carts = make_service(order_repo, make_cart([(1, 2), (2, 3)]))

    order = service.checkout(CUSTOMER)

    assert [(line.name, line.unit_price, line.line_total) for line in order.lines] == [
        ("Butter Chicken", 15.99, 31.98),
        ("Naan", 0.1, 0.3),  # Decimal maths: not 0.30000000000000004
    ]
    assert order.total == 32.28
    assert (order.customer_id, order.restaurant_id) == (1, 1)
    assert (order.restaurant_name, order.delivery_address) == ("Pretty Pizza", "1 St")
    assert order.created_at.tzinfo is not None
    assert order_repo.get(order.id) == order
    assert carts.cleared == [1]


def test_empty_cart_is_409_and_saves_nothing(order_repo):
    service, _ = make_service(order_repo, make_cart([]))

    with pytest.raises(EmptyCartError):
        service.checkout(CUSTOMER)

    assert order_repo.list_all() == []


def test_unavailable_item_saves_nothing_and_keeps_the_cart(order_repo):
    service, carts = make_service(order_repo, make_cart([(1, 1), (2, 1)]), unavailable={2})

    with pytest.raises(BusinessRuleError):
        service.checkout(CUSTOMER)

    assert order_repo.list_all() == []
    assert carts.cleared == []


def test_cart_stays_open_if_saving_the_order_fails(order_repo, monkeypatch):
    def broken_create(order):
        raise OSError("disk full")

    monkeypatch.setattr(order_repo, "create", broken_create)
    service, carts = make_service(order_repo, make_cart([(1, 1)]))

    with pytest.raises(OSError):
        service.checkout(CUSTOMER)

    assert carts.cleared == []


def test_order_is_removed_if_emptying_the_cart_fails(order_repo):
    # Otherwise the error tells the customer to retry, and the retry orders the same cart twice.
    service, carts = make_service(order_repo, make_cart([(1, 1)]))

    def broken_clear(customer_id):
        raise OSError("disk full")

    carts.clear = broken_clear

    with pytest.raises(OSError):
        service.checkout(CUSTOMER)

    assert order_repo.list_all() == []


def test_if_the_undo_also_fails_the_original_error_is_raised(order_repo, monkeypatch, caplog):
    service, carts = make_service(order_repo, make_cart([(1, 1)]))

    def broken_clear(customer_id):
        raise OSError("cart disk full")

    def broken_delete(order_id):
        raise OSError("orders disk full")

    carts.clear = broken_clear
    monkeypatch.setattr(order_repo, "delete", broken_delete)

    with pytest.raises(OSError, match="cart disk full"):
        service.checkout(CUSTOMER)

    assert "Could not undo order 1" in caplog.text


class SlowRealisticCart(FakeCartService):
    """Reads slowly and really empties on clear, so overlapping checkouts can race."""

    def get_or_create_active(self, customer_id):
        cart = make_cart([(line.item_id, line.quantity) for line in self.cart.items])
        time.sleep(0.05)
        return cart

    def clear(self, customer_id):
        self.cart = make_cart([])


def test_double_click_checkout_places_only_one_order(order_repo):
    carts = SlowRealisticCart(make_cart([(1, 1)]))
    service = CheckoutService(order_repo, carts, FakeMenuService(MENU), FakeRestaurantService())

    def attempt(_):
        try:
            return service.checkout(CUSTOMER)
        except EmptyCartError:
            return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, range(2)))

    assert len(order_repo.list_all()) == 1
    assert results.count(None) == 1
