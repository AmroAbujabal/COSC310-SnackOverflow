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

@pytest.mark.parametrize("endpoint", ["/menu", "/menu/items"])
@pytest.mark.parametrize("query,expected", [("", [1, 2]), ("?include_unavailable=false", [1, 2]),
                                            ("?include_unavailable=true", [1, 2, 3, 4, 5])])
def test_menu_customer_filter_and_management_view(client, tmp_path, endpoint, query, expected):
    path = tmp_path / "menus.json"
    menus = json.loads(path.read_text(encoding="utf-8"))
    for item_id, available, active in [(3, False, True), (4, True, False), (5, False, False)]:
        menus[0]["items"].append(dict(item_id=item_id, restaurant_id=1, name="Hidden", price=5,
                                       available=available, active=active))
    path.write_text(json.dumps(menus), encoding="utf-8")
    before = path.read_bytes()
    response = client.get(f"/restaurants/1{endpoint}{query}")
    assert response.status_code == 200
    items = response.json()["items"] if endpoint == "/menu" else response.json()
    assert [item["item_id"] for item in items] == expected
    assert path.read_bytes() == before


@pytest.mark.parametrize("endpoint", ["/menu", "/menu/items"])
def test_all_hidden_items_return_empty_customer_menu(client, tmp_path, endpoint):
    path = tmp_path / "menus.json"
    menus = json.loads(path.read_text(encoding="utf-8"))
    for item in menus[0]["items"]:
        item["active"] = False
    path.write_text(json.dumps(menus), encoding="utf-8")
    response = client.get(f"/restaurants/1{endpoint}")
    assert response.status_code == 200
    assert (response.json()["items"] if endpoint == "/menu" else response.json()) == []


@pytest.mark.parametrize("endpoint", ["/menu", "/menu/items"])
def test_menu_documents_filter_and_rejects_invalid_flag(client, endpoint):
    path = f"/restaurants/{{restaurant_id}}{endpoint}"
    operation = client.get("/openapi.json").json()["paths"][path]["get"]
    flag = next(p for p in operation["parameters"] if p["name"] == "include_unavailable")
    assert flag["schema"]["default"] is False
    assert flag["description"]
    assert client.get(f"/restaurants/1{endpoint}?include_unavailable=invalid").status_code == 422


def test_service_filter_does_not_mutate_catalog_and_orderability_still_rejects(client, tmp_path):
    from app.models.menu import Menu
    from app.services.exceptions import BusinessRuleError, MenuItemNotFoundError
    from unittest.mock import Mock

    catalog = Menu(restaurant_id=1, items=[
        dict(item_id=1, restaurant_id=1, name="Soup", price=5),
        dict(item_id=2, restaurant_id=1, name="Sold out", price=6, available=False),
        dict(item_id=3, restaurant_id=1, name="Retired", price=7, active=False),
    ])
    repo = Mock()
    repo.get.return_value = catalog
    restaurants = Mock()
    service = MenuService(repo, restaurants)
    assert [i.item_id for i in service.get_menu(1).items] == [1]
    assert len(catalog.items) == 3
    assert len(service.get_menu(1, include_unavailable=True).items) == 3
    assert service.get_orderable_item(1, 1).name == "Soup"
    for item_id in (2, 3):
        with pytest.raises(BusinessRuleError):
            service.get_orderable_item(1, item_id)
    with pytest.raises(MenuItemNotFoundError):
        service.get_orderable_item(1, 999)
