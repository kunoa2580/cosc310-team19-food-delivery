from pydantic import BaseModel, Field


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
    price: float = Field(ge=0, allow_inf_nan=False)
    availability: bool = True


class MenuItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    availability: bool | None = None


class MenuItemPreview(BaseModel):
    item: MenuItemCreate
    other_names: list[str]






