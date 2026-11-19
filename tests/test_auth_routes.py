import json
import pytest

from app.core.config import Settings
from app.core.security import create_access_token, hash_password


@pytest.mark.parametrize("role", ["owner", "admin"])
def test_register_rejects_elevated_role(client, data_dir, role):
    payload = register_payload()
    payload["role"] = role

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 422

    saved = json.loads(
        (data_dir / "customers.json").read_text(encoding="utf-8")
    )
    assert saved == []


def create_admin_and_customer(data_dir):
    admin = {
        "id": 1,
        "name": "Test Admin",
        "email": "admin@example.com",
        "password_hash": hash_password("admin-password"),
        "address": "1 Admin Street",
        "role": "admin",
        "is_active": True,
    }

    customer = {
        "id": 2,
        "name": "Another Customer",
        "email": "another@example.com",
        "password_hash": hash_password("customer-password"),
        "address": "2 Customer Street",
        "role": "customer",
        "is_active": True,
    }

    (data_dir / "customers.json").write_text(
        json.dumps([admin, customer]),
        encoding="utf-8",
    )

    settings = Settings(data_dir=data_dir)
    token = create_access_token(1, settings)

    return {"Authorization": f"Bearer {token}"}


def register_payload(email="customer@example.com"):
    return {
        "name": "Test Customer",
        "email": email,
        "password": "password123",
        "address": "123 Test Street",
    }


def login(client, email="customer@example.com", password="password123"):
    return client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )


