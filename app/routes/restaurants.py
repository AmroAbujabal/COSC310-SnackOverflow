from fastapi import APIRouter, Depends

from app.models.restaurant import Restaurant
from app.repositories.restaurant_repository import (
    RestaurantRepository,
    get_restaurant_repository,
)
from app.services.restaurant_services import RestaurantService


router = APIRouter()


@router.get("/restaurants", response_model=list[Restaurant])
def restaurants(
    repo: RestaurantRepository = Depends(get_restaurant_repository)
):
    service = RestaurantService(repo)
    return service.list_restaurants()
