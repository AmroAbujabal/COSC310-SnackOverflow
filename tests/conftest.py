import json

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.core.security import create_access_token
from app.main import app
from app.repositories.order_repository import OrderRepository

RESTAURANTS = [
    {
        "id": 1,
        "name": "Pretty Pizza",
        "cuisine": "Italian",
        "address": "294 Orchid Street",
        "rating": 4.5,
        "owner_id": 1,
    },
    {
        "id": 2,
        "name": "Swift Sushi",
        "cuisine": "Japanese",
        "address": "789 Daisy Road",
        "rating": 4.2,
        "owner_id": 1,
    },
]

MENUS = []
CUSTOMERS = []


@pytest.fixture
def data_dir(tmp_path):
    """Give each test isolated JSON files for every repository."""
    (tmp_path / "restaurants.json").write_text(
        json.dumps(RESTAURANTS), encoding="utf-8"
    )
    (tmp_path / "menus.json").write_text(
        json.dumps(MENUS), encoding="utf-8"
    )
    (tmp_path / "customers.json").write_text(
        json.dumps(CUSTOMERS), encoding="utf-8"
    )
    return tmp_path


@pytest.fixture
def client(data_dir):
    """Unauthenticated API client using isolated test data."""
    app.dependency_overrides[get_settings] = lambda: Settings(data_dir=data_dir)
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def owner_client(data_dir):
    """API client authenticated as an owner for write-endpoint tests."""
    owner = {
        "id": 1,
        "name": "Test Owner",
        "email": "owner@example.com",
        "password_hash": "not-used-by-token-tests",
        "address": "1 Test Street",
        "role": "owner",
        "is_active": True,
    }
    (data_dir / "customers.json").write_text(
        json.dumps([owner]), encoding="utf-8"
    )

    settings = Settings(data_dir=data_dir)
    token = create_access_token(1, settings)
    app.dependency_overrides[get_settings] = lambda: settings

    try:
        with TestClient(
            app,
            headers={"Authorization": f"Bearer {token}"},
        ) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def order_repo(tmp_path):
    (tmp_path / "orders.json").write_text("[]", encoding="utf-8")
    return OrderRepository(Settings(data_dir=tmp_path))
