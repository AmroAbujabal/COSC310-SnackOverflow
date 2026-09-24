import json

from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import app


def test_get_restaurants(tmp_path):
    # Create a temporary restaurants.json
    (tmp_path / "restaurants.json").write_text(
        json.dumps(
            [
                {
                    "id": 1,
                    "name": "Pretty Pizza",
                    "cuisine": "Italian",
                    "address": "294 Orchid Street",
                    "rating": 4.5,
                },
                {
                    "id": 2,
                    "name": "Swift Sushi",
                    "cuisine": "Japanese",
                    "address": "789 Daisy Road",
                    "rating": 4.2,
                },
            ]
        ),
        encoding="utf-8",
    )

    # Tell the application to use the temporary data directory
    app.dependency_overrides[get_settings] = lambda: Settings(data_dir=tmp_path)

    try:
        client = TestClient(app)

        response = client.get("/restaurants")

        assert response.status_code == 200
        assert [r["name"] for r in response.json()] == [
            "Pretty Pizza",
            "Swift Sushi",
        ]
    finally:
        app.dependency_overrides.clear()

