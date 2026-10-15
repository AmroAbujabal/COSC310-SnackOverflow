from pydantic import BaseModel

class MenuItem(BaseModel):
    item_id: int
    restaurant_id: int
    name: str
    price: float