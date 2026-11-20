"""Checks that the committed demo accounts can use management endpoints."""

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
            (tmp_path / filename).write_text(
                "[]",
                encoding="utf-8",
            )

    settings = Settings(data_dir=tmp_path)

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_settings] = lambda: settings

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)


def test_demo_accounts_have_valid_argon2_hashes_and_roles():
    customers = json.loads(
        (DATA_DIR / "customers.json").read_text(encoding="utf-8")
    )

    assert {customer["email"] for customer in customers} == set(DEMO_ACCOUNTS)

    for customer in customers:
        expected = DEMO_ACCOUNTS[customer["email"]]

        assert customer["id"] == expected["id"]
        assert customer["role"] == expected["role"]
        assert customer["is_active"] is True
        assert customer["password_hash"].startswith("$argon2id$")

        assert verify_password(
            expected["password"],
            customer["password_hash"],
        )


def test_every_seeded_restaurant_belongs_to_the_demo_owner():
    customers = json.loads(
        (DATA_DIR / "customers.json").read_text(encoding="utf-8")
    )
    restaurants = json.loads(
        (DATA_DIR / "restaurants.json").read_text(encoding="utf-8")
    )

    owner = next(
        customer
        for customer in customers
        if customer["role"] == "owner"
    )

    assert restaurants

    assert all(
        restaurant["owner_id"] == owner["id"]
        for restaurant in restaurants
    )


@pytest.mark.parametrize(
    "email,account",
    DEMO_ACCOUNTS.items(),
)
def test_demo_account_can_log_in_and_manage_seeded_restaurant(
    seeded_client,
    email,
    account,
):
    login = seeded_client.post(
        "/auth/login",
        data={
            "username": email,
            "password": account["password"],
        },
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}",
    }

    response = seeded_client.patch(
        "/restaurants/1",
        json={"rating": 4.8},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["rating"] == 4.8

    menu_response = seeded_client.post(
        "/restaurants/1/menu/items",
        json={
            "name": "Demo Test Item",
            "price": 5.25,
        },
        headers=headers,
    )

    assert menu_response.status_code == 201
    assert menu_response.json()["name"] == "Demo Test Item"


def test_newly_registered_customer_cannot_manage_seeded_restaurant(
    seeded_client,
):
    registration = seeded_client.post(
        "/auth/register",
        json={
            "name": "Regular Demo Customer",
            "email": "customer@example.com",
            "password": "CustomerDemo2026!",
            "address": "1 Customer Street",
        },
    )

    assert registration.status_code == 201
    assert registration.json()["role"] == "customer"

    login = seeded_client.post(
        "/auth/login",
        data={
            "username": "customer@example.com",
            "password": "CustomerDemo2026!",
        },
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    response = seeded_client.patch(
        "/restaurants/1",
        json={"rating": 1.0},
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 403
