class DomainError(Exception):
    """A business problem raised by a service. app/main.py turns it into an HTTP response."""


class NotFoundError(DomainError):
    """The requested thing does not exist (404)."""


class BusinessRuleError(DomainError):
    """The request is valid but breaks a rule given the current data (409)."""


class ForbiddenError(DomainError):
    """The user is known but is not allowed to do this (403)."""


class RestaurantNotFoundError(NotFoundError):
    """No restaurant has the requested id."""

    def __init__(self, restaurant_id: int):
        super().__init__(f"Restaurant {restaurant_id} not found")

class MenuNotFoundError(NotFoundError):
    """The restaurant exists but has no menu."""

    def __init__(self, restaurant_id: int):
        super().__init__(f"Menu for restaurant {restaurant_id} not found")

class MenuItemNotFoundError(NotFoundError):
    def __init__(self, restaurant_id: int, item_id: int):
        self.restaurant_id = restaurant_id
        self.item_id = item_id
        super().__init__(
            f"Menu item {item_id} not found "
            f"for restaurant {restaurant_id}"
        )
