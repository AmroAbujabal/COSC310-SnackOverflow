import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import app

# The whole customer journey over HTTP, on a copy of the real seed data.
# No tokens or records are made by hand: everything goes through the API.

SEED_DATA = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture
def client(tmp_path):
    for seed_file in SEED_DATA.glob("*.json"):
        shutil.copy(seed_file, tmp_path)
    app.dependency_overrides[get_settings] = lambda: Settings(data_dir=tmp_path)
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


def sign_up_and_log_in(client, name, email):
    password = "correct-horse-battery"
    response = client.post("/auth/register", json=dict(
        name=name, email=email, password=password, address="1 Main Street"))
    assert response.status_code == 201
    response = client.post("/auth/login", data=dict(username=email, password=password))
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_register_login_cart_checkout_and_view_order(client):
    alice = sign_up_and_log_in(client, "Alice", "alice@example.com")

    # Browse: pick a restaurant and two items from its customer-facing menu.
    restaurant_id = client.get("/restaurants").json()[0]["id"]
    items = client.get(f"/restaurants/{restaurant_id}/menu/items").json()
    assert len(items) >= 2, "seed data: the first restaurant needs 2 orderable items"
    first, second = items[:2]

    for item, quantity in [(first, 2), (second, 1)]:
        response = client.post("/cart/items", headers=alice, json=dict(
            restaurant_id=restaurant_id, item_id=item["item_id"], quantity=quantity))
        assert response.status_code == 200

    cart = client.get("/cart", headers=alice).json()
    expected_total = round(first["price"] * 2 + second["price"], 2)
    assert cart["total"] == expected_total

    # Checkout turns the cart into an order and empties the cart.
    response = client.post("/checkout", headers=alice)
    assert response.status_code == 201
    order = response.json()
    assert order["total"] == expected_total
    assert order["restaurant_id"] == restaurant_id
    assert [(line["item_id"], line["quantity"]) for line in order["lines"]] == [
        (first["item_id"], 2), (second["item_id"], 1)]
    assert client.get("/cart", headers=alice).json()["items"] == []

    # Alice sees her order; it is the same one checkout returned.
    assert client.get("/orders", headers=alice).json() == [order]
    assert client.get(f"/orders/{order['id']}", headers=alice).json() == order

    # Checking out again with the now-empty cart is refused.
    assert client.post("/checkout", headers=alice).status_code == 409

    # Another customer can't see Alice's order, and has none of their own.
    bob = sign_up_and_log_in(client, "Bob", "bob@example.com")
    assert client.get(f"/orders/{order['id']}", headers=bob).status_code == 403
    assert client.get("/orders", headers=bob).json() == []

    # Without a token, nothing about orders is visible.
    assert client.get("/orders").status_code == 401
