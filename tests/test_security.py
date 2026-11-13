
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import Settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)



def test_hash_password_does_not_return_plain_password():
    password = "mypassword123"

    hashed = hash_password(password)

    assert hashed != password


def test_verify_password_with_correct_password():
    password = "mypassword123"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_with_incorrect_password():
    hashed = hash_password("mypassword123")

    assert verify_password("wrongpassword", hashed) is False


def test_hashing_same_password_produces_different_hashes():
    password = "mypassword123"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash


def test_create_and_decode_access_token(tmp_path):
    settings = Settings(data_dir=tmp_path)

    token = create_access_token(1, settings)

    assert decode_access_token(token, settings) == 1


def test_decode_expired_token(tmp_path):
    settings = Settings(data_dir=tmp_path)

    expired_token = jwt.encode(
        {
            "sub": "1",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    assert decode_access_token(expired_token, settings) is None


def test_decode_tampered_token(tmp_path):
    settings = Settings(data_dir=tmp_path)

    token = create_access_token(1, settings)

    tampered_token = token[:-1] + (
        "A" if token[-1] != "A" else "B"
    )

    assert decode_access_token(tampered_token, settings) is None
