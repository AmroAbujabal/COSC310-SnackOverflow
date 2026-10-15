from fastapi import APIRouter, Depends, HTTPException

from app.models.menu import Menu
from app.models.menu_item import MenuItem

from app.repositories.menu_repository import (
    MenuRepository,
    get_menu_repository,
)
from app.repositories.restaurant_repository import (
    RestaurantRepository,
    get_restaurant_repository,
)
from app.services.menu_services import MenuService


router = APIRouter()


@router.get(
    "/restaurants/{restaurant_id}/menu",
    response_model=Menu,
    responses={404: {"description": "Menu not found"}},
)
def get_menu(
    restaurant_id: int,
    repo: MenuRepository = Depends(get_menu_repository),
    restaurant_repo: RestaurantRepository = Depends(get_restaurant_repository),
):
    service = MenuService(repo, restaurant_repo)
    menu = service.get_menu(restaurant_id)

    if menu is None:
        raise HTTPException(
            status_code=404,
            detail=f"Menu for restaurant {restaurant_id} not found"
        )

    return menu


@router.get(
    "/restaurants/{restaurant_id}/menu/items",
    response_model=list[MenuItem],
    responses={404: {"description": "Menu not found"}},
)
def get_menu_items(
    restaurant_id: int,
    repo: MenuRepository = Depends(get_menu_repository),
    restaurant_repo: RestaurantRepository = Depends(get_restaurant_repository),
):
    service = MenuService(repo, restaurant_repo)
    menu = service.get_menu(restaurant_id)

    if menu is None:
        raise HTTPException(
            status_code=404,
            detail=f"Menu for restaurant {restaurant_id} not found"
        )

    return menu.items