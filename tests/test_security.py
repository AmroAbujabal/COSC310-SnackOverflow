
from app.core.security import hash_password, verify_password


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
