from fastapi import APIRouter, Depends, Path, Response

from app.dependencies.auth import get_current_user
from app.models.cart import CartAdd, CartQuantityUpdate, CartView
from app.models.customer import Customer
from app.models.error import ErrorResponse
from app.repositories.cart_repository import CartRepository, get_cart_repository
from app.repositories.customer_repository import CustomerRepository, get_customer_repository
from app.repositories.menu_repository import MenuRepository, get_menu_repository
from app.repositories.restaurant_repository import RestaurantRepository, get_restaurant_repository
from app.services.cart_service import CartService
from app.services.menu_services import MenuService

router = APIRouter(prefix="/cart", tags=["Cart"], responses={
    401: {"model": ErrorResponse, "description": "Missing/invalid token or inactive customer"},
    403: {"model": ErrorResponse, "description": "Customer deactivated since authentication"},
    404: {"model": ErrorResponse, "description": "Customer, restaurant, menu or item not found"},
    409: {"model": ErrorResponse, "description": "Unavailable/deactivated item, mixed restaurants or excessive combined quantity"},
})


def get_cart_service(
    repo: CartRepository = Depends(get_cart_repository),
    customers: CustomerRepository = Depends(get_customer_repository),
    menus: MenuRepository = Depends(get_menu_repository),
    restaurants: RestaurantRepository = Depends(get_restaurant_repository),
) -> CartService:
    return CartService(repo, customers, MenuService(menus, restaurants))


@router.get("", response_model=CartView, summary="Get or create your active cart",
            description="One active cart per authenticated customer. Current menu prices determine totals; total equals subtotal. Existing unavailable items are marked orderable=false. Physically deleted catalog records return 404; remove the item or clear the cart.")
def get_cart(user: Customer = Depends(get_current_user), service: CartService = Depends(get_cart_service)):
    return service.get_or_create_active(user.id)


@router.post("/items", response_model=CartView, summary="Add an orderable menu item",
             description="Adds quantity to an existing line, or inserts a new line. Quantities must be integers 1–99, including the combined quantity. Prices and totals are supplied by the backend.")
def add_item(request: CartAdd, user: Customer = Depends(get_current_user), service: CartService = Depends(get_cart_service)):
    return service.add_item(user.id, request)


@router.patch("/items/{item_id}", response_model=CartView, summary="Replace a cart item's quantity")
def update_quantity(request: CartQuantityUpdate, item_id: int = Path(gt=0, description="Menu item ID already in your cart"),
                    user: Customer = Depends(get_current_user), service: CartService = Depends(get_cart_service)):
    return service.update_quantity(user.id, item_id, request)


@router.delete("/items/{item_id}", status_code=204, summary="Remove an item from your cart",
               description="Removal remains possible if the menu item has become unavailable, deactivated or deleted.")
def remove_item(item_id: int = Path(gt=0, description="Menu item ID to remove"),
                user: Customer = Depends(get_current_user), service: CartService = Depends(get_cart_service)):
    service.remove_item(user.id, item_id)
    return Response(status_code=204)


@router.delete("", status_code=204, summary="Clear your cart",
               description="Keeps the cart ID and releases the restaurant restriction. Does not create an order; checkout must save an order before clearing.")
def clear_cart(user: Customer = Depends(get_current_user), service: CartService = Depends(get_cart_service)):
    service.clear(user.id)
    return Response(status_code=204)
