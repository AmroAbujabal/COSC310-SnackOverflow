
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
from app.models.error import ErrorResponse

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
    status_code=201,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Restaurant not found",
        }
    },
)
def add_menu_item(
    restaurant_id: int,
    request: MenuItemCreate,
    repo: MenuRepository = Depends(get_menu_repository),
    restaurant_repo: RestaurantRepository = Depends(
        get_restaurant_repository
    ),
):
    service = build_service(repo, restaurant_repo)
    return service.add_menu_item(restaurant_id, request)


@router.patch(
    "/restaurants/{restaurant_id}/menu/items/{item_id}",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Restaurant or menu item not found",
        }
    },
)
def update_menu_item(
    restaurant_id: int,
    item_id: int,
    request: MenuItemUpdate,
    repo: MenuRepository = Depends(get_menu_repository),
    restaurant_repo: RestaurantRepository = Depends(
        get_restaurant_repository
    ),
):
    service = build_service(repo, restaurant_repo)
    return service.update_menu_item(
        restaurant_id,
        item_id,
        request,
    )
