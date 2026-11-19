from fastapi import Depends

from app.core.config import Settings, get_settings
from app.models.customer import Customer
from app.models.customer_requests import CustomerUpdate
from app.repositories.json_repository import JsonRepository
from app.services.exceptions import BusinessRuleError


class CustomerRepository(JsonRepository[Customer]):
    """Reads and writes customer records in JSON storage."""

    def __init__(self, settings: Settings):
        super().__init__(settings.customers_file, Customer)

    def get(self, customer_id: int) -> Customer | None:
        return next(
            (customer for customer in self.list_all() if customer.id == customer_id),
            None,
        )

    def get_by_email(self, email: str) -> Customer | None:
        normalized_email = email.strip().casefold()
        return next(
            (
                customer
                for customer in self.list_all()
                if customer.email.strip().casefold() == normalized_email
            ),
            None,
        )

    def create(self, customer: Customer) -> Customer:
        customers = self.list_all()
        if self.get_by_email(customer.email) is not None:
            raise BusinessRuleError("A customer with this email already exists")

        new_customer = customer.model_copy(
            update={"id": self._next_id([item.id for item in customers])}
        )
        customers.append(new_customer)
        self._save(customers)
        return new_customer

    def update(
        self,
        customer_id: int,
        request: CustomerUpdate,
    ) -> Customer | None:
        customers = self.list_all()
        for index, customer in enumerate(customers):
            if customer.id != customer_id:
                continue

            updated_data = customer.model_dump()
            changes = request.model_dump(exclude_unset=True)
            new_email = changes.get("email")
            if new_email and new_email.casefold() != customer.email.casefold():
                existing = self.get_by_email(new_email)
                if existing is not None and existing.id != customer_id:
                    raise BusinessRuleError(
                        "A customer with this email already exists"
                    )

            updated_data.update(changes)
            updated_customer = Customer(**updated_data)
            customers[index] = updated_customer
            self._save(customers)
            return updated_customer
        return None

    def deactivate(self, customer_id: int) -> Customer | None:
        customers = self.list_all()
        for index, customer in enumerate(customers):
            if customer.id == customer_id:
                updated_customer = customer.model_copy(
                    update={"is_active": False}
                )
                customers[index] = updated_customer
                self._save(customers)
                return updated_customer
        return None


def get_customer_repository(
    settings: Settings = Depends(get_settings),
) -> CustomerRepository:
    return CustomerRepository(settings)
