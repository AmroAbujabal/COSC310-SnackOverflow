from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import Settings, get_settings
from app.core.security import decode_access_token
from app.models.customer import Customer
from app.repositories.customer_repository import (
    CustomerRepository,
    get_customer_repository,
)
from app.services.exceptions import ForbiddenError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    customer_repo: CustomerRepository = Depends(get_customer_repository),
    settings: Settings = Depends(get_settings),
) -> Customer:
    customer_id = decode_access_token(token, settings)

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


def require_role(*allowed_roles: str) -> Callable:
    """Return a dependency that permits only the supplied customer roles."""
    if not allowed_roles:
        raise ValueError("At least one role must be specified")

    def role_checker(
        current_user: Customer = Depends(get_current_user),
    ) -> Customer:
        if current_user.role not in allowed_roles:
            raise ForbiddenError("You do not have permission to perform this action")
        return current_user

    return role_checker
