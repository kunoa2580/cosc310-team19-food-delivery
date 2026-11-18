from xmlrpc import client

import pytest
import random
from app.errors import CartNotFoundError, MenuItemNotFoundError, DuplicateMenuItemError, InvalidMenuItemUpdateError, MenuItemRestaurantNotFoundError, CustomerNotFoundError 
from app.api.routes.shopping_cart_route import shopping_cart_route as shoppingCart_route
from app.services.shopping_cart_service import shopping_cart_service as shoppingCart_service
from app.repositories.shopping_cart_repository import ShoppingCartRepository as shoppingCart_repository
from fastapi.testclient import TestClient

sC_route = shoppingCart_route()
sC_service = shoppingCart_service()
sC_repository = shoppingCart_repository()





def test_add_item_customer_route_good(client):
    response = client.post("/cart/add/1/1/1/1")
    data = response.json()
    assert response.status_code is 201
def test_add_item_customer_route_customer_not_found(client):
    response = client.post("/cart/add/999/1/1/1")
    assert response.status_code == 404
    assert response.json()["detail"] == "Customer 999 is not found"
def test_add_item_customer_route_menu_item_not_found(client):
    response = client.post("/cart/add/1/999/999/1")
    assert response.status_code == 404
    assert response.json()["detail"] == "No menu item 999 on restaurant 999"
def test_add_item_customer_route_cart_not_found(client):
    
    response = client.post("/cart/add/4/1/1/1")
    assert response.status_code == 404
    assert response.json()["detail"] == "No cart for customer 4"

def test_edit_item_route_good(client):
    client.post("/cart/add/1/1/1/1")
    response = client.patch("/cart/edit/1/1/2")
    data = response.json()
    assert response.status_code is 200
    assert any(line["item_id"] == 1 and line["quantity"] == 2 for line in data["items"])

def test_add_item_persists_to_disk():
    repo = shoppingCart_repository()
    repo.cart_add_item_to_cart_repo(1, {"item_id": 2, "restaurant_id": 1,
                                        "name": "x", "price": 4.99,
                                        "availability": True, "quantity": 1})

    fresh = shoppingCart_repository()          
    cart = fresh.cart_view_by_customer_repo(1)
    assert any(line["item_id"] == 2 for line in cart["items"])



def test_add_item_service_good():
    response = sC_service.cart_add_item_to_cart_service(1, 1, 1, 1)
    assert response.customer_id == 1
    assert any(line.item_id == 1 for line in response.items)

def test_add_item_service_bad():
    with pytest.raises(MenuItemNotFoundError):
        sC_service.cart_add_item_to_cart_service(1, 999, 999, 1)


def test_add_item_service_customer_not_found():
    with pytest.raises(CustomerNotFoundError):
        sC_service.cart_add_item_to_cart_service(999, 1, 1, 1)

def test_add_item_service_cart_not_found():
    with pytest.raises(CartNotFoundError):
        sC_service.cart_add_item_to_cart_service(4, 1, 1, 1)

def test_edit_item_service_good():
    sC_service.cart_add_item_to_cart_service(1, 1, 1, 1)
    response = sC_service.cart_edit_item_to_cart_service(1, 1, 2)
    assert response.customer_id == 1
    assert any(line.item_id == 1 and line.quantity == 2 for line in response.items)