import json

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import Settings
from app.repositories.menu_repository import MenuRepository, get_menu_repository

from app.repositories.restaurant_repository import (
    RestaurantRepository,
    get_restaurant_repository,
)


@pytest.fixture
def client(tmp_path):
    menus = [
        {
            "restaurant_id": 1,
            "items": [
                {
                    "item_id": 1,
                    "restaurant_id": 1,
                    "name": "Butter Chicken",
                    "price": 15.99
                },
                {
                    "item_id": 2,
                    "restaurant_id": 1,
                    "name": "Chicken Biryani",
                    "price": 13.99
                }
            ]
        }
    ]

    restaurants = [
        {
            "id": 1,
            "name": "Fine India Dining",
            "cuisine": "Indian",
            "address": "123 Main Street",
            "rating": 4.7
        }
    ]

    (tmp_path / "restaurants.json").write_text(
        json.dumps(restaurants), encoding="utf-8"
    )

    app.dependency_overrides[get_restaurant_repository] = (
        lambda: RestaurantRepository(Settings(data_dir=tmp_path))
    )

    (tmp_path / "menus.json").write_text(
        json.dumps(menus), encoding="utf-8"
    )

    app.dependency_overrides[get_menu_repository] = (
        lambda: MenuRepository(Settings(data_dir=tmp_path))
    )

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_menu_repository, None)
        app.dependency_overrides.pop(get_restaurant_repository, None)


def test_get_menu_success(client):
    response = client.get("/restaurants/1/menu")

    assert response.status_code == 200
    assert response.json()["restaurant_id"] == 1
    assert len(response.json()["items"]) == 2


def test_get_menu_not_found(client):
    response = client.get("/restaurants/999/menu")

    assert response.status_code == 404


def test_get_menu_items_success(client):
    response = client.get("/restaurants/1/menu/items")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Butter Chicken"


def test_get_menu_items_not_found(client):
    response = client.get("/restaurants/999/menu/items")

    assert response.status_code == 404

def test_menu_requires_existing_restaurant(client, tmp_path):
    (tmp_path / "restaurants.json").write_text(
        "[]", encoding="utf-8"
    )

    response = client.get("/restaurants/1/menu")

    assert response.status_code == 404