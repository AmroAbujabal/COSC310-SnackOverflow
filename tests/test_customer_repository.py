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
