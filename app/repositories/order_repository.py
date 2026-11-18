import json

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.models.order import Order


class OrderRepository:
    """Reads and writes order records in JSON storage."""

    def __init__(self, settings: Settings):
        self._path = settings.orders_file

    def _save(self, orders: list[Order]) -> None:
        # mode="json" turns created_at into an ISO string; plain json.dumps can't encode a datetime.
        self._path.write_text(
            json.dumps([order.model_dump(mode="json") for order in orders], indent=2) + "\n",
            encoding="utf-8",
        )

    def list_all(self) -> list[Order]:
        with open(self._path, encoding="utf-8") as file:
            return [Order(**row) for row in json.load(file)]

    def get(self, order_id: int) -> Order | None:
        return next((order for order in self.list_all() if order.id == order_id), None)

    def list_for_customer(self, customer_id: int) -> list[Order]:
        return [order for order in self.list_all() if order.customer_id == customer_id]

    def create(self, order: Order) -> Order:
        orders = self.list_all()
        next_id = max((existing.id for existing in orders), default=0) + 1
        new_order = order.model_copy(update={"id": next_id})
        orders.append(new_order)
        self._save(orders)
        return new_order


def get_order_repository(settings: Settings = Depends(get_settings)) -> OrderRepository:
    return OrderRepository(settings)
