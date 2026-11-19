
from fastapi import APIRouter, Depends, Path, Query, status


from app.dependencies.auth import require_role
from app.models.customer import Customer
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
from app.services.restaurant_services import RestaurantService

router = APIRouter()


def build_service(
    repo: MenuRepository,
    restaurant_repo: RestaurantRepository,
) -> MenuService:
    return MenuService(repo, restaurant_repo)


@router.get(
    "/restaurants/{restaurant_id}/menu",
    response_model=Menu,
    responses={404: {"model": ErrorResponse, "description": "Restaurant or menu not found"}},
)
def get_menu(
    restaurant_id: int,
    include_unavailable: bool = Query(
        default=False,
        description="Include unavailable and deactivated items for management; customer reads hide them by default.",
    ),
    repo: MenuRepository = Depends(get_menu_repository),
    restaurant_repo: RestaurantRepository = Depends(get_restaurant_repository),
):
    return build_service(repo, restaurant_repo).get_menu(
        restaurant_id, include_unavailable=include_unavailable,
    )


@router.get(
    "/restaurants/{restaurant_id}/menu/items",
    response_model=list[MenuItem],
    responses={404: {"model": ErrorResponse, "description": "Restaurant or menu not found"}},
)
def get_menu_items(
    restaurant_id: int,
    include_unavailable: bool = Query(
        default=False,
        description="Include unavailable and deactivated items for management; customer reads hide them by default.",
    ),
    repo: MenuRepository = Depends(get_menu_repository),
    restaurant_repo: RestaurantRepository = Depends(get_restaurant_repository),
):
    return build_service(repo, restaurant_repo).get_menu(
        restaurant_id, include_unavailable=include_unavailable,
    ).items


@router.post(
    "/restaurants/{restaurant_id}/menu/items",
    status_code=201,
    response_model=MenuItem,
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
    current_user: Customer = Depends(require_role("owner", "admin")),
):
    restaurant_service = RestaurantService(restaurant_repo)
    restaurant_service.ensure_owner_access(
        restaurant_id,
        current_user,
    )

    service = build_service(repo, restaurant_repo)
    return service.add_menu_item(restaurant_id, request)


@router.patch(
    "/restaurants/{restaurant_id}/menu/items/{item_id}",
    response_model=MenuItem,
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
    current_user: Customer = Depends(require_role("owner", "admin")),
):
    restaurant_service = RestaurantService(restaurant_repo)
    restaurant_service.ensure_owner_access(
        restaurant_id,
        current_user,
    )

    service = build_service(repo, restaurant_repo)

    return service.update_menu_item(
        restaurant_id,
        item_id,
        request,
    )
