
from argon2 import PasswordHasher
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)
from datetime import datetime, timedelta, timezone
import jwt
from app.core.config import Settings

password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a plain-text password using Argon2."""
    return password_hasher.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Verify a password against its stored Argon2 hash."""
    try:
        return password_hasher.verify(
            hashed_password,
            plain_password,
        )
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False

def create_access_token(
    customer_id: int,
    settings: Settings,
) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": str(customer_id),
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(
    token: str,
    settings: Settings,
) -> int | None:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )

        customer_id = payload.get("sub")

        if not isinstance(customer_id, str) or not customer_id.isdigit():
            return None

        return int(customer_id)

    except jwt.InvalidTokenError:
        return None
    