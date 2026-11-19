
import json
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from app.core.config import Settings, get_settings
from app.main import app
from app.models.menu_item_requests import MenuItemCreate
from app.core.security import create_access_token

@pytest.fixture
def menu_write_client(tmp_path):
    restaurants = [
        {
            "id": 1,
            "name": "Fine India Dining",
            "cuisine": "Indian",
            "address": "123 Main Street",
            "rating": 4.7,
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

    owner = [
        {
            "id": 1,
            "name": "Test Owner",
            "email": "owner@example.com",
            "password_hash": "not-used-by-token-tests",
            "address": "123 Main Street",
            "role": "owner",
            "is_active": True,
        }
    ]

    (tmp_path / "restaurants.json").write_text(
        json.dumps(restaurants), encoding="utf-8"
    )
    (tmp_path / "menus.json").write_text(
        json.dumps(menus), encoding="utf-8"
    )
    (tmp_path / "customers.json").write_text(
        json.dumps(owner), encoding="utf-8"
    )

    settings = Settings(data_dir=tmp_path)
    token = create_access_token(1, settings)

    app.dependency_overrides[get_settings] = lambda: settings

    try:
        with TestClient(
            app,
            raise_server_exceptions=False,
            headers={"Authorization": f"Bearer {token}"},
        ) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


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
        "available": True,
        "active": True,
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
        "available": True,
        "active": True,
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



@pytest.mark.parametrize("available", [False, True])
def test_create_menu_item_with_availability(menu_write_client, available):
    response = menu_write_client.post(
        "/restaurants/1/menu/items",
        json={"name": "Soup", "price": 5.50, "available": available},
    )
    assert response.status_code == 201
    item = response.json()
    assert item["available"] is available
    saved = menu_write_client.get("/restaurants/1/menu/items?include_unavailable=true").json()
    assert next(i for i in saved if i["item_id"] == item["item_id"])["available"] is available


def test_availability_toggle_persists_and_preserves_other_fields(menu_write_client, tmp_path):
    from app.repositories.menu_repository import MenuRepository

    original = menu_write_client.get("/restaurants/1/menu/items").json()
    assert all(item["available"] is True for item in original)  # Legacy JSON defaults.
    url = "/restaurants/1/menu/items/1"
    response = menu_write_client.patch(url, json={"available": False})
    assert response.status_code == 200
    assert response.json() == {**original[0], "available": False}
    menu = menu_write_client.get("/restaurants/1/menu?include_unavailable=true").json()
    assert menu["items"][0]["available"] is False
    assert menu["items"][1] == original[1]
    # A fresh repository reads the persisted state, without an in-memory cache.
    repo = MenuRepository(Settings(data_dir=tmp_path))
    assert repo.get(1).items[0].available is False
    menu_write_client.patch(url, json={"price": 16.50})
    assert repo.get(1).items[0].available is False
    response = menu_write_client.patch(url, json={"available": True})
    assert response.status_code == 200
    assert repo.get(1).items[0].available is True
    assert repo.get(1).items[0].price == 16.50


@pytest.mark.parametrize("field", ["available", "active"])
@pytest.mark.parametrize("invalid", [None, "false", "yes", 0, 1, [], {}])
@pytest.mark.parametrize("method", ["post", "patch"])
def test_availability_rejects_non_boolean_without_writing(menu_write_client, tmp_path, invalid, method, field):
    path = tmp_path / "menus.json"
    before = path.read_bytes()
    url = "/restaurants/1/menu/items"
    payload = {field: invalid}
    if method == "post":
        payload.update(name="Soup", price=5.50)
    else:
        url += "/1"
    response = getattr(menu_write_client, method)(url, json=payload)
    assert response.status_code == 422
    assert path.read_bytes() == before


@pytest.mark.parametrize("restaurant_id,item_id", [(999, 1), (1, 999), (2, 1)])
def test_availability_update_missing_or_wrong_restaurant(menu_write_client, tmp_path, restaurant_id, item_id):
    path = tmp_path / "menus.json"
    before = path.read_bytes()
    response = menu_write_client.patch(
        f"/restaurants/{restaurant_id}/menu/items/{item_id}",
        json={"available": False},
    )
    assert response.status_code == 404
    assert path.read_bytes() == before


@pytest.mark.parametrize("active", [True, False])
def test_create_active_state_persists(menu_write_client, tmp_path, active):
    response = menu_write_client.post("/restaurants/1/menu/items", json={"name": "Soup", "price": 5, "active": active})
    assert response.status_code == 201
    assert response.json()["active"] is active
    stored = json.loads((tmp_path / "menus.json").read_text(encoding="utf-8"))
    assert stored[0]["items"][-1]["active"] is active


def test_deactivate_hide_and_restore_item(menu_write_client, tmp_path):
    original = menu_write_client.get("/restaurants/1/menu/items").json()[0]
    url = "/restaurants/1/menu/items/1"
    response = menu_write_client.patch(url, json={"active": False})
    assert response.status_code == 200
    assert response.json() == {**original, "active": False}
    assert [i["item_id"] for i in menu_write_client.get("/restaurants/1/menu/items").json()] == [2]
    management = menu_write_client.get("/restaurants/1/menu/items?include_unavailable=true").json()
    assert management[0]["active"] is False
    stored = json.loads((tmp_path / "menus.json").read_text(encoding="utf-8"))
    assert stored[0]["items"][0]["active"] is False
    assert menu_write_client.patch(url, json={"active": True}).status_code == 200
    assert menu_write_client.get("/restaurants/1/menu/items").json()[0] == original


def test_owner_cannot_modify_another_owners_menu(
    owner_client,
    data_dir,
):
    restaurants_path = data_dir / "restaurants.json"

    restaurants = json.loads(
        restaurants_path.read_text(encoding="utf-8")
    )

    # Restaurant 2 belongs to a different owner.
    restaurants[1]["owner_id"] = 2

    restaurants_path.write_text(
        json.dumps(restaurants),
        encoding="utf-8",
    )

    response = owner_client.post(
        "/restaurants/2/menu/items",
        json={
            "name": "Unauthorized Dish",
            "price": 10.00,
        },
    )

    assert response.status_code == 403

    # Confirm the restaurant still belongs to owner 2.
    saved = json.loads(
        restaurants_path.read_text(encoding="utf-8")
    )

    assert saved[1]["owner_id"] == 2