def test_register_customer(client, data_dir):
    response = client.post("/auth/register", json=register_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["email"] == "customer@example.com"
    assert "password_hash" not in body

    saved = json.loads((data_dir / "customers.json").read_text(encoding="utf-8"))
    assert len(saved) == 1
    assert saved[0]["password_hash"] != "password123"
    assert saved[0]["role"] == "customer"


def test_register_rejects_duplicate_email_with_409(client):
    first = client.post("/auth/register", json=register_payload())
    second = client.post(
        "/auth/register",
        json=register_payload("CUSTOMER@example.com"),
    )

    assert first.status_code == 201
    assert second.status_code == 409


def test_login_returns_bearer_token(client):
    client.post("/auth/register", json=register_payload())

    response = login(client)

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_rejects_incorrect_password(client):
    client.post("/auth/register", json=register_payload())

    response = login(client, password="wrong-password")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_login_rejects_unknown_email(client):
    response = login(
        client,
        email="unknown@example.com",
        password="wrong-password",
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"
    assert response.headers["www-authenticate"] == "Bearer"


def test_login_rejects_inactive_customer(client, data_dir):
    customer = {
        "id": 1,
        "name": "Inactive Customer",
        "email": "customer@example.com",
        "password_hash": hash_password("password123"),
        "address": "123 Test Street",
        "role": "customer",
        "is_active": False,
    }
    (data_dir / "customers.json").write_text(
        json.dumps([customer]),
        encoding="utf-8",
    )

    response = login(client)

    assert response.status_code == 401


def test_get_current_user_rejects_missing_and_invalid_tokens(client):
    missing = client.get("/customers/me")
    invalid = client.get(
        "/customers/me",
        headers={"Authorization": "Bearer not-a-valid-token"},
    )

    assert missing.status_code == 401
    assert invalid.status_code == 401


def test_get_current_user_rejects_expired_token(client, data_dir):
    customer = {
        "id": 1,
        "name": "Test Customer",
        "email": "customer@example.com",
        "password_hash": hash_password("password123"),
        "address": "123 Test Street",
        "role": "customer",
        "is_active": True,
    }
    (data_dir / "customers.json").write_text(
        json.dumps([customer]),
        encoding="utf-8",
    )
    settings = Settings(data_dir=data_dir, access_token_expire_minutes=-1)
    token = create_access_token(1, settings)

    response = client.get(
        "/customers/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_get_current_user_rejects_inactive_customer(client, data_dir):
    customer = {
        "id": 1,
        "name": "Inactive Customer",
        "email": "customer@example.com",
        "password_hash": hash_password("password123"),
        "address": "123 Test Street",
        "role": "customer",
        "is_active": False,
    }
    (data_dir / "customers.json").write_text(
        json.dumps([customer]),
        encoding="utf-8",
    )
    settings = Settings(data_dir=data_dir)
    token = create_access_token(1, settings)

    response = client.get(
        "/customers/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_customer_can_get_update_and_deactivate_own_profile(client):
    registered = client.post("/auth/register", json=register_payload())
    assert registered.status_code == 201

    token_response = login(client)
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    profile = client.get("/customers/me", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["name"] == "Test Customer"

    updated = client.patch(
        "/customers/me",
        json={"name": "Updated Customer", "address": "456 New Street"},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Updated Customer"
    assert updated.json()["address"] == "456 New Street"

    deactivated = client.delete("/customers/me", headers=headers)
    assert deactivated.status_code == 200
    assert deactivated.json()["is_active"] is False

    after_deactivation = client.get("/customers/me", headers=headers)
    assert after_deactivation.status_code == 401


def test_customer_cannot_access_another_customers_profile(client, data_dir):
    first = client.post("/auth/register", json=register_payload())
    second = client.post(
        "/auth/register",
        json=register_payload("other@example.com"),
    )
    token = login(client).json()["access_token"]

    response = client.get(
        f"/customers/{second.json()['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert first.status_code == 201
    assert response.status_code == 403


def test_customer_role_cannot_create_restaurant(client):
    client.post("/auth/register", json=register_payload())
    token = login(client).json()["access_token"]

    response = client.post(
        "/restaurants",
        json={
            "name": "Test Restaurant",
            "cuisine": "Test",
            "address": "123 Test Street",
            "rating": 4.0,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_unauthenticated_user_cannot_create_restaurant(client):
    response = client.post(
        "/restaurants",
        json={
            "name": "Test Restaurant",
            "cuisine": "Test",
            "address": "123 Test Street",
            "rating": 4.0,
        },
    )

    assert response.status_code == 401


def test_get_current_user_rejects_token_for_missing_customer(client, data_dir):
    # A correctly signed token is still unauthorized if its customer no longer exists.
    settings = Settings(data_dir=data_dir)
    token = create_access_token(999, settings)

    response = client.get(
        "/customers/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_customer_cannot_update_restaurant_or_menu(client):
    client.post("/auth/register", json=register_payload())
    token = login(client).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    restaurant_response = client.patch(
        "/restaurants/1",
        json={"rating": 4.9},
        headers=headers,
    )
    menu_create_response = client.post(
        "/restaurants/1/menu/items",
        json={"name": "Test Dish", "price": 10.0},
        headers=headers,
    )
    menu_update_response = client.patch(
        "/restaurants/1/menu/items/1",
        json={"price": 11.0},
        headers=headers,
    )

    assert restaurant_response.status_code == 403
    assert menu_create_response.status_code == 403
    assert menu_update_response.status_code == 403


def test_customer_update_rejects_duplicate_email_with_409(client):
    client.post("/auth/register", json=register_payload())
    client.post(
        "/auth/register",
        json=register_payload("other@example.com"),
    )
    token = login(client).json()["access_token"]

    response = client.patch(
        "/customers/me",
        json={"email": "other@example.com"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 409


def test_admin_can_view_another_customer(client, data_dir):
    headers = create_admin_and_customer(data_dir)

    response = client.get(
        "/customers/2",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == 2
    assert response.json()["email"] == "another@example.com"
    assert response.json()["role"] == "customer"
    assert response.json()["is_active"] is True

    # Password hashes must never be exposed.
    assert "password_hash" not in response.json()


def test_admin_can_deactivate_another_customer(client, data_dir):
    headers = create_admin_and_customer(data_dir)

    response = client.delete(
        "/customers/2",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == 2
    assert response.json()["is_active"] is False

    saved = json.loads(
        (data_dir / "customers.json").read_text(encoding="utf-8")
    )

    customer = next(item for item in saved if item["id"] == 2)
    assert customer["is_active"] is False
