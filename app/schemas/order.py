from pydantic import BaseModel, Field


class OrderItemRead(BaseModel):
    item_id: int
    name: str
    unit_price: float = Field(ge=0)
    quantity: int = Field(gt=0)


class OrderRead(BaseModel):
    order_id: int
    customer_id: int
    restaurant_id: int
    items: list[OrderItemRead]
    total: float = Field(ge=0)
    status: str
    created_at: str