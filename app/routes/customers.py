from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user, require_role
from app.models.customer import Customer
from app.models.customer_requests import CustomerPublic, CustomerUpdate
from app.repositories.customer_repository import (
    CustomerRepository,
    get_customer_repository,
)
from app.services.customer_services import CustomerService
from app.services.exceptions import ForbiddenError

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("/me", response_model=CustomerPublic, summary="Get the signed-in customer")
def get_my_profile(current_user: Customer = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=CustomerPublic, summary="Update the signed-in customer's profile")
def update_my_profile(
    request: CustomerUpdate,
    current_user: Customer = Depends(get_current_user),
    repo: CustomerRepository = Depends(get_customer_repository),
):
    return CustomerService(repo).update_customer(current_user.id, request)


@router.delete(
    "/me",
    response_model=CustomerPublic,
    summary="Deactivate the signed-in customer's account",
)
def deactivate_my_account(
    current_user: Customer = Depends(get_current_user),
    repo: CustomerRepository = Depends(get_customer_repository),
):
    return CustomerService(repo).deactivate_customer(current_user.id)


@router.get("/{customer_id}", response_model=CustomerPublic, summary="Get a customer")
def get_customer(
    customer_id: int,
    current_user: Customer = Depends(get_current_user),
    repo: CustomerRepository = Depends(get_customer_repository),
):
    if current_user.id != customer_id and current_user.role != "admin":
        raise ForbiddenError("You can only view your own customer profile")
    return CustomerService(repo).get_customer(customer_id)


@router.patch("/{customer_id}", response_model=CustomerPublic, summary="Update a customer's profile")
def update_customer(
    customer_id: int,
    request: CustomerUpdate,
    current_user: Customer = Depends(get_current_user),
    repo: CustomerRepository = Depends(get_customer_repository),
):
    if current_user.id != customer_id and current_user.role != "admin":
        raise ForbiddenError("You can only update your own customer profile")
    return CustomerService(repo).update_customer(customer_id, request)


@router.delete(
    "/{customer_id}",
    response_model=CustomerPublic,
    summary="Deactivate a customer (admin only)",
)
def deactivate_customer(
    customer_id: int,
    _admin: Customer = Depends(require_role("admin")),
    repo: CustomerRepository = Depends(get_customer_repository),
):
    return CustomerService(repo).deactivate_customer(customer_id)
