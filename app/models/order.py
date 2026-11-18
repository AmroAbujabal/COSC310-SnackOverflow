from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.core.pricing import line_total, order_total


class OrderLine(BaseModel):
    item_id: int
    # Snapshots: what the customer paid, even if the menu changes later.
    name: str
    unit_price: float = Field(ge=0)
    quantity: int = Field(gt=0)
    line_total: float

    @model_validator(mode="after")
    def check_line_total(self):
        if self.line_total != line_total(self.unit_price, self.quantity):
            raise ValueError("line_total must equal unit_price * quantity")
        return self


class Order(BaseModel):
    id: int
    customer_id: int
    restaurant_id: int
    lines: list[OrderLine] = Field(min_length=1)
    total: float
    status: Literal["placed"] = "placed"
    created_at: datetime

    @model_validator(mode="after")
    def check_total(self):
        if self.total != order_total([line.line_total for line in self.lines]):
            raise ValueError("total must equal the sum of line totals")
        return self
