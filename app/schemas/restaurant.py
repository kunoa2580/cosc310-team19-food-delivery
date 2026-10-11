from pydantic import BaseModel


class RestaurantRead(BaseModel):
    id: int
    name: str
    address: str
    phone_number: str
    email: str
    website: str
    cuisine_type: str
    opening_hours: str
    rating: float
    availability: bool

class RestaurantCreate(BaseModel):
    name: str
    address: str
    phone_number: str
    email: str
    website: str
    cuisine_type: str
    opening_hours: str
    rating: float
    availability: bool = True

class RestaurantUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    phone_number: str | None = None
    email: str | None = None
    website: str | None = None
    cuisine_type: str | None = None
    opening_hours: str | None = None
    rating: float | None = None
    availability: bool | None = None

