from app.models.customer import Customer
from app.models.restaurant import Restaurant
from app.models.restaurant_requests import RestaurantCreate, RestaurantUpdate
from app.repositories.restaurant_repository import RestaurantRepository
from app.services.exceptions import (
    ForbiddenError,
    RestaurantNotFoundError,
)


class RestaurantService:
    def __init__(self, repo: RestaurantRepository):
        self._repo = repo

    def list_restaurants(
        self,
        name: str | None = None,
        cuisine: str | None = None,
    ) -> list[Restaurant]:
        name = (name or "").strip().casefold()
        cuisine = (cuisine or "").strip().casefold()

        restaurants = self._repo.list_all()

        if name:
            restaurants = [
                r for r in restaurants
                if name in r.name.casefold()
            ]

        if cuisine:
            restaurants = [
                r for r in restaurants
                if r.cuisine.casefold() == cuisine
            ]

        return restaurants

    def get_restaurant(self, restaurant_id: int) -> Restaurant:
        restaurant = self._repo.get(restaurant_id)

        if restaurant is None:
            raise RestaurantNotFoundError(restaurant_id)

        return restaurant

    def ensure_owner_access(
        self,
        restaurant_id: int,
        current_user: Customer,
    ) -> Restaurant:
        """Verify that the user owns the restaurant or is an admin."""
        restaurant = self.get_restaurant(restaurant_id)

        if current_user.role == "admin":
            return restaurant

        if restaurant.owner_id != current_user.id:
            raise ForbiddenError(
                "You do not have permission to manage this restaurant"
            )

        return restaurant

    def create_restaurant(
        self,
        request: RestaurantCreate,
        owner_id: int,
    ) -> Restaurant:
        return self._repo.create(request, owner_id)

    def update_restaurant(
        self,
        restaurant_id: int,
        request: RestaurantUpdate,
        current_user: Customer,
    ) -> Restaurant:
        self.ensure_owner_access(restaurant_id, current_user)

        restaurant = self._repo.update(restaurant_id, request)

        if restaurant is None:
            raise RestaurantNotFoundError(restaurant_id)

        return restaurant
