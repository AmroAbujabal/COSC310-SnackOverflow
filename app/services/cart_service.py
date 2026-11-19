from decimal import Decimal, ROUND_HALF_UP

from app.models.cart import Cart, CartAdd, CartLine, CartLineView, CartQuantityUpdate, CartView
from app.repositories.cart_repository import CartRepository
from app.repositories.customer_repository import CustomerRepository
from app.services.exceptions import BusinessRuleError, ForbiddenError, NotFoundError
from app.services.menu_services import MenuService


class CartService:
    def __init__(self, repo: CartRepository, customer_repo: CustomerRepository, menu_service: MenuService):
        self._repo = repo
        self._customers = customer_repo
        self._menus = menu_service

    def _check_customer(self, customer_id: int):
        customer = self._customers.get(customer_id)
        if customer is None:
            raise NotFoundError(f"Customer {customer_id} not found")
        if not customer.is_active:
            raise ForbiddenError("Inactive customers cannot use a cart")

    @staticmethod
    def _find_or_create(carts: list[Cart], customer_id: int) -> Cart:
        cart = next((c for c in carts if c.customer_id == customer_id), None)
        if cart is None:
            cart = Cart(id=max((c.id for c in carts), default=0) + 1, customer_id=customer_id)
            carts.append(cart)
        return cart

    def _view(self, cart: Cart) -> CartView:
        lines = []
        subtotal = Decimal("0.00")
        # Retain disabled lines for display/removal; mutations still use get_orderable_item.
        menu = self._menus.get_menu(
            cart.restaurant_id, include_unavailable=True,
        ) if cart.items else None
        for line in cart.items:
            item = next((i for i in menu.items if i.item_id == line.item_id), None)
            if item is None:
                raise NotFoundError(f"Menu item {line.item_id} no longer exists; remove it or clear the cart")
            price = Decimal(str(item.price)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            amount = price * line.quantity
            subtotal += amount
            lines.append(CartLineView(**line.model_dump(), name=item.name, unit_price=float(price),
                                      line_total=float(amount), orderable=item.available and item.active))
        return CartView(**{**cart.model_dump(), "items": lines}, subtotal=float(subtotal), total=float(subtotal))

    def get_or_create_active(self, customer_id: int) -> CartView:
        self._check_customer(customer_id)
        existing = self._repo.get_active(customer_id)
        if existing is not None:
            return self._view(existing)
        with self._repo.transaction() as carts:
            result = self._view(self._find_or_create(carts, customer_id))
        return result

    def add_item(self, customer_id: int, request: CartAdd) -> CartView:
        self._check_customer(customer_id)
        self._menus.get_orderable_item(request.restaurant_id, request.item_id)
        with self._repo.transaction() as carts:
            cart = self._find_or_create(carts, customer_id)
            if cart.restaurant_id not in (None, request.restaurant_id):
                raise BusinessRuleError("A cart can contain items from only one restaurant")
            line = next((i for i in cart.items if i.item_id == request.item_id), None)
            quantity = request.quantity + (line.quantity if line else 0)
            if quantity > 99:
                raise BusinessRuleError("Quantity cannot exceed 99 per item")
            if line:
                line.quantity = quantity
            else:
                cart.items.append(CartLine(item_id=request.item_id, quantity=quantity))
            cart.restaurant_id = request.restaurant_id
            result = self._view(cart)
        return result

    def update_quantity(self, customer_id: int, item_id: int, request: CartQuantityUpdate) -> CartView:
        self._check_customer(customer_id)
        with self._repo.transaction() as carts:
            cart = next((c for c in carts if c.customer_id == customer_id), None)
            line = next((i for i in cart.items if i.item_id == item_id), None) if cart else None
            if line is None:
                raise NotFoundError(f"Cart item {item_id} not found")
            self._menus.get_orderable_item(cart.restaurant_id, item_id)
            line.quantity = request.quantity
            result = self._view(cart)
        return result

    def remove_item(self, customer_id: int, item_id: int) -> None:
        self._check_customer(customer_id)
        with self._repo.transaction() as carts:
            cart = next((c for c in carts if c.customer_id == customer_id), None)
            if cart is None or not any(i.item_id == item_id for i in cart.items):
                raise NotFoundError(f"Cart item {item_id} not found")
            cart.items = [i for i in cart.items if i.item_id != item_id]
            if not cart.items:
                cart.restaurant_id = None

    def clear(self, customer_id: int) -> None:
        self._check_customer(customer_id)
        with self._repo.transaction() as carts:
            cart = self._find_or_create(carts, customer_id)
            cart.items = []
            cart.restaurant_id = None
