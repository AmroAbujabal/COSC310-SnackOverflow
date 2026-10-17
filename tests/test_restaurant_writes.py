
import json


def test_create_restaurant(client, data_dir):
    response = client.post(
        "/restaurants",
        json={
            "name": "Noodle House",
            "cuisine": "Chinese",
            "address": "45 Main Street",
            "rating": 4.3,
        },
    )

    assert response.status_code == 201
    created = response.json()

    assert created == {
        "id": 3,
        "name": "Noodle House",
        "cuisine": "Chinese",
        "address": "45 Main Street",
        "rating": 4.3,
    }

    saved = json.loads(
        (data_dir / "restaurants.json").read_text(encoding="utf-8")
    )
    assert any(
        restaurant["id"] == 3
        and restaurant["name"] == "Noodle House"
        for restaurant in saved
    )


def test_create_restaurant_generates_distinct_ids(client):
    payload = {
        "name": "Noodle House",
        "cuisine": "Chinese",
        "address": "45 Main Street",
        "rating": 4.3,
    }

    first = client.post("/restaurants", json=payload)
    second = client.post(
        "/restaurants",
        json={**payload, "name": "Taco Place"},
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] != second.json()["id"]


def test_update_restaurant_preserves_unmodified_fields(client):
    response = client.patch(
        "/restaurants/1",
        json={"rating": 4.8},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Pretty Pizza",
        "cuisine": "Italian",
        "address": "294 Orchid Street",
        "rating": 4.8,
    }


def test_update_restaurant_not_found(client):
    response = client.patch(
        "/restaurants/999",
        json={"rating": 4.8},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Restaurant 999 not found"
    }


def test_create_restaurant_rejects_invalid_rating(client):
    response = client.post(
        "/restaurants",
        json={
            "name": "Noodle House",
            "cuisine": "Chinese",
            "address": "45 Main Street",
            "rating": 6.0,
        },
    )

    assert response.status_code == 422


def test_create_restaurant_rejects_blank_name(client):
    response = client.post(
        "/restaurants",
        json={
            "name": "   ",
            "cuisine": "Chinese",
            "address": "45 Main Street",
            "rating": 4.3,
        },
    )

    assert response.status_code == 422


def test_update_restaurant_rejects_empty_body(client):
    response = client.patch(
        "/restaurants/1",
        json={},
    )

    assert response.status_code == 422


def test_update_restaurant_rejects_null_rating(client):
    response = client.patch(
        "/restaurants/1",
        json={"rating": None},
    )

    assert response.status_code == 422
