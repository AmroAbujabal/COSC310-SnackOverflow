
import json

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from app.core.config import Settings, get_settings
from app.main import app
from app.models.menu_item_requests import MenuItemCreate


@pytest.fixture
def menu_write_client(tmp_path):
    restaurants = [
        {
            "id": 1,
            "name": "Fine India Dining",
            "cuisine": "Indian",
            "address": "123 Main Street",
            "rating": 4.7,
        },
        {
            "id": 2,
            "name": "Swift Sushi",
            "cuisine": "Japanese",
            "address": "789 Daisy Road",
            "rating": 4.2,
        },
    ]

    menus = [
        {
            "restaurant_id": 1,
            "items": [
                {
                    "item_id": 1,
                    "restaurant_id": 1,
                    "name": "Butter Chicken",
                    "price": 15.99,
                },
                {
                    "item_id": 2,
                    "restaurant_id": 1,
                    "name": "Chicken Biryani",
                    "price": 13.99,
                },
            ],
        }
    ]

    (tmp_path / "restaurants.json").write_text(
        json.dumps(restaurants), encoding="utf-8"
    )
    (tmp_path / "menus.json").write_text(
        json.dumps(menus), encoding="utf-8"
    )

    app.dependency_overrides[get_settings] = (
        lambda: Settings(data_dir=tmp_path)
    )

    try:
        with TestClient(app, raise_server_exceptions=False) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_settings, None)


def test_add_menu_item(menu_write_client, tmp_path):
    response = menu_write_client.post(
        "/restaurants/1/menu/items",
        json={"name": "Vegetable Noodles", "price": 12.50},
    )

    assert response.status_code == 201
    assert response.json() == {
        "item_id": 3,
        "restaurant_id": 1,
        "name": "Vegetable Noodles",
        "price": 12.50,
    }

    saved_menus = json.loads(
        (tmp_path / "menus.json").read_text(encoding="utf-8")
    )
    saved_items = saved_menus[0]["items"]
    assert any(item["name"] == "Vegetable Noodles" for item in saved_items)


def test_add_menu_item_to_restaurant_without_menu(menu_write_client):
    response = menu_write_client.post(
        "/restaurants/2/menu/items",
        json={"name": "Salmon Roll", "price": 9.50},
    )

    assert response.status_code == 201
    assert response.json()["restaurant_id"] == 2
    assert response.json()["item_id"] == 3

    menu_response = menu_write_client.get("/restaurants/2/menu")
    assert menu_response.status_code == 200
    assert menu_response.json()["items"][0]["name"] == "Salmon Roll"


def test_add_menu_item_for_missing_restaurant(menu_write_client):
    response = menu_write_client.post(
        "/restaurants/999/menu/items",
        json={"name": "Mystery Dish", "price": 10.00},
    )

    assert response.status_code == 404


def test_add_menu_item_rejects_nonpositive_price(menu_write_client):
    response = menu_write_client.post(
        "/restaurants/1/menu/items",
        json={"name": "Free Dish", "price": 0},
    )

    assert response.status_code == 422


def test_add_menu_item_rejects_blank_name(menu_write_client):
    response = menu_write_client.post(
        "/restaurants/1/menu/items",
        json={"name": "   ", "price": 10.00},
    )

    assert response.status_code == 422


def test_update_menu_item_preserves_unmodified_fields(menu_write_client):
    response = menu_write_client.patch(
        "/restaurants/1/menu/items/1",
        json={"price": 17.25},
    )

    assert response.status_code == 200
    assert response.json() == {
        "item_id": 1,
        "restaurant_id": 1,
        "name": "Butter Chicken",
        "price": 17.25,
    }


def test_update_menu_item_not_found(menu_write_client):
    response = menu_write_client.patch(
        "/restaurants/1/menu/items/999",
        json={"price": 17.25},
    )

    assert response.status_code == 404


def test_update_menu_item_for_missing_restaurant(menu_write_client):
    response = menu_write_client.patch(
        "/restaurants/999/menu/items/1",
        json={"price": 17.25},
    )

    assert response.status_code == 404


def test_update_menu_item_rejects_empty_body(menu_write_client):
    response = menu_write_client.patch(
        "/restaurants/1/menu/items/1",
        json={},
    )

    assert response.status_code == 422


def test_update_menu_item_rejects_null_price(menu_write_client):
    response = menu_write_client.patch(
        "/restaurants/1/menu/items/1",
        json={"price": None},
    )

    assert response.status_code == 422

def test_add_menu_item_rejects_infinite_price(menu_write_client):
    with pytest.raises(ValidationError):
        MenuItemCreate.model_validate_json(
            '{"name":"Noodles","price":1e400}'
        )

