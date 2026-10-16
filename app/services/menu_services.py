
from app.models.menu import Menu
from app.models.menu_item import MenuItem
from app.models.menu_item_requests import MenuItemCreate, MenuItemUpdate
from app.repositories.menu_repository import MenuRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.services.exceptions import (RestaurantNotFoundError, MenuItemNotFoundError,)

class MenuService:
    def __init__(
        self,
        repo: MenuRepository,
        restaurant_repo: RestaurantRepository,
    ):
        self._repo = repo
        self._restaurant_repo = restaurant_repo

    def list_menus(self) -> list[Menu]:
        return self._repo.list_all()

    def get_menu(self, restaurant_id: int) -> Menu | None:
        if self._restaurant_repo.get(restaurant_id) is None:
            return None

        return self._repo.get(restaurant_id)

    def add_menu_item(
        self,
        restaurant_id: int,
        request: MenuItemCreate,
    ) -> MenuItem | None:
        if self._restaurant_repo.get(restaurant_id) is None:
            raise RestaurantNotFoundError(restaurant_id)

        return self._repo.add_item(restaurant_id, request)

    def update_menu_item(
        self,
        restaurant_id: int,
        item_id: int,
        request: MenuItemUpdate,
    ) -> MenuItem:
        if self._restaurant_repo.get(restaurant_id) is None:
            raise RestaurantNotFoundError(restaurant_id)

        updated_item = self._repo.update_item(
            restaurant_id,
            item_id,
            request,
        )

        if updated_item is None:
            raise MenuItemNotFoundError(restaurant_id, item_id)

        return updated_item

