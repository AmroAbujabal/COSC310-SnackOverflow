from app.core.security import hash_password, verify_password
from app.models.customer import Customer
from app.models.customer_requests import CustomerRegister, CustomerUpdate
from app.repositories.customer_repository import CustomerRepository
from app.services.exceptions import CustomerNotFoundError


# Generate one valid Argon2 hash when the application starts.
# It is used to perform password verification when an email is unknown.
DUMMY_PASSWORD_HASH = hash_password(
    "snackoverflow-dummy-password-not-for-login"
)


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

    def authenticate(
        self,
        email: str,
        password: str,
    ) -> Customer | None:
        customer = self._repo.get_by_email(email)

        # Perform an Argon2 verification even if the email is unknown.
        if customer is None:
            verify_password(password, DUMMY_PASSWORD_HASH)
            return None

        # Verify the password before checking account activity.
        # This avoids skipping the expensive password verification
        # for inactive accounts.
        password_valid = verify_password(
            password,
            customer.password_hash,
        )

        if not password_valid or not customer.is_active:
            return None

        return customer
