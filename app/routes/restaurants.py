from fastapi import APIRouter, Depends, Path, Query

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
    summary="List, search and filter restaurants",
    description=(
        "Returns every restaurant, optionally narrowed by a name search and a cuisine filter. "
        "Both filters can be combined. No match returns an empty list."
    ),
)
def restaurants(
    name: str | None = Query(None, description="Only restaurants whose name contains this text (case-insensitive)"),
    cuisine: str | None = Query(None, description="Only restaurants with exactly this cuisine (case-insensitive)"),
    repo: RestaurantRepository = Depends(get_restaurant_repository),
):
    service = RestaurantService(repo)
    return service.list_restaurants(name=name, cuisine=cuisine)


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
