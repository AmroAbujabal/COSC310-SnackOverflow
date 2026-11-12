
import json

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.models.customer import Customer


class CustomerRepository:
    """Reads and writes customer records in JSON storage."""

    def __init__(self, settings: Settings):
        self._path = settings.customers_file

    def _save(self, customers: list[Customer]) -> None:
        self._path.write_text(
            json.dumps(
                [customer.model_dump() for customer in customers],
                indent=2,
            ) + "\n",
            encoding="utf-8",
        )

    def list_all(self) -> list[Customer]:
        with open(self._path, encoding="utf-8") as file:
            return [
                Customer(**row)
                for row in json.load(file)
            ]

    def get(self, customer_id: int) -> Customer | None:
        return next(
            (
                customer
                for customer in self.list_all()
                if customer.id == customer_id
            ),
            None,
        )

    def get_by_email(self, email: str) -> Customer | None:
        normalized_email = email.strip().casefold()

        return next(
            (
                customer
                for customer in self.list_all()
                if customer.email.strip().casefold()
                == normalized_email
            ),
            None,
        )

    def create(self, customer: Customer) -> Customer:
        customers = self.list_all()

        next_id = max(
            (customer.id for customer in customers),
            default=0,
        ) + 1

        new_customer = customer.model_copy(
            update={"id": next_id}
        )

        customers.append(new_customer)
        self._save(customers)

        return new_customer


def get_customer_repository(
    settings: Settings = Depends(get_settings),
) -> CustomerRepository:
    return CustomerRepository(settings)
