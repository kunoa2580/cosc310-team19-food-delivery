from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

NonBlank = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class RestaurantCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: NonBlank = Field(description="Restaurant name; must not be blank.")
    address: NonBlank = Field(description="Restaurant street address.")
    phone_number: NonBlank = Field(description="Restaurant contact phone number.")
    email: NonBlank = Field(description="Contact email; syntax checked, not deliverability.")
    website: str = Field(description="Restaurant HTTP or HTTPS website.")
    cuisine_type: NonBlank = Field(description="Cuisine used for exact-match filtering.")
    opening_hours: NonBlank = Field(description="Human-readable opening hours.")
    rating: float = Field(ge=0, le=5, allow_inf_nan=False, description="Rating from 0 to 5.")
    availability: bool = Field(default=True, description="Whether the restaurant is available.")



class RestaurantRead(RestaurantCreate):
    id: int = Field(gt=0, description="Server-assigned restaurant identifier.")


class RestaurantUpdate(BaseModel):
    """Omitted and explicit null fields leave existing values unchanged."""

    model_config = ConfigDict(str_strip_whitespace=True)
    #configures Pydantic to remove whitespace from the beginning and end of string values during validation

    name: NonBlank | None = None
    address: NonBlank | None = None
    phone_number: NonBlank | None = None
    email: NonBlank | None = None
    website: str | None = None
    cuisine_type: NonBlank | None = None
    opening_hours: NonBlank | None = None
    rating: float | None = Field(default=None, ge=0, le=5, allow_inf_nan=False)
    availability: bool | None = None

