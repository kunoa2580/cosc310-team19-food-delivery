from pydantic import BaseModel

class MenuItemRead(BaseModel):
    item_id: int
    restaurant_id: int
    name: str
    description: str
    price: float
    availability: bool


class MenuItemCreate(BaseModel):
    name: str
    description: str
    price: float
    availability: bool = True


class MenuItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    availability: bool | None = None
