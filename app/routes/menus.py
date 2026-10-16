
from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.models.menu import Menu
from app.models.menu_item import MenuItem
from app.models.menu_item_requests import MenuItemCreate, MenuItemUpdate
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


def build_service(
    repo: MenuRepository,
    restaurant_repo: RestaurantRepository,
) -> MenuService:
    return MenuService(repo, restaurant_repo)


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
    menu = build_service(repo, restaurant_repo).get_menu(restaurant_id)

    if menu is None:
        raise HTTPException(
            status_code=404,
            detail=f"Menu for restaurant {restaurant_id} not found",
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
    menu = build_service(repo, restaurant_repo).get_menu(restaurant_id)

    if menu is None:
        raise HTTPException(
            status_code=404,
            detail=f"Menu for restaurant {restaurant_id} not found",
        )

    return menu.items


@router.post(
    "/restaurants/{restaurant_id}/menu/items",
    response_model=MenuItem,
    status_code=status.HTTP_201_CREATED,
    summary="Add an item to a restaurant's menu",
)
def add_menu_item(
    request: MenuItemCreate,
    restaurant_id: int = Path(description="The restaurant's id"),
    repo: MenuRepository = Depends(get_menu_repository),
    restaurant_repo: RestaurantRepository = Depends(get_restaurant_repository),
):
    item = build_service(repo, restaurant_repo).add_menu_item(
        restaurant_id,
        request,
    )

    if item is None:
        raise HTTPException(
            status_code=404,
            detail=f"Restaurant {restaurant_id} not found",
        )

    return item


@router.patch(
    "/restaurants/{restaurant_id}/menu/items/{item_id}",
    response_model=MenuItem,
    summary="Update a menu item",
)
def update_menu_item(
    request: MenuItemUpdate,
    restaurant_id: int = Path(description="The restaurant's id"),
    item_id: int = Path(description="The menu item's id"),
    repo: MenuRepository = Depends(get_menu_repository),
    restaurant_repo: RestaurantRepository = Depends(get_restaurant_repository),
):
    item = build_service(repo, restaurant_repo).update_menu_item(
        restaurant_id,
        item_id,
        request,
    )

    if item is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Menu item {item_id} not found "
                f"for restaurant {restaurant_id}"
            ),
        )

    return item
