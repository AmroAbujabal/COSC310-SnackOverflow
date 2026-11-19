
from app.models.menu import Menu
from app.models.menu_item import MenuItem
from app.models.menu_item_requests import MenuItemCreate, MenuItemUpdate
from app.repositories.menu_repository import MenuRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.services.exceptions import (
    BusinessRuleError, RestaurantNotFoundError, MenuItemNotFoundError, MenuNotFoundError,
)

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

    def get_menu(self, restaurant_id: int, *, include_unavailable: bool = False) -> Menu:
        """Customer reads hide unavailable/inactive items; management can request all."""
        if self._restaurant_repo.get(restaurant_id) is None:
            raise RestaurantNotFoundError(restaurant_id)

        menu = self._repo.get(restaurant_id)
        # Restaurant exists, menu doesn't.
        if menu is None:
            raise MenuNotFoundError(restaurant_id)

        if include_unavailable:
            return menu
        return menu.model_copy(update={
            "items": [item for item in menu.items if item.available and item.active],
        })

    def get_orderable_item(self, restaurant_id: int, item_id: int) -> MenuItem:
        """Shared cart/checkout validation; always reloads current catalog state."""
        menu = self.get_menu(restaurant_id, include_unavailable=True)
        item = next((i for i in menu.items if i.item_id == item_id), None)
        if item is None:
            raise MenuItemNotFoundError(restaurant_id, item_id)
        if not item.active or not item.available:
            raise BusinessRuleError(f"Menu item {item_id} is unavailable or deactivated")
        return item

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

