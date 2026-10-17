
import json

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.models.restaurant import Restaurant
from app.models.restaurant_requests import RestaurantCreate, RestaurantUpdate


class RestaurantRepository:
    """Reads and writes restaurant records in JSON storage."""

    def __init__(self, settings: Settings):
        self._path = settings.restaurants_file

    def _save(self, restaurants: list[Restaurant]) -> None:
        self._path.write_text(
            json.dumps(
                [restaurant.model_dump() for restaurant in restaurants],
                indent=2,
            ) + "\n",
            encoding="utf-8",
        )

    def list_all(self) -> list[Restaurant]:
        with open(self._path, encoding="utf-8") as file:
            return [Restaurant(**row) for row in json.load(file)]

    def get(self, restaurant_id: int) -> Restaurant | None:
        return next(
            (r for r in self.list_all() if r.id == restaurant_id),
            None,
        )

    def create(self, request: RestaurantCreate) -> Restaurant:
        restaurants = self.list_all()
        next_id = max((r.id for r in restaurants), default=0) + 1

        restaurant = Restaurant(
            id=next_id,
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
                updated_data.update(
                    request.model_dump(exclude_unset=True)
                )

                updated_restaurant = Restaurant(**updated_data)
                restaurants[index] = updated_restaurant
                self._save(restaurants)
                return updated_restaurant

        return None


def get_restaurant_repository(
    settings: Settings = Depends(get_settings),
) -> RestaurantRepository:
    return RestaurantRepository(settings)
