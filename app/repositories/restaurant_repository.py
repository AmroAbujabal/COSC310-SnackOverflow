from fastapi import Depends

from app.core.config import Settings, get_settings
from app.models.restaurant import Restaurant
from app.models.restaurant_requests import RestaurantCreate, RestaurantUpdate
from app.repositories.json_repository import JsonRepository


class RestaurantRepository(JsonRepository[Restaurant]):
    """Reads and writes restaurant records in JSON storage."""

    def __init__(self, settings: Settings):
        super().__init__(settings.restaurants_file, Restaurant)

    def get(self, restaurant_id: int) -> Restaurant | None:
        return next(
            (restaurant for restaurant in self.list_all() if restaurant.id == restaurant_id),
            None,
        )

    def create(self, request: RestaurantCreate) -> Restaurant:
        restaurants = self.list_all()
        restaurant = Restaurant(
            id=self._next_id([item.id for item in restaurants]),
            **request.model_dump(),
        )
        restaurants.append(restaurant)
        self._save(restaurants)
        return restaurant

    def update(
        self,
        restaurant_id: int,
        request: RestaurantUpdate,
    ) -> Restaurant | None:
        restaurants = self.list_all()
        for index, restaurant in enumerate(restaurants):
            if restaurant.id == restaurant_id:
                updated_data = restaurant.model_dump()
                updated_data.update(request.model_dump(exclude_unset=True))
                updated_restaurant = Restaurant(**updated_data)
                restaurants[index] = updated_restaurant
                self._save(restaurants)
                return updated_restaurant
        return None


def get_restaurant_repository(
    settings: Settings = Depends(get_settings),
) -> RestaurantRepository:
    return RestaurantRepository(settings)
