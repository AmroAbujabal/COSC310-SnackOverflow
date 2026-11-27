from app.models.customer import Customer
from app.models.order import Order, OrderStatus
from app.repositories.order_repository import OrderRepository, order_lock
from app.services.exceptions import (
    InvalidOrderTransitionError,
    OrderForbiddenError,
    OrderNotFoundError,
)
from app.services.restaurant_services import RestaurantService

# The order lifecycle: each status and the statuses it may move to next.
# One step forward at a time; cancelling is only possible before preparation starts;
# delivered and cancelled are final.
ALLOWED_TRANSITIONS: dict[OrderStatus, frozenset[OrderStatus]] = {
    "placed": frozenset({"accepted", "cancelled"}),
    "accepted": frozenset({"preparing", "cancelled"}),
    "preparing": frozenset({"ready"}),
    "ready": frozenset({"out_for_delivery"}),
    "out_for_delivery": frozenset({"delivered"}),
    "delivered": frozenset(),
    "cancelled": frozenset(),
}


def check_transition(current: str, new: str) -> None:
    """Raise InvalidOrderTransitionError (409) unless an order may move from `current` to `new`."""
    if new not in ALLOWED_TRANSITIONS.get(current, frozenset()):
        raise InvalidOrderTransitionError(current, new)


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

    def update_status(
        self, order_id: int, new_status: OrderStatus, user: Customer, restaurants: RestaurantService
    ) -> Order:
        """Staff move an order on: the owner of the order's restaurant, or an admin."""
        order = self._repo.get(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        restaurants.ensure_owner_access(order.restaurant_id, user)
        return self.change_status(order_id, new_status)

    def cancel(self, order_id: int, user: Customer) -> Order:
        """The customer who placed the order, or an admin, cancels it.

        ALLOWED_TRANSITIONS only allows this while the order is placed or accepted.
        """
        self.get_order(order_id, user)  # 404 / 403
        return self.change_status(order_id, "cancelled")

    def change_status(self, order_id: int, new_status: OrderStatus) -> Order:
        """Move an order to `new_status` and save it. Every order status change goes through here.

        Usage from another service (e.g. delivery):

            from app.services.order_service import OrderService
            order = OrderService(order_repo).change_status(order_id, "out_for_delivery")

        Raises OrderNotFoundError (404) for an unknown id and InvalidOrderTransitionError (409)
        if ALLOWED_TRANSITIONS does not allow the move; nothing is saved in either case.
        It does not check who is asking: callers check roles and their own rules
        (e.g. a driver is assigned) first.
        """
        # Hold the lock from read to save, so two changes can't both pass the check
        # against the same old status, and a checkout can't overwrite the change.
        with order_lock:
            order = self._repo.get(order_id)
            if order is None:
                raise OrderNotFoundError(order_id)
            check_transition(order.status, new_status)
            changed = order.model_copy(update={"status": new_status})
            self._repo.save(changed)
            return changed
