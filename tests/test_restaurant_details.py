import json

import pytest

from app.core.config import Settings
from app.repositories.restaurant_repository import RestaurantRepository
from app.services.exceptions import RestaurantNotFoundError
from app.services.restaurant_services import RestaurantService


def test_get_restaurant_returns_its_details(client):
    response = client.get("/restaurants/2")
    assert response.status_code == 200
    assert response.json() == {
        "id": 2,
        "name": "Swift Sushi",
        "cuisine": "Japanese",
        "address": "789 Daisy Road",
        "rating": 4.2,
    }


def test_unknown_restaurant_returns_404(client):
    response = client.get("/restaurants/99")
    assert response.status_code == 404
    assert response.json() == {"detail": "Restaurant 99 not found"}


def test_non_integer_id_returns_422(client):
    assert client.get("/restaurants/abc").status_code == 422


def test_docs_list_the_404_response(client):
    paths = client.get("/openapi.json").json()["paths"]
    not_found = paths["/restaurants/{restaurant_id}"]["get"]["responses"]["404"]
    assert not_found["content"]["application/json"]["schema"]["$ref"].endswith("/ErrorResponse")


def test_service_raises_for_unknown_restaurant(data_dir):
    service = RestaurantService(RestaurantRepository(Settings(data_dir=data_dir)))
    with pytest.raises(RestaurantNotFoundError):
        service.get_restaurant(99)


@pytest.fixture
def empty_data_dir(tmp_path_factory):
    path = tmp_path_factory.mktemp("empty_data")
    (path / "restaurants.json").write_text(json.dumps([]), encoding="utf-8")
    return path


def test_service_raises_when_repo_has_no_restaurants(empty_data_dir):
    service = RestaurantService(RestaurantRepository(Settings(data_dir=empty_data_dir)))
    with pytest.raises(RestaurantNotFoundError):
        service.get_restaurant(1)


def test_empty_repo_lists_no_restaurants(empty_data_dir):
    service = RestaurantService(RestaurantRepository(Settings(data_dir=empty_data_dir)))
    assert service.list_restaurants() == []
