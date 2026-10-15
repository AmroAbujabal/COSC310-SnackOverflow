import json

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.models.menu import Menu

class MenuRepository:
    def __init__(self, settings: Settings):
        self._path = settings.menus_file

    def list_all(self) -> list[Menu]:
        with open(self._path, encoding="utf-8") as file:
             return [Menu(**row) for row in json.load(file)]


    def get(self, restaurant_id: int) -> Menu | None:
        return next((m for m in self.list_all() if m.restaurant_id == restaurant_id), None)

    


def get_menu_repository(
    settings: Settings = Depends(get_settings),
) -> MenuRepository:
    return MenuRepository(settings)