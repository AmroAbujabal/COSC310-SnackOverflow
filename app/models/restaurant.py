from pydantic import BaseModel


class Restaurant(BaseModel):
    id: int
    name: str
    address: str
