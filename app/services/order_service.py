from app.models.customer import Customer
from app.models.order import Order
from app.repositories.order_repository import OrderRepository
from app.services.exceptions import OrderForbiddenError, OrderNotFoundError


class OrderService:
    def __init__(self, repo: OrderRepository):
        self._repo = repo

    def get_order(self, order_id: int, user: Customer) -> Order:
        order = self._repo.get(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        # Team decision: an order is visible to the customer who placed it and to admins.
        if user.role != "admin" and order.customer_id != user.id:
            raise OrderForbiddenError(order_id)
        return order

    def list_my_orders(self, user: Customer) -> list[Order]:
        return self._repo.list_for_customer(user.id)
