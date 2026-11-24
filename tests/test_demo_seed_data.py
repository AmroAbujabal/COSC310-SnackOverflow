import json
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.core.security import verify_password
from app.main import app


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

DEMO_ACCOUNTS = {
    "admin@snackoverflow.demo": {
        "password": "AdminDemo2026!",
        "role": "admin",
        "id": 1,
    },
    "owner@snackoverflow.demo": {
        "password": "OwnerDemo2026!",
        "role": "owner",
        "id": 2,
    },
}


@pytest.fixture
def seeded_client(tmp_path):
    """Use copies of the committed seed files so tests never edit them."""

    for filename in (
        "customers.json",
        "restaurants.json",
        "menus.json",
        "carts.json",
    ):
        source = DATA_DIR / filename

        if source.exists():
            shutil.copyfile(source, tmp_path / filename)
        else:
            (tmp_path / filename).write_text("[]", encoding="utf-8")

    settings = Settings(data_dir=tmp_path)

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_settings] = lambda: settings

    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)


def test_demo_accounts_have_valid_argon2_hashes_and_roles():
    customers = json.loads(
        (DATA_DIR / "customers.json").read_text(encoding="utf-8")
    )

    customers_by_email = {
        customer["email"]: customer
        for customer in customers
    }

    # Both demo accounts must exist, but other customer accounts are allowed.
    for email, expected in DEMO_ACCOUNTS.items():
        assert email in customers_by_email

        customer = customers_by_email[email]

        assert customer["id"] == expected["id"]
        assert customer["role"] == expected["role"]
        assert customer["is_active"] is True
        assert customer["password_hash"].startswith("$argon2id$")
        assert verify_password(
            expected["password"],
            customer["password_hash"],
        )


def test_seeded_restaurants_belong_to_demo_owner():
    restaurants = json.loads(
        (DATA_DIR / "restaurants.json").read_text(encoding="utf-8")
    )

    assert restaurants, "Expected seeded restaurants to exist."

    for restaurant in restaurants:
        assert restaurant["owner_id"] == DEMO_ACCOUNTS[
            "owner@snackoverflow.demo"
        ]["id"]


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("admin@snackoverflow.demo", "AdminDemo2026!"),
        ("owner@snackoverflow.demo", "OwnerDemo2026!"),
    ],
)
def test_demo_accounts_can_sign_in(seeded_client, email, password):
    response = seeded_client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )

    assert response.status_code == 200
    assert response.json()["access_token"]


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("admin@snackoverflow.demo", "AdminDemo2026!"),
        ("owner@snackoverflow.demo", "OwnerDemo2026!"),
    ],
)
def test_demo_accounts_can_access_restaurant_management(
    seeded_client,
    email,
    password,
):
    login_response = seeded_client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    restaurants_response = seeded_client.get(
        "/restaurants",
        headers=headers,
    )

    assert restaurants_response.status_code == 200

    restaurants = restaurants_response.json()
    assert restaurants

    restaurant_id = restaurants[0]["id"]

    update_response = seeded_client.patch(
        f"/restaurants/{restaurant_id}",
        json={"name": "Updated Demo Restaurant"},
        headers=headers,
    )

    assert update_response.status_code == 200


def test_new_customer_cannot_manage_restaurants(seeded_client):
    register_response = seeded_client.post(
        "/auth/register",
        json={
            "name": "Regular Customer",
            "email": "regular.customer@example.com",
            "password": "CustomerPassword123!",
            "address": "123 Test Street",
        },
    )

    assert register_response.status_code in (200, 201)

    login_response = seeded_client.post(
        "/auth/login",
        data={
            "username": "regular.customer@example.com",
            "password": "CustomerPassword123!",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    restaurants = seeded_client.get(
        "/restaurants",
        headers=headers,
    )

    assert restaurants.status_code == 200
    restaurant_id = restaurants.json()[0]["id"]

    update_response = seeded_client.patch(
        f"/restaurants/{restaurant_id}",
        json={"name": "Unauthorized Update"},
        headers=headers,
    )

    assert update_response.status_code == 403
