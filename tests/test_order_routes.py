import json

import pytest

from app.dependencies.auth import get_current_user
from app.main import app
from app.models.customer import Customer

LINE = {"item_id": 1, "name": "Butter Chicken", "unit_price": 15.99, "quantity": 2, "line_total": 31.98}
ORDERS = [
    {"id": 1, "customer_id": 1, "restaurant_id": 1, "lines": [LINE], "total": 31.98,
     "status": "placed", "created_at": "2026-11-18T12:00:00Z"},
    {"id": 2, "customer_id": 2, "restaurant_id": 1, "lines": [LINE], "total": 31.98,
     "status": "placed", "created_at": "2026-11-18T12:05:00Z"},
]


@pytest.fixture
def orders_client(client, data_dir):
    (data_dir / "orders.json").write_text(json.dumps(ORDERS), encoding="utf-8")
    return client


def log_in_as(user_id, role="customer"):
    # Skip the JWT: these tests are about who may see which order, not about tokens.
    user = Customer(id=user_id, name="User", email=f"u{user_id}@example.com",
                    password_hash="hash", address="1 Test St", role=role)
    app.dependency_overrides[get_current_user] = lambda: user


def test_my_orders_lists_only_the_callers_orders(orders_client):
    log_in_as(1)
    response = orders_client.get("/orders")
    assert response.status_code == 200
    assert [order["id"] for order in response.json()] == [1]


def test_owner_gets_their_order(orders_client):
    log_in_as(1)
    response = orders_client.get("/orders/1")
    assert response.status_code == 200
    assert response.json()["lines"][0]["name"] == "Butter Chicken"


def test_admin_gets_any_order(orders_client):
    log_in_as(9, role="admin")
    assert orders_client.get("/orders/2").status_code == 200


def test_someone_elses_order_is_403(orders_client):
    log_in_as(1)
    response = orders_client.get("/orders/2")
    assert response.status_code == 403
    assert response.json() == {"detail": "You cannot view order 2"}


def test_unknown_order_is_404(orders_client):
    log_in_as(1)
    response = orders_client.get("/orders/99")
    assert response.status_code == 404
    assert response.json() == {"detail": "Order 99 not found"}


@pytest.mark.parametrize("path", ["/orders", "/orders/1"])
def test_orders_require_a_token(orders_client, path):
    assert orders_client.get(path).status_code == 401
