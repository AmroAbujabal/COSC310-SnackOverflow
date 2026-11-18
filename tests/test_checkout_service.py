from types import SimpleNamespace

import pytest

from app.core.config import Settings
from app.models.customer import Customer
from app.models.menu_item import MenuItem
from app.repositories.order_repository import OrderRepository
from app.services.checkout_service import CheckoutService
from app.services.exceptions import BusinessRuleError, EmptyCartError

# Fakes follow the cart/menu contract agreed with Al-Munther (2026-11-01):
#   CartService.get_active_cart(customer_id) -> Cart | None, CartService.close_cart(cart_id)
#   MenuService.get_orderable_item(restaurant_id, item_id) -> MenuItem (raises 404/409 itself)


class FakeCartService:
    def __init__(self, cart):
        self.cart = cart
        self.closed = []

    def get_active_cart(self, customer_id):
        return self.cart if self.cart and self.cart.customer_id == customer_id else None

    def close_cart(self, cart_id):
        self.closed.append(cart_id)


class ItemUnavailableError(BusinessRuleError):
    pass


class FakeMenuService:
    def __init__(self, items, unavailable=()):
        self.items = {item.item_id: item for item in items}
        self.unavailable = set(unavailable)

    def get_orderable_item(self, restaurant_id, item_id):
        if item_id in self.unavailable:
            raise ItemUnavailableError(f"Item {item_id} is unavailable")
        return self.items[item_id]


def make_cart(lines, customer_id=1):
    return SimpleNamespace(
        id=7, customer_id=customer_id, restaurant_id=1, status="active",
        lines=[SimpleNamespace(item_id=item_id, quantity=qty) for item_id, qty in lines],
    )


MENU = [
    MenuItem(item_id=1, restaurant_id=1, name="Butter Chicken", price=15.99),
    MenuItem(item_id=2, restaurant_id=1, name="Naan", price=0.1),
]
CUSTOMER = Customer(id=1, name="C", email="c@example.com", password_hash="h", address="1 St")


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "orders.json").write_text("[]", encoding="utf-8")
    return OrderRepository(Settings(data_dir=tmp_path))


def checkout(repo, cart, unavailable=()):
    carts = FakeCartService(cart)
    service = CheckoutService(repo, carts, FakeMenuService(MENU, unavailable))
    return service.checkout(CUSTOMER), carts


def test_checkout_saves_an_order_at_current_prices_and_closes_the_cart(repo):
    order, carts = checkout(repo, make_cart([(1, 2), (2, 3)]))

    assert [(line.name, line.unit_price, line.line_total) for line in order.lines] == [
        ("Butter Chicken", 15.99, 31.98),
        ("Naan", 0.1, 0.3),  # Decimal maths: not 0.30000000000000004
    ]
    assert order.total == 32.28
    assert (order.customer_id, order.restaurant_id) == (1, 1)
    assert order.created_at.tzinfo is not None
    assert repo.get(order.id) == order
    assert carts.closed == [7]


def test_no_active_cart_is_409_and_saves_nothing(repo):
    with pytest.raises(EmptyCartError):
        checkout(repo, None)
    assert repo.list_all() == []


def test_empty_cart_is_409_and_saves_nothing(repo):
    with pytest.raises(EmptyCartError):
        checkout(repo, make_cart([]))
    assert repo.list_all() == []


def test_unavailable_item_saves_nothing_and_keeps_the_cart(repo):
    carts = FakeCartService(make_cart([(1, 1), (2, 1)]))
    service = CheckoutService(repo, carts, FakeMenuService(MENU, unavailable={2}))

    with pytest.raises(ItemUnavailableError):
        service.checkout(CUSTOMER)

    assert repo.list_all() == []
    assert carts.closed == []


def test_cart_stays_open_if_saving_the_order_fails(repo, monkeypatch):
    def broken_create(order):
        raise OSError("disk full")

    monkeypatch.setattr(repo, "create", broken_create)
    carts = FakeCartService(make_cart([(1, 1)]))

    with pytest.raises(OSError):
        CheckoutService(repo, carts, FakeMenuService(MENU)).checkout(CUSTOMER)

    assert carts.closed == []
