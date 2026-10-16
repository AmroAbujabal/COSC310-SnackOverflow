
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class RestaurantCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1)
    cuisine: str = Field(min_length=1)
    address: str = Field(min_length=1)
    rating: float = Field(ge=0, le=5)

    @field_validator("name", "cuisine", "address")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank")
        return value


class RestaurantUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1)
    cuisine: str | None = Field(default=None, min_length=1)
    address: str | None = Field(default=None, min_length=1)
    rating: float | None = Field(default=None, ge=0, le=5)

    @field_validator("name", "cuisine", "address")
    @classmethod
    def strip_required_text(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("This field cannot be null")
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank")
        return value

    
    @model_validator(mode="after")
    def validate_update_fields(self):
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update")

        for field in self.model_fields_set:
            if getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")

        return self

