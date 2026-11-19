from fastapi import Depends

from app.core.config import Settings, get_settings
from app.models.menu import Menu
from app.models.menu_item import MenuItem
from app.models.menu_item_requests import MenuItemCreate, MenuItemUpdate
from app.repositories.json_repository import JsonRepository


class MenuRepository(JsonRepository[Menu]):
    """Reads and writes menu records in JSON storage."""

    def __init__(self, settings: Settings):
        super().__init__(settings.menus_file, Menu)

    def get(self, restaurant_id: int) -> Menu | None:
        return next(
            (menu for menu in self.list_all() if menu.restaurant_id == restaurant_id),
            None,
        )

    def add_item(
        self,
        restaurant_id: int,
        request: MenuItemCreate,
    ) -> MenuItem:
        menus = self.list_all()
        existing_ids = [
            item.item_id for menu in menus for item in menu.items
        ]
        item = MenuItem(
            item_id=self._next_id(existing_ids),
            restaurant_id=restaurant_id,
            **request.model_dump(),
        )

        menu = next(
            (menu for menu in menus if menu.restaurant_id == restaurant_id),
            None,
        )
        if menu is None:
            menu = Menu(restaurant_id=restaurant_id, items=[])
            menus.append(menu)

        menu.items.append(item)
        self._save(menus)
        return item

    def update_item(
        self,
        restaurant_id: int,
        item_id: int,
        request: MenuItemUpdate,
    ) -> MenuItem | None:
        menus = self.list_all()
        for menu in menus:
            if menu.restaurant_id != restaurant_id:
                continue
            for index, item in enumerate(menu.items):
                if item.item_id == item_id:
                    updated_data = item.model_dump()
                    updated_data.update(request.model_dump(exclude_unset=True))
                    updated_item = MenuItem(**updated_data)
                    menu.items[index] = updated_item
                    self._save(menus)
                    return updated_item
        return None


def get_menu_repository(
    settings: Settings = Depends(get_settings),
) -> MenuRepository:
    return MenuRepository(settings)
