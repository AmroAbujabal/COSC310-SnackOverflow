from datetime import datetime, timezone

from app.models.customer import Customer
from app.models.order import Order, OrderLine
from app.repositories.order_repository import OrderRepository
from app.services.cart_service import CartService
from app.services.exceptions import EmptyCartError
from app.services.menu_services import MenuService
from app.services.pricing import line_total, money, order_total


class CheckoutService:
    """Turns a customer's active cart into a saved order.

    Uses Al-Munther's CartService (one cart per customer, emptied after checkout)
    and MenuService.get_orderable_item, which raises its own 404/409.
    """

    def __init__(self, order_repo: OrderRepository, cart_service: CartService, menu_service: MenuService):
        self._orders = order_repo
        self._carts = cart_service
        self._menu = menu_service

    def checkout(self, user: Customer) -> Order:
        # 1-5 only read, so a failure leaves nothing half-written.
        # Also 403s a customer deactivated since their token was issued.
        cart = self._carts.get_or_create_active(user.id)
        if not cart.items:
            raise EmptyCartError()

        lines = [self._order_line(cart.restaurant_id, line) for line in cart.items]
        order = Order(
            id=0,  # the repository assigns the real id
            customer_id=user.id,
            restaurant_id=cart.restaurant_id,
            lines=lines,
            total=order_total([line.line_total for line in lines]),
            created_at=datetime.now(timezone.utc),
        )

        # 6 save, then 7 empty the cart: if saving fails the cart is untouched and the customer can retry.
        saved = self._orders.create(order)
        self._carts.clear(user.id)
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
