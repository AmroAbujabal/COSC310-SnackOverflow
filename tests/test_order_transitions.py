from datetime import datetime, timezone

import pytest

from app.models.order import ORDER_STATUSES, Order, OrderLine
from app.services.exceptions import BusinessRuleError, InvalidOrderTransitionError, OrderNotFoundError
from app.services.order_service import ALLOWED_TRANSITIONS, OrderService, check_transition

VALID = [
    ("placed", "accepted"),
    ("placed", "cancelled"),
    ("accepted", "preparing"),
    ("accepted", "cancelled"),
    ("preparing", "ready"),
    ("ready", "out_for_delivery"),
    ("out_for_delivery", "delivered"),
]

INVALID = [
    ("placed", "preparing"),            # skips a step
    ("placed", "delivered"),            # skips to the end
    ("ready", "accepted"),              # goes backwards
    ("preparing", "cancelled"),         # too late to cancel
    ("out_for_delivery", "cancelled"),  # too late to cancel
    ("delivered", "placed"),            # delivered is final
    ("cancelled", "accepted"),          # cancelled is final
    ("placed", "placed"),               # not a change
    ("placed", "lost"),                 # not a status
]


def make_order(status="placed"):
    line = OrderLine(item_id=1, name="Butter Chicken", unit_price=15.99, quantity=2, line_total=31.98)
    return Order(
        id=0, customer_id=1, restaurant_id=1, lines=[line], total=31.98, status=status,
        created_at=datetime(2026, 11, 18, 12, 0, tzinfo=timezone.utc),
    )


def test_table_covers_every_status_and_nothing_else():
    assert set(ALLOWED_TRANSITIONS) == set(ORDER_STATUSES)
    assert {new for targets in ALLOWED_TRANSITIONS.values() for new in targets} <= set(ORDER_STATUSES)


def test_table_allows_exactly_the_valid_moves():
    allowed = {(current, new) for current, targets in ALLOWED_TRANSITIONS.items() for new in targets}
    assert allowed == set(VALID)


@pytest.mark.parametrize("current, new", VALID)
def test_valid_transition_passes(current, new):
    check_transition(current, new)


@pytest.mark.parametrize("current, new", INVALID)
def test_invalid_transition_raises_a_business_rule_error(current, new):
    with pytest.raises(InvalidOrderTransitionError) as error:
        check_transition(current, new)
    assert isinstance(error.value, BusinessRuleError)  # so main.py maps it to 409


def test_change_status_saves_a_valid_move(order_repo):
    order = order_repo.create(make_order(status="ready"))

    changed = OrderService(order_repo).change_status(order.id, "out_for_delivery")

    assert changed.status == "out_for_delivery"
    assert order_repo.get(order.id) == changed
    assert changed.model_copy(update={"status": "ready"}) == order  # nothing else changed


def test_change_status_rejects_an_invalid_move_and_saves_nothing(order_repo):
    order = order_repo.create(make_order(status="delivered"))

    with pytest.raises(InvalidOrderTransitionError, match="An order cannot go from delivered to preparing"):
        OrderService(order_repo).change_status(order.id, "preparing")

    assert order_repo.get(order.id) == order


def test_change_status_of_unknown_order_is_not_found(order_repo):
    with pytest.raises(OrderNotFoundError):
        OrderService(order_repo).change_status(99, "accepted")


def test_change_status_checks_the_stored_status_not_a_stale_copy(order_repo):
    # Two staff press "accept" on the same order: the second must be refused.
    order = order_repo.create(make_order())
    service = OrderService(order_repo)

    service.change_status(order.id, "accepted")

    with pytest.raises(InvalidOrderTransitionError):
        service.change_status(order.id, "accepted")
