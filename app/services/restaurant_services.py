from app.repositories.restaurant_repository import RestaurantRepository

class RestaurantService:
    def __init__(self, repo: RestaurantRepository):
        self._repo = repo

    def list_restaurants(self):
        return self._repo.list_all()
