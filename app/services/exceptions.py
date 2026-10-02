class RestaurantNotFoundError(Exception):
    """No restaurant has the requested id. app/main.py maps this to a 404."""

    def __init__(self, restaurant_id: int):
        super().__init__(f"Restaurant {restaurant_id} not found")
