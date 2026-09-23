import json

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.models.restaurant import Restaurant


class RestaurantRepository:
    """Reads restaurant records from JSON storage.

    Takes Settings rather than a hardcoded path so tests can point at a
    temporary data directory and leave the committed data untouched.
    """

    def __init__(self, settings: Settings):
        self._path = settings.restaurants_file

    def list_all(self) -> list[Restaurant]:
        with open(self._path, encoding="utf-8") as file:
            return [Restaurant(**row) for row in json.load(file)]

    def get(self, restaurant_id: int) -> Restaurant | None:
        return next((r for r in self.list_all() if r.id == restaurant_id), None)


def get_restaurant_repository(
    settings: Settings = Depends(get_settings),
) -> RestaurantRepository:
    return RestaurantRepository(settings)
