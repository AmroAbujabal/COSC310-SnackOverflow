from app.models.restaurant import Restaurant
from app.repositories.restaurant_repository import RestaurantRepository
from app.services.exceptions import RestaurantNotFoundError

class RestaurantService:
    def __init__(self, repo: RestaurantRepository):
        self._repo = repo

    def list_restaurants(self):
        return self._repo.list_all()

    def get_restaurant(self, restaurant_id: int) -> Restaurant:
        restaurant = self._repo.get(restaurant_id)
        if restaurant is None:
            raise RestaurantNotFoundError(restaurant_id)
        return restaurant
