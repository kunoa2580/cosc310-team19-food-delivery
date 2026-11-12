
from pydantic import BaseModel, Field


""" [
    {
        "cart_id": 1,
        "customer_id": 1,
        "checkout_status": false,
        "items": [
            {
                "item_id": 2,
                "restaurant_id": 1,
                "name": "Iced Peach Black Tea Lemonade",
                "price": 4.99,
                "availability": true,
                "quantity": 1
            },
            {
                "item_id": 1,
                "restaurant_id": 1,
                "name": "Really Small Hamburger",
                "price": 10.99,
                "availability": true,
                "quantity": 2
            }
        ]
    },
    {
        "cart_id": 2,
        "customer_id": 2,
        "checkout_status": false,
        "items": [
            {
                "item_id": 2,
                "restaurant_id": 1,
                "name": "Iced Peach Black Tea Lemonade",
                "price": 4.99,
                "availability": true,
                "quantity": 1
            },
            {
                "item_id": 1,
                "restaurant_id": 1,
                "name": "Really Small Hamburger",
                "price": 10.99,
                "availability": true,
                "quantity": 2
            }
        ]
        
    }
]

 """



class ItemInCartCreate(BaseModel):
    item_id: int
    restaurant_id: int
    name: str
    price: float
    availability: bool
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")

class ItemInCartUpdate(BaseModel):
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")

class ItemInCartRead(BaseModel):
    item_id: int
    restaurant_id: int
    name: str
    price: float
    availability: bool
    quantity: int

class ShoppingCartCreate(BaseModel):
    customer_id: int

class ShoppingCartUpdate(BaseModel):
    checkout_status: bool | None = None

class ShoppingCartRead(BaseModel):
    cart_id: int
    customer_id: int
    checkout_status: bool
    items: list[ItemInCartRead] = []


