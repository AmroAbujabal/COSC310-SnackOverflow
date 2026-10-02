import pytest

ALL = ["Pretty Pizza", "Swift Sushi"]


@pytest.mark.parametrize(
    "query, expected",
    [
        ("", ALL),
        ("?name=sushi", ["Swift Sushi"]),
        ("?name=SWI", ["Swift Sushi"]),
        ("?cuisine=japanese", ["Swift Sushi"]),
        ("?cuisine=Jap", []),
        ("?name=i&cuisine=Japanese", ["Swift Sushi"]),
        ("?name=sushi&cuisine=Italian", []),
        ("?name=burger", []),
        ("?name=%20%20", ALL),
    ],
    ids=[
        "no filters",
        "name match",
        "name ignores case and matches part",
        "cuisine ignores case",
        "cuisine needs exact match",
        "filters combine",
        "combined with no match",
        "no match",
        "blank name ignored",
    ],
)
def test_search_and_filter(client, query, expected):
    response = client.get(f"/restaurants{query}")
    assert response.status_code == 200
    assert [r["name"] for r in response.json()] == expected


def test_docs_list_the_search_params(client):
    params = client.get("/openapi.json").json()["paths"]["/restaurants"]["get"]["parameters"]
    assert {p["name"] for p in params} == {"name", "cuisine"}
