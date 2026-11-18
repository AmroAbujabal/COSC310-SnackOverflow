from datetime import datetime, timezone

from app.models.customer import Customer
from app.models.order import Order, OrderLine
from app.repositories.order_repository import OrderRepository
from app.services.exceptions import EmptyCartError
from app.services.pricing import line_total, money, order_total


class CheckoutService:
    """Turns a customer's active cart into a saved order.

    cart_service and menu_service follow the contract agreed with Al-Munther:
    get_active_cart(customer_id) -> Cart | None, close_cart(cart_id),
    get_orderable_item(restaurant_id, item_id) -> MenuItem (raises 404/409 itself).
    """

    def __init__(self, order_repo: OrderRepository, cart_service, menu_service):
        self._orders = order_repo
        self._carts = cart_service
        self._menu = menu_service

    def checkout(self, user: Customer) -> Order:
        # 1-5 only read, so a failure leaves nothing half-written.
        cart = self._carts.get_active_cart(user.id)
        if cart is None or not cart.lines:
            raise EmptyCartError()

        lines = [self._order_line(cart.restaurant_id, line) for line in cart.lines]
        order = Order(
            id=0,  # the repository assigns the real id
            customer_id=user.id,
            restaurant_id=cart.restaurant_id,
            lines=lines,
            total=order_total([line.line_total for line in lines]),
            created_at=datetime.now(timezone.utc),
        )

        # 6 save, then 7 close: if saving fails the cart is untouched and the customer can retry.
        saved = self._orders.create(order)
        self._carts.close_cart(cart.id)
        return saved

    def _order_line(self, restaurant_id: int, cart_line) -> OrderLine:
        # Re-check the item now and use its current price, not what it cost when added to the cart.
        item = self._menu.get_orderable_item(restaurant_id, cart_line.item_id)
        unit_price = money(item.price)
        return OrderLine(
            item_id=item.item_id,
            name=item.name,
            unit_price=unit_price,
            quantity=cart_line.quantity,
            line_total=line_total(unit_price, cart_line.quantity),
        )
