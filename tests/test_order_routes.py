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
    assert response.json() == {"detail": "You do not have access to order 2"}


def test_unknown_order_is_404(orders_client):
    log_in_as(1)
    response = orders_client.get("/orders/99")
    assert response.status_code == 404
    assert response.json() == {"detail": "Order 99 not found"}


@pytest.mark.parametrize("method, path", [
    ("GET", "/orders"), ("GET", "/orders/1"), ("PATCH", "/orders/1/status"), ("POST", "/orders/1/cancel"),
])
def test_orders_require_a_token(orders_client, method, path):
    assert orders_client.request(method, path, json={"status": "accepted"}).status_code == 401


def set_status(data_dir, order_id, status):
    orders = [dict(order, status=status) if order["id"] == order_id else order for order in ORDERS]
    (data_dir / "orders.json").write_text(json.dumps(orders), encoding="utf-8")


# conftest's restaurant 1, which both orders come from, is owned by user 1.

@pytest.mark.parametrize("user_id, role", [(1, "owner"), (9, "admin")], ids=["restaurant owner", "admin"])
def test_staff_move_an_order_on(orders_client, user_id, role):
    log_in_as(user_id, role=role)
    response = orders_client.patch("/orders/2/status", json={"status": "accepted"})
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"
    log_in_as(9, role="admin")
    assert orders_client.get("/orders/2").json()["status"] == "accepted"


@pytest.mark.parametrize("user_id, role", [(3, "owner"), (2, "customer")], ids=["other owner", "customer"])
def test_others_cannot_change_status(orders_client, user_id, role):
    log_in_as(user_id, role=role)
    response = orders_client.patch("/orders/2/status", json={"status": "accepted"})
    assert response.status_code == 403


def test_invalid_status_move_is_409(orders_client):
    log_in_as(1, role="owner")
    response = orders_client.patch("/orders/2/status", json={"status": "ready"})
    assert response.status_code == 409
    assert response.json() == {"detail": "An order cannot go from placed to ready"}


@pytest.mark.parametrize("status", ["out_for_delivery", "delivered", "placed"])
def test_patch_only_accepts_staff_statuses(orders_client, status):
    # out_for_delivery and delivered are set by the delivery flow, not by this endpoint.
    log_in_as(9, role="admin")
    assert orders_client.patch("/orders/2/status", json={"status": status}).status_code == 422


def test_patch_unknown_order_is_404(orders_client):
    log_in_as(9, role="admin")
    assert orders_client.patch("/orders/99/status", json={"status": "accepted"}).status_code == 404


@pytest.mark.parametrize("status", ["placed", "accepted"])
def test_customer_cancels_their_order(orders_client, data_dir, status):
    set_status(data_dir, 1, status)
    log_in_as(1)
    response = orders_client.post("/orders/1/cancel")
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_admin_cancels_any_order(orders_client):
    log_in_as(9, role="admin")
    assert orders_client.post("/orders/2/cancel").json()["status"] == "cancelled"


def test_cannot_cancel_someone_elses_order(orders_client):
    log_in_as(1)
    assert orders_client.post("/orders/2/cancel").status_code == 403


def test_cancel_after_preparation_started_is_409(orders_client, data_dir):
    set_status(data_dir, 1, "preparing")
    log_in_as(1)
    response = orders_client.post("/orders/1/cancel")
    assert response.status_code == 409
    assert response.json() == {"detail": "An order cannot go from preparing to cancelled"}


@pytest.mark.parametrize("status", ["delivered", "cancelled"])
def test_finished_orders_stay_retrievable(orders_client, data_dir, status):
    set_status(data_dir, 1, status)
    log_in_as(1)
    assert orders_client.get("/orders/1").json()["status"] == status
    assert [order["status"] for order in orders_client.get("/orders").json()] == [status]

