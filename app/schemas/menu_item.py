from pydantic import BaseModel

class Menu_item_Read(BaseModel):
    
    item_id: int
    restaurant_id: int
    name: str
    description: str
    price: float
    availability: bool


class Menu_item_Create(BaseModel):
    item_id: int
    restaurant_id: int
    name: str
    description: str
    price: float
    availability: bool = True


class Menu_item_Update(BaseModel):
    item_id: int | None = None
    restaurant_id: int | None = None
    name: str | None = None
    description: str | None = None
    price: float | None = None
    availability: bool | None = None
    