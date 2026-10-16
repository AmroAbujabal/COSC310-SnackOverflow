from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_frontend_is_text_only_and_serves_its_script():
    page = client.get("/")
    script = client.get("/app.js")

    assert page.status_code == 200
    assert "SnackOverflow" in page.text
    assert "Search by name, cuisine, address, or rating" in page.text
    assert "stylesheet" not in page.text
    assert script.status_code == 200
    assert "loadRestaurants" in script.text
    assert "images.unsplash.com" not in script.text