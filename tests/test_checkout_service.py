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
    return CheckoutService(order_repo, carts, FakeMenuService(MENU, unavailable)), carts


def test_checkout_saves_an_order_at_current_prices_and_clears_the_cart(order_repo):
    service, carts = make_service(order_repo, make_cart([(1, 2), (2, 3)]))

    order = service.checkout(CUSTOMER)

    assert [(line.name, line.unit_price, line.line_total) for line in order.lines] == [
        ("Butter Chicken", 15.99, 31.98),
        ("Naan", 0.1, 0.3),  # Decimal maths: not 0.30000000000000004
    ]
    assert order.total == 32.28
    assert (order.customer_id, order.restaurant_id) == (1, 1)
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
