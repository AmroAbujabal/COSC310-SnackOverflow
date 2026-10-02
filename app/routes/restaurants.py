from fastapi import APIRouter, Depends, Path

from app.models.error import ErrorResponse
from app.models.restaurant import Restaurant
from app.repositories.restaurant_repository import (
    RestaurantRepository,
    get_restaurant_repository,
)
from app.services.restaurant_services import RestaurantService


router = APIRouter()


@router.get(
    "/restaurants",
    response_model=list[Restaurant],
    summary="List restaurants",
    description="Returns every restaurant in the data store.",
)
def restaurants(
    repo: RestaurantRepository = Depends(get_restaurant_repository)
):
    service = RestaurantService(repo)
    return service.list_restaurants()


@router.get(
    "/restaurants/{restaurant_id}",
    response_model=Restaurant,
    summary="Get a restaurant",
    description="Returns the details of one restaurant. Responds with 404 if no restaurant has that id.",
    responses={404: {"model": ErrorResponse, "description": "Restaurant not found"}},
)
def restaurant_details(
    restaurant_id: int = Path(description="The restaurant's id"),
    repo: RestaurantRepository = Depends(get_restaurant_repository),
):
    service = RestaurantService(repo)
    return service.get_restaurant(restaurant_id)
