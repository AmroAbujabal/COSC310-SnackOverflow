from app.models.restaurant import Restaurant
from app.repositories.restaurant_repository import RestaurantRepository
from app.services.exceptions import RestaurantNotFoundError

class RestaurantService:
    def __init__(self, repo: RestaurantRepository):
        self._repo = repo

    def list_restaurants(self, name: str | None = None, cuisine: str | None = None) -> list[Restaurant]:
        # Blank or missing filters are ignored. Name matches any part of the name,
        # cuisine must match exactly; both ignore case.
        name = (name or "").strip().casefold()
        cuisine = (cuisine or "").strip().casefold()
        restaurants = self._repo.list_all()
        if name:
            restaurants = [r for r in restaurants if name in r.name.casefold()]
        if cuisine:
            restaurants = [r for r in restaurants if r.cuisine.casefold() == cuisine]
        return restaurants

    def get_restaurant(self, restaurant_id: int) -> Restaurant:
        restaurant = self._repo.get(restaurant_id)
        if restaurant is None:
            raise RestaurantNotFoundError(restaurant_id)
        return restaurant
