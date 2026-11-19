from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.models.order import Order, OrderLine


def make_line(**overrides):
    fields = {"item_id": 1, "name": "Butter Chicken", "unit_price": 15.99, "quantity": 2, "line_total": 31.98}
    return OrderLine(**(fields | overrides))


def make_order(**overrides):
    fields = {
        "id": 1,
        "customer_id": 1,
        "restaurant_id": 1,
        "lines": [make_line()],
        "total": 31.98,
        "created_at": datetime.now(timezone.utc),
    }
    return Order(**(fields | overrides))


def test_valid_order_defaults_to_placed():
    assert make_order().status == "placed"


def test_line_total_must_match_price_times_quantity():
    with pytest.raises(ValidationError):
        make_line(line_total=99.0)


def test_quantity_must_be_positive():
    with pytest.raises(ValidationError):
        make_line(quantity=0, line_total=0.0)


def test_total_must_match_lines():
    with pytest.raises(ValidationError):
        make_order(total=1.0)


def test_order_needs_at_least_one_line():
    with pytest.raises(ValidationError):
        make_order(lines=[], total=0.0)
