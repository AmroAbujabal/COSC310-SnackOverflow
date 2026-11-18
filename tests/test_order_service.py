from datetime import datetime, timezone

import pytest

from app.core.config import Settings
from app.models.customer import Customer
from app.models.order import Order, OrderLine
from app.repositories.order_repository import OrderRepository
from app.services.exceptions import OrderForbiddenError, OrderNotFoundError
from app.services.order_service import OrderService


def make_user(user_id, role="customer"):
    return Customer(
        id=user_id, name="User", email=f"u{user_id}@example.com",
        password_hash="hash", address="1 Test St", role=role,
    )


def make_order(customer_id):
    line = OrderLine(item_id=1, name="Butter Chicken", unit_price=15.99, quantity=2, line_total=31.98)
    return Order(
        id=0, customer_id=customer_id, restaurant_id=1, lines=[line], total=31.98,
        created_at=datetime(2026, 11, 18, 12, 0, tzinfo=timezone.utc),
    )


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "orders.json").write_text("[]", encoding="utf-8")
    return OrderRepository(Settings(data_dir=tmp_path))


@pytest.fixture
def service(repo):
    return OrderService(repo)


def test_owner_can_get_their_order(repo, service):
    order = repo.create(make_order(customer_id=1))
    assert service.get_order(order.id, make_user(1)) == order


def test_admin_can_get_any_order(repo, service):
    order = repo.create(make_order(customer_id=1))
    assert service.get_order(order.id, make_user(9, role="admin")) == order


@pytest.mark.parametrize("role", ["customer", "owner"])
def test_other_users_are_forbidden(repo, service, role):
    order = repo.create(make_order(customer_id=1))
    with pytest.raises(OrderForbiddenError):
        service.get_order(order.id, make_user(2, role=role))


def test_unknown_order_is_not_found(service):
    with pytest.raises(OrderNotFoundError):
        service.get_order(99, make_user(1))


def test_list_my_orders_returns_only_mine(repo, service):
    repo.create(make_order(customer_id=1))
    repo.create(make_order(customer_id=2))

    orders = service.list_my_orders(make_user(1))

    assert [order.customer_id for order in orders] == [1]
