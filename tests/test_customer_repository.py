from app.core.config import Settings
from app.models.customer import Customer
from app.repositories.customer_repository import CustomerRepository


def test_create_customer(tmp_path):
    (tmp_path / "customers.json").write_text("[]", encoding="utf-8")

    settings = Settings(data_dir=tmp_path)
    repo = CustomerRepository(settings)

    customer = Customer(
        id=0,
        name="Test Customer",
        email="test@example.com",
        password_hash="hashed-password",
        address="123 Test Street",
    )

    created = repo.create(customer)

    assert created.id == 1
    assert created.email == "test@example.com"


def test_get_by_email(tmp_path):
    (tmp_path / "customers.json").write_text("[]", encoding="utf-8")

    settings = Settings(data_dir=tmp_path)
    repo = CustomerRepository(settings)

    customer = Customer(
        id=0,
        name="Test Customer",
        email="test@example.com",
        password_hash="hashed-password",
        address="123 Test Street",
    )

    repo.create(customer)

    found = repo.get_by_email("TEST@example.com")

    assert found is not None
    assert found.email == "test@example.com"


def test_create_rejects_duplicate_email(tmp_path):
    from app.services.exceptions import BusinessRuleError
    import pytest

    (tmp_path / "customers.json").write_text("[]", encoding="utf-8")
    repo = CustomerRepository(Settings(data_dir=tmp_path))
    customer = Customer(
        id=0,
        name="Test Customer",
        email="test@example.com",
        password_hash="hashed-password",
        address="123 Test Street",
    )

    repo.create(customer)

    with pytest.raises(BusinessRuleError):
        repo.create(customer)


def test_update_customer_and_deactivate(tmp_path):
    from app.models.customer_requests import CustomerUpdate

    (tmp_path / "customers.json").write_text("[]", encoding="utf-8")
    repo = CustomerRepository(Settings(data_dir=tmp_path))

    created = repo.create(
        Customer(
            id=0,
            name="Test Customer",
            email="test@example.com",
            password_hash="hashed-password",
            address="123 Test Street",
        )
    )

    updated = repo.update(
        created.id,
        CustomerUpdate(name="Updated Customer", address="456 New Street"),
    )
    assert updated is not None
    assert updated.name == "Updated Customer"
    assert updated.address == "456 New Street"

    deactivated = repo.deactivate(created.id)
    assert deactivated is not None
    assert deactivated.is_active is False


def test_get_customer_by_id(tmp_path):
    (tmp_path / "customers.json").write_text("[]", encoding="utf-8")
    repo = CustomerRepository(Settings(data_dir=tmp_path))

    created = repo.create(
        Customer(
            id=0,
            name="Test Customer",
            email="test@example.com",
            password_hash="hashed-password",
            address="123 Test Street",
        )
    )

    assert repo.get(created.id) == created
    assert repo.get(999) is None
