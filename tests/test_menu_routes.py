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
from app.services.exceptions import MenuNotFoundError
from app.services.menu_services import MenuService

NO_MENU_RESTAURANT = {"id": 2, "name": "No Menu Cafe", "cuisine": "Cafe", "address": "1 Empty St", "rating": 3.0}


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
    assert response.json() == {"detail": "Restaurant 999 not found"}


def test_get_menu_items_success(client):
    response = client.get("/restaurants/1/menu/items")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Butter Chicken"


def test_get_menu_items_not_found(client):
    response = client.get("/restaurants/999/menu/items")

    assert response.status_code == 404
    assert response.json() == {"detail": "Restaurant 999 not found"}

def test_menu_requires_existing_restaurant(client, tmp_path):
    (tmp_path / "restaurants.json").write_text(
        "[]", encoding="utf-8"
    )

    response = client.get("/restaurants/1/menu")

    assert response.status_code == 404


@pytest.mark.parametrize("path", ["/restaurants/2/menu", "/restaurants/2/menu/items"])
def test_restaurant_without_menu_is_404(client, tmp_path, path):
    # Restaurant 2 exists but has no menu.
    restaurants = json.loads((tmp_path / "restaurants.json").read_text(encoding="utf-8"))
    (tmp_path / "restaurants.json").write_text(
        json.dumps(restaurants + [NO_MENU_RESTAURANT]), encoding="utf-8"
    )

    response = client.get(path)

    assert response.status_code == 404
    assert response.json() == {"detail": "Menu for restaurant 2 not found"}


def test_service_raises_menu_not_found(data_dir):
    # conftest's restaurant 2, no menus.
    (data_dir / "menus.json").write_text("[]", encoding="utf-8")
    settings = Settings(data_dir=data_dir)
    service = MenuService(MenuRepository(settings), RestaurantRepository(settings))

    with pytest.raises(MenuNotFoundError):
        service.get_menu(2)