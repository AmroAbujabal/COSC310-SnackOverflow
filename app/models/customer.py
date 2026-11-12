
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr


class Customer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    name: str
    email: str
    password_hash: str
    address: str
    role: Literal["customer", "owner", "admin"] = "customer"
    is_active: bool = True
