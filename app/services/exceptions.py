class RestaurantNotFoundError(Exception):
    """No restaurant has the requested id. app/main.py maps this to a 404."""

    def __init__(self, restaurant_id: int):
        super().__init__(f"Restaurant {restaurant_id} not found")

class MenuItemNotFoundError(Exception):
    def __init__(self, restaurant_id: int, item_id: int):
        self.restaurant_id = restaurant_id
        self.item_id = item_id
        super().__init__(
            f"Menu item {item_id} not found "
            f"for restaurant {restaurant_id}"
        )
