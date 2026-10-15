from pydantic import BaseModel
from app.models.menu_item import MenuItem

class Menu(BaseModel):
    restaurant_id: int
    items: list[MenuItem]