from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_access_token
from app.models.customer import Customer
from app.repositories.customer_repository import (
    CustomerRepository,
    get_customer_repository,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    customer_repo: CustomerRepository = Depends(get_customer_repository),
) -> Customer:
    customer_id = decode_access_token(token)

    if customer_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    customer = customer_repo.get(customer_id)

    if customer is None or not customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Customer not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return customer
