from app.repositories.menu_repository import MenuRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.models.menu import Menu


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