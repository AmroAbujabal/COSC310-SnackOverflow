from fastapi import APIRouter, Depends, Path

from app.dependencies.auth import get_current_user
from app.models.customer import Customer
from app.models.error import ErrorResponse
from app.models.order import Order
from app.repositories.order_repository import OrderRepository, get_order_repository
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
