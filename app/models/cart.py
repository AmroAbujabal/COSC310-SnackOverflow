from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

PositiveId = Annotated[int, Field(strict=True, gt=0)]
Quantity = Annotated[int, Field(strict=True, ge=1, le=99)]


class CartLine(BaseModel):
    model_config = ConfigDict(extra="forbid")
    item_id: PositiveId
    quantity: Quantity


class Cart(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: PositiveId
    customer_id: PositiveId
    restaurant_id: PositiveId | None = None
    items: list[CartLine] = Field(default_factory=list)

    @model_validator(mode="after")
    def valid_contents(self):
        if bool(self.items) != (self.restaurant_id is not None):
            raise ValueError("Only a nonempty cart has a restaurant")
        if len({line.item_id for line in self.items}) != len(self.items):
            raise ValueError("Cart item IDs must be unique")
        return self


class CartAdd(BaseModel):
    model_config = ConfigDict(extra="forbid")
    restaurant_id: PositiveId
    item_id: PositiveId
    quantity: Quantity


class CartQuantityUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    quantity: Quantity


class CartLineView(CartLine):
    name: str
    unit_price: float
    line_total: float
    orderable: bool


class CartView(Cart):
    items: list[CartLineView] = Field(default_factory=list)
    subtotal: float
    total: float
