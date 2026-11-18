from datetime import datetime, timezone

import pytest

from app.core.config import Settings
from app.models.order import Order, OrderLine
from app.repositories.order_repository import OrderRepository


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "orders.json").write_text("[]", encoding="utf-8")
    return OrderRepository(Settings(data_dir=tmp_path))


def make_order(customer_id=1):
    line = OrderLine(item_id=1, name="Butter Chicken", unit_price=15.99, quantity=2, line_total=31.98)
    return Order(
        id=0,
        customer_id=customer_id,
        restaurant_id=1,
        lines=[line],
        total=31.98,
        created_at=datetime(2026, 11, 18, 12, 0, tzinfo=timezone.utc),
    )


def test_create_assigns_next_id(repo):
    assert repo.create(make_order()).id == 1
    assert repo.create(make_order()).id == 2


def test_created_order_survives_a_new_repository(repo, tmp_path):
    created = repo.create(make_order())

    # A fresh repository re-reads the file, like a server restart.
    reloaded = OrderRepository(Settings(data_dir=tmp_path)).get(created.id)

    assert reloaded == created


def test_get_unknown_order_returns_none(repo):
    assert repo.get(99) is None


def test_list_for_customer_returns_only_their_orders(repo):
    repo.create(make_order(customer_id=1))
    repo.create(make_order(customer_id=2))
    repo.create(make_order(customer_id=1))

    assert [order.id for order in repo.list_for_customer(1)] == [1, 3]
