import pytest
from pydantic import ValidationError
from app.models.menu import Menu
from app.models.menu_item import MenuItem


def test_rejects_item_from_different_restaurant():
    with pytest.raises(ValidationError):
        Menu(
            restaurant_id=1,
            items=[
                MenuItem(
                    item_id=1,
                    restaurant_id=2,
                    name="Wrong Restaurant Item",
                    price=10.99
                )
            ]
        )