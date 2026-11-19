from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import Settings, get_settings
from app.core.security import create_access_token
from app.models.customer_requests import CustomerPublic, CustomerRegister, TokenResponse
from app.repositories.customer_repository import (
    CustomerRepository,
    get_customer_repository,
)
from app.services.customer_services import CustomerService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=CustomerPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Register a customer account",
)
def register_customer(
    request: CustomerRegister,
    repo: CustomerRepository = Depends(get_customer_repository),
):
    return CustomerService(repo).register(request)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Sign in and receive an access token",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    repo: CustomerRepository = Depends(get_customer_repository),
    settings: Settings = Depends(get_settings),
):
    customer = CustomerService(repo).authenticate(
        form_data.username,
        form_data.password,
    )
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(
        access_token=create_access_token(customer.id, settings)
    )
