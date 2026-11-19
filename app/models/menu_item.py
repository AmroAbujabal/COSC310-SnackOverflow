from pydantic import BaseModel, StrictBool

class MenuItem(BaseModel):
    item_id: int
    restaurant_id: int
    name: str
    price: float
    available: StrictBool = True
    active: StrictBool = True