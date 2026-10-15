from pydantic import BaseModel, model_validator
from app.models.menu_item import MenuItem


class Menu(BaseModel):
    restaurant_id: int
    items: list[MenuItem]


    @model_validator(mode="after")
    def validate_items(self):
        for item in self.items:
            if item.restaurant_id != self.restaurant_id:
                raise ValueError(
                    "Menu item belongs to a different restaurant"
                )
        return self