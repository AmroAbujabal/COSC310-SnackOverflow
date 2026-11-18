from fastapi import APIRouter, Depends, Path, status

from app.dependencies.auth import get_current_user
from app.models.customer import Customer
from app.models.error import ErrorResponse
from app.models.order import Order
from app.repositories.menu_repository import MenuRepository, get_menu_repository
from app.repositories.order_repository import OrderRepository, get_order_repository
from app.repositories.restaurant_repository import RestaurantRepository, get_restaurant_repository
from app.routes.cart import get_cart_service
from app.services.cart_service import CartService
from app.services.checkout_service import CheckoutService
from app.services.menu_services import MenuService
from app.services.order_service import OrderService

router = APIRouter()


@router.get(
    "/orders",
    response_model=list[Order],
    summary="List my orders",
    description="Returns the orders placed by the logged-in customer.",
    responses={401: {"model": ErrorResponse}},
)
def my_orders(
    user: Customer = Depends(get_current_user),
    repo: OrderRepository = Depends(get_order_repository),
):
    return OrderService(repo).list_my_orders(user)


@router.get(
    "/orders/{order_id}",
    response_model=Order,
    summary="Get one order",
    description="Visible to the customer who placed it and to admins.",
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def get_order(
    order_id: int = Path(..., description="The order's id"),
    user: Customer = Depends(get_current_user),
    repo: OrderRepository = Depends(get_order_repository),
):
    return OrderService(repo).get_order(order_id, user)


def get_checkout_service(
    orders: OrderRepository = Depends(get_order_repository),
    carts: CartService = Depends(get_cart_service),
    menus: MenuRepository = Depends(get_menu_repository),
    restaurants: RestaurantRepository = Depends(get_restaurant_repository),
) -> CheckoutService:
    return CheckoutService(orders, carts, MenuService(menus, restaurants))


@router.post(
    "/checkout",
    response_model=Order,
    status_code=status.HTTP_201_CREATED,
    summary="Place an order from my cart",
    description=(
        "Re-checks every cart item against the current menu, saves an order at today's prices, "
        "then empties the cart. If any item fails the check, no order is saved and the cart is unchanged."
    ),
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse, "description": "Empty cart, or an item is unavailable or deactivated"},
    },
)
def checkout(
    user: Customer = Depends(get_current_user),
    service: CheckoutService = Depends(get_checkout_service),
):
    return service.checkout(user)
