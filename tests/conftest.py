import json

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import app

RESTAURANTS = [
    {"id": 1, "name": "Pretty Pizza", "cuisine": "Italian", "address": "294 Orchid Street", "rating": 4.5},
    {"id": 2, "name": "Swift Sushi", "cuisine": "Japanese", "address": "789 Daisy Road", "rating": 4.2},
]


@pytest.fixture
def data_dir(tmp_path):
    (tmp_path / "restaurants.json").write_text(json.dumps(RESTAURANTS), encoding="utf-8")
    return tmp_path


@pytest.fixture
def client(data_dir):
    # Point the app at the temporary folder so tests never touch data/.
    app.dependency_overrides[get_settings] = lambda: Settings(data_dir=data_dir)
    yield TestClient(app)
    app.dependency_overrides.clear()
