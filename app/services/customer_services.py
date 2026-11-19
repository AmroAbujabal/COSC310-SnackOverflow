from app.core.security import hash_password, verify_password
from app.models.customer import Customer
from app.models.customer_requests import CustomerRegister, CustomerUpdate
from app.repositories.customer_repository import CustomerRepository
from app.services.exceptions import CustomerNotFoundError


class CustomerService:
    def __init__(self, repo: CustomerRepository):
        self._repo = repo

    def register(self, request: CustomerRegister) -> Customer:
        customer = Customer(
            id=0,
            name=request.name,
            email=request.email,
            password_hash=hash_password(request.password),
            address=request.address,
        )
        return self._repo.create(customer)

    def get_customer(self, customer_id: int) -> Customer:
        customer = self._repo.get(customer_id)
        if customer is None:
            raise CustomerNotFoundError(customer_id)
        return customer

    def update_customer(
        self,
        customer_id: int,
        request: CustomerUpdate,
    ) -> Customer:
        customer = self._repo.update(customer_id, request)
        if customer is None:
            raise CustomerNotFoundError(customer_id)
        return customer

    def deactivate_customer(self, customer_id: int) -> Customer:
        customer = self._repo.deactivate(customer_id)
        if customer is None:
            raise CustomerNotFoundError(customer_id)
        return customer

    def authenticate(self, email: str, password: str) -> Customer | None:
        customer = self._repo.get_by_email(email)
        if (
            customer is None
            or not customer.is_active
            or not verify_password(password, customer.password_hash)
        ):
            return None
        return customer
