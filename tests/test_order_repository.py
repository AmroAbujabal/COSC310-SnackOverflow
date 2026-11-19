from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from app.core.config import Settings
from app.models.order import Order, OrderLine
from app.repositories.order_repository import OrderRepository


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


def test_create_assigns_next_id(order_repo):
    assert order_repo.create(make_order()).id == 1
    assert order_repo.create(make_order()).id == 2


def test_created_order_survives_a_new_repository(order_repo, tmp_path):
    created = order_repo.create(make_order())

    # A fresh repository re-reads the file, like a server restart.
    reloaded = OrderRepository(Settings(data_dir=tmp_path)).get(created.id)

    assert reloaded == created


def test_get_unknown_order_returns_none(order_repo):
    assert order_repo.get(99) is None


def test_list_for_customer_returns_only_their_orders(order_repo):
    order_repo.create(make_order(customer_id=1))
    order_repo.create(make_order(customer_id=2))
    order_repo.create(make_order(customer_id=1))

    assert [order.id for order in order_repo.list_for_customer(1)] == [1, 3]


def test_concurrent_creates_get_unique_ids_and_none_are_lost(order_repo):
    with ThreadPoolExecutor(max_workers=8) as pool:
        created = list(pool.map(lambda _: order_repo.create(make_order()), range(20)))

    assert sorted(order.id for order in created) == list(range(1, 21))
    assert len(order_repo.list_all()) == 20
