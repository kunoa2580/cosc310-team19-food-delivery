
from pydantic import BaseModel


class menu_item_read(BaseModel):# menu item model
    item_id: int
    restaurant_id: int
    name: str
    description: str
    price: float
    availability: bool