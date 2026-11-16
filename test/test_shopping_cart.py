import pytest
import random
from app.errors import MenuItemNotFoundError, DuplicateMenuItemError, InvalidMenuItemUpdateError, MenuItemRestaurantNotFoundError, CustomerNotFoundError 
from app.api.routes.shopping_cart_route import shopping_cart_route as shoppingCart_route
from app.services.shopping_cart_service import shopping_cart_service as shoppingCart_service
from app.repositories.shopping_cart_repository import ShoppingCartRepository as shoppingCart_repository
from fastapi.testclient import TestClient

sC_route = shoppingCart_route()
sC_service = shoppingCart_service()
sC_repository = shoppingCart_repository()




# def test_add_item_customer_not_exits(client):

#     with pytest.raises(CustomerNotFoundError):
#         client.post("/cart/add/{customer_id}/{restaurant_id}/{item_id}/{quantity}")


# def test_add_item_customer(client):
#     # 

def test_add_item_customer_route_good(client):
    response = client.post("/cart/add/1/1/1/1")
    data = response.json()
    assert response.status_code is 201

# def test_add_item_customer_route_bad(client):
#     with pytest.raises(MenuItemNotFoundError) as e:
#         client.post("/cart/add/1/1123/1123/1")


def test_add_item_persists_to_disk():
    repo = shoppingCart_repository()
    repo.cart_add_item_to_cart_repo(1, {"item_id": 2, "restaurant_id": 1,
                                        "name": "x", "price": 4.99,
                                        "availability": True, "quantity": 1})

    fresh = shoppingCart_repository()          
    cart = fresh.cart_view_by_customer_repo(1)
    assert any(line["item_id"] == 2 for line in cart["items"])


