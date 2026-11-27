from fastapi import APIRouter, Depends, Path, status

from app.dependencies.auth import get_current_user, require_role
from app.models.customer import Customer
from app.models.error import ErrorResponse
from app.models.order import Order
from app.models.order_requests import OrderStatusUpdate
from app.repositories.menu_repository import MenuRepository, get_menu_repository
from app.repositories.order_repository import OrderRepository, get_order_repository
from app.repositories.restaurant_repository import RestaurantRepository, get_restaurant_repository
from app.routes.cart import get_cart_service
from app.services.cart_service import CartService
from app.services.checkout_service import CheckoutService
from app.services.menu_services import MenuService
from app.services.order_service import OrderService
from app.services.restaurant_services import RestaurantService

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


@router.get(
    "/restaurants/{restaurant_id}/orders",
    response_model=list[Order],
    summary="List a restaurant's orders",
    description="Every order placed at the restaurant, in any status. For the restaurant's owner or an admin.",
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def restaurant_orders(
    restaurant_id: int = Path(..., description="The restaurant's id"),
    user: Customer = Depends(require_role("owner", "admin")),
    orders: OrderRepository = Depends(get_order_repository),
    restaurants: RestaurantRepository = Depends(get_restaurant_repository),
):
    return OrderService(orders).list_restaurant_orders(restaurant_id, user, RestaurantService(restaurants))


@router.patch(
    "/orders/{order_id}/status",
    response_model=Order,
    summary="Move an order to its next status",
    description=(
        "For the owner of the order's restaurant, or an admin. Accepts accepted, preparing, ready "
        "or cancelled; out_for_delivery and delivered are set by the delivery flow. "
        "A move the order lifecycle does not allow is a 409."
    ),
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse, "description": "Not an allowed next status"},
    },
)
def update_order_status(
    body: OrderStatusUpdate,
    order_id: int = Path(..., description="The order's id"),
    user: Customer = Depends(require_role("owner", "admin")),
    orders: OrderRepository = Depends(get_order_repository),
    restaurants: RestaurantRepository = Depends(get_restaurant_repository),
):
    return OrderService(orders).update_status(order_id, body.status, user, RestaurantService(restaurants))


@router.post(
    "/orders/{order_id}/cancel",
    response_model=Order,
    summary="Cancel an order",
    description="For the customer who placed it, or an admin, while the order is placed or accepted.",
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse, "description": "Preparation has already started"},
    },
)
def cancel_order(
    order_id: int = Path(..., description="The order's id"),
    user: Customer = Depends(get_current_user),
    repo: OrderRepository = Depends(get_order_repository),
):
    return OrderService(repo).cancel(order_id, user)


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
