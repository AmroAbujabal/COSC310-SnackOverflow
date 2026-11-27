from typing import Literal

from pydantic import BaseModel, ConfigDict


class OrderStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Only the statuses restaurant staff set. out_for_delivery and delivered come from the
    # delivery flow, so it can keep delivery and order state consistent (driver assigned first).
    status: Literal["accepted", "preparing", "ready", "cancelled"]
