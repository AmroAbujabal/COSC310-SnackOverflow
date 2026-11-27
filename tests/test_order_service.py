from datetime import datetime, timezone

import pytest

from app.core.config import Settings
from app.models.customer import Customer
from app.models.order import Order, OrderLine
from app.repositories.restaurant_repository import RestaurantRepository
from app.services.exceptions import (
    ForbiddenError,
    InvalidOrderTransitionError,
    OrderForbiddenError,
    OrderNotFoundError,
)
from app.services.order_service import OrderService
from app.services.restaurant_services import RestaurantService


def make_user(user_id, role="customer"):
    return Customer(
        id=user_id, name="User", email=f"u{user_id}@example.com",
        password_hash="hash", address="1 Test St", role=role,
    )


def make_order(customer_id, status="placed"):
    line = OrderLine(item_id=1, name="Butter Chicken", unit_price=15.99, quantity=2, line_total=31.98)
    return Order(
        id=0, customer_id=customer_id, restaurant_id=1, lines=[line], total=31.98, status=status,
        created_at=datetime(2026, 11, 18, 12, 0, tzinfo=timezone.utc),
    )


@pytest.fixture
def service(order_repo):
    return OrderService(order_repo)


@pytest.fixture
def restaurants(data_dir):
    # conftest's restaurant 1 is owned by user 1.
    return RestaurantService(RestaurantRepository(Settings(data_dir=data_dir)))


RESTAURANT_OWNER = make_user(1, role="owner")
OTHER_OWNER = make_user(3, role="owner")
ADMIN = make_user(9, role="admin")
CUSTOMER = make_user(5)


def test_owner_can_get_their_order(order_repo, service):
    order = order_repo.create(make_order(customer_id=1))
    assert service.get_order(order.id, make_user(1)) == order


def test_admin_can_get_any_order(order_repo, service):
    order = order_repo.create(make_order(customer_id=1))
    assert service.get_order(order.id, make_user(9, role="admin")) == order


@pytest.mark.parametrize("role", ["customer", "owner"])
def test_other_users_are_forbidden(order_repo, service, role):
    order = order_repo.create(make_order(customer_id=1))
    with pytest.raises(OrderForbiddenError):
        service.get_order(order.id, make_user(2, role=role))


def test_unknown_order_is_not_found(service):
    with pytest.raises(OrderNotFoundError):
        service.get_order(99, make_user(1))


def test_list_my_orders_returns_only_mine(order_repo, service):
    order_repo.create(make_order(customer_id=1))
    order_repo.create(make_order(customer_id=2))

    orders = service.list_my_orders(make_user(1))

    assert [order.customer_id for order in orders] == [1]


@pytest.mark.parametrize("user", [RESTAURANT_OWNER, ADMIN], ids=["restaurant owner", "admin"])
def test_owner_or_admin_can_move_an_order_on(order_repo, service, restaurants, user):
    order = order_repo.create(make_order(customer_id=5))

    changed = service.update_status(order.id, "accepted", user, restaurants)

    assert changed.status == "accepted"
    assert order_repo.get(order.id).status == "accepted"


@pytest.mark.parametrize("user", [OTHER_OWNER, CUSTOMER], ids=["other owner", "customer"])
def test_others_cannot_move_an_order_on(order_repo, service, restaurants, user):
    order = order_repo.create(make_order(customer_id=5))

    with pytest.raises(ForbiddenError):
        service.update_status(order.id, "accepted", user, restaurants)

    assert order_repo.get(order.id).status == "placed"


def test_update_status_rejects_an_invalid_move(order_repo, service, restaurants):
    order = order_repo.create(make_order(customer_id=5))

    with pytest.raises(InvalidOrderTransitionError):
        service.update_status(order.id, "ready", RESTAURANT_OWNER, restaurants)


def test_update_status_of_unknown_order_is_not_found(service, restaurants):
    with pytest.raises(OrderNotFoundError):
        service.update_status(99, "accepted", ADMIN, restaurants)


@pytest.mark.parametrize("status", ["placed", "accepted"])
@pytest.mark.parametrize("user", [CUSTOMER, ADMIN], ids=["customer who placed it", "admin"])
def test_order_can_be_cancelled_while_placed_or_accepted(order_repo, service, status, user):
    order = order_repo.create(make_order(customer_id=5, status=status))

    assert service.cancel(order.id, user).status == "cancelled"
    assert order_repo.get(order.id).status == "cancelled"


@pytest.mark.parametrize("user", [make_user(6), RESTAURANT_OWNER], ids=["other customer", "restaurant owner"])
def test_only_the_customer_or_admin_can_cancel(order_repo, service, user):
    order = order_repo.create(make_order(customer_id=5))

    with pytest.raises(OrderForbiddenError):
        service.cancel(order.id, user)

    assert order_repo.get(order.id).status == "placed"


@pytest.mark.parametrize("status", ["preparing", "ready", "out_for_delivery", "delivered", "cancelled"])
def test_cancel_is_rejected_once_preparation_has_started(order_repo, service, status):
    order = order_repo.create(make_order(customer_id=5, status=status))

    with pytest.raises(InvalidOrderTransitionError, match=f"from {status} to cancelled"):
        service.cancel(order.id, CUSTOMER)

    assert order_repo.get(order.id).status == status
