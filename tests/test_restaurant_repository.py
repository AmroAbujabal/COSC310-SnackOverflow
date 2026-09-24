import json

import pytest

from app.core.config import Settings
from app.repositories.restaurant_repository import RestaurantRepository


@pytest.fixture
def repository(tmp_path):
    (tmp_path / "restaurants.json").write_text(
        json.dumps(
            [
                {"id": 1, "name": "Pretty Pizza", "cuisine": "Italian", "address": "294 Orchid Street", "rating": 4.5},
                {"id": 2, "name": "Swift Sushi", "cuisine": "Japanese", "address": "789 Daisy Road", "rating": 4.2},
            ]
        ),
        encoding="utf-8",
    )
    return RestaurantRepository(Settings(data_dir=tmp_path))


def test_list_all_returns_every_restaurant(repository):
    restaurants = repository.list_all()
    assert [r.name for r in restaurants] == ["Pretty Pizza", "Swift Sushi"]


def test_get_returns_matching_restaurant(repository):
    assert repository.get(2).name == "Swift Sushi"


def test_get_returns_none_when_id_is_unknown(repository):
    assert repository.get(99) is None


def test_list_all_rejects_a_record_with_a_missing_field(tmp_path):
    (tmp_path / "restaurants.json").write_text(
        json.dumps([{"id": 1, "name": "No Address"}]), encoding="utf-8"
    )
    repository = RestaurantRepository(Settings(data_dir=tmp_path))
    with pytest.raises(ValueError):
        repository.list_all()
