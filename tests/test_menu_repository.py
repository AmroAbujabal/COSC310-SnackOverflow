import json
import pytest

from app.core.config import Settings
from app.repositories.menu_repository import MenuRepository


@pytest.fixture
def menu_repo(tmp_path):
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
        },
        {
            "restaurant_id": 2,
            "items": []
        }
    ]

    (tmp_path / "menus.json").write_text(
        json.dumps(menus), encoding="utf-8"
    )

    return MenuRepository(Settings(data_dir=tmp_path))


def test_list_all_reads_menus(menu_repo):
    menus = menu_repo.list_all()

    assert len(menus) == 2
    assert menus[0].restaurant_id == 1
    assert len(menus[0].items) == 2
    assert menus[0].items[0].name == "Butter Chicken"


def test_get_existing_menu(menu_repo):
    menu = menu_repo.get(1)

    assert menu is not None
    assert menu.restaurant_id == 1
    assert menu.items[0].price == 15.99


def test_get_nonexistent_menu(menu_repo):
    menu = menu_repo.get(999)

    assert menu is None


def test_missing_file(tmp_path):
    repo = MenuRepository(Settings(data_dir=tmp_path))

    with pytest.raises(FileNotFoundError):
        repo.list_all()


def test_invalid_json(tmp_path):
    (tmp_path / "menus.json").write_text(
        "{invalid json}", encoding="utf-8"
    )

    repo = MenuRepository(Settings(data_dir=tmp_path))

    with pytest.raises(json.JSONDecodeError):
        repo.list_all()