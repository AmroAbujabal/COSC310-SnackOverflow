import logging
from datetime import datetime, timezone

from app.models.customer import Customer
from app.models.order import Order, OrderLine
from app.repositories.cart_repository import cart_lock
from app.repositories.order_repository import OrderRepository
from app.services.cart_service import CartService
from app.services.exceptions import EmptyCartError
from app.services.menu_services import MenuService
from app.services.restaurant_services import RestaurantService
from app.core.pricing import line_total, money, order_total

logger = logging.getLogger(__name__)


class CheckoutService:
    """Turns a customer's active cart into a saved order.

    Uses Al-Munther's CartService (one cart per customer, emptied after checkout)
    and MenuService.get_orderable_item, which raises its own 404/409.
    """

    def __init__(
        self,
        order_repo: OrderRepository,
        cart_service: CartService,
        menu_service: MenuService,
        restaurant_service: RestaurantService,
    ):
        self._orders = order_repo
        self._carts = cart_service
        self._menu = menu_service
        self._restaurants = restaurant_service

    def checkout(self, user: Customer) -> Order:
        # Hold the cart lock for the whole checkout: a double-click can't turn one cart into two orders,
        # and an item added mid-checkout waits for the next order instead of being cleared with this one.
        # This serialises every cart action across customers; fine at our scale, use per-customer locks if not.
        with cart_lock:
            return self._checkout(user)

    def _checkout(self, user: Customer) -> Order:
        # Nothing is ordered or cleared before create(), so a failed check leaves the cart's items as they
        # were (get_or_create_active may create an empty cart, which changes nothing the customer sees).
        # Also 403s a customer deactivated since their token was issued.
        cart = self._carts.get_or_create_active(user.id)
        if not cart.items:
            raise EmptyCartError()

        lines = [self._order_line(cart.restaurant_id, line) for line in cart.items]
        restaurant = self._restaurants.get_restaurant(cart.restaurant_id)
        order = Order(
            id=0,  # the repository assigns the real id
            customer_id=user.id,
            restaurant_id=cart.restaurant_id,
            restaurant_name=restaurant.name,
            # get_current_user reloads the customer each request, so this is today's address.
            delivery_address=user.address,
            lines=lines,
            total=order_total([line.line_total for line in lines]),
            created_at=datetime.now(timezone.utc),
        )

        # Save first, then empty the cart: if saving fails the cart is untouched and the customer can retry.
        saved = self._orders.create(order)
        try:
            self._carts.clear(user.id)
        except Exception:
            # Undo the order, or the customer's retry would order the same cart twice.
            # ponytail: not a real transaction. If the delete fails too, the duplicate risk is back; and for
            # those few ms a reader can see the order, whose id the next order then reuses. A DB closes both.
            try:
                self._orders.delete(saved.id)
            except Exception:
                logger.exception("Could not undo order %s after emptying the cart failed", saved.id)
            raise
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
