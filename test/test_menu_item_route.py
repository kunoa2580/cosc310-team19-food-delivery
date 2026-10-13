import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.routes.menu_item_route import (
    menu_route_list_items,
    menu_route_get_by_id,
    menu_route_add_item,
    menu_route_delete_item,
    menu_route_update_item
    
    )
from app.errors import MenuItemNotFoundError, DuplicateMenuItemError



def test_menu_route_list_items(client):
    response = client.get("/restaurant/1/menu-items")
    data = response.json()
    assert response.status_code == 200
    assert data[0]["name"] == "Iced Peach Green Tea Lemonade"
    assert data[0]["restaurant_id"] == 1
    assert data[1]["restaurant_id"] == 1
    assert data[1]["name"] == "Iced Peach Black Tea Lemonade"
    assert len(data) == 4


def test_menu_route_get_by_id_good(client):
    response = client.get("/restaurant/1/menu-items/1")
    data = response.json()
    assert data["name"] == "Iced Peach Green Tea Lemonade"
    assert data["restaurant_id"] == 1
    assert data["item_id"] == 1

def test_menu_route_get_by_id_bad(client):
    response = client.get("/restaurant/999/menu-items/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "No menu item 999 on restaurant 999"




def test_menu_route_add_item_GOOD(client):
    payload = {
        "name": "Test Item",
        "description": "This is a test item",
        "price": 9.99
    }
    response = client.post("/restaurant/10/menu-items/create", json=payload)
    data = response.json()
    assert response.status_code == 201
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert data["price"] == payload["price"]
    assert data["restaurant_id"] == 10
    assert "item_id" in data

def test_menu_route_add_item_BAD(client):
    payload = {
        "name": "Test Item",
        "description": "This is a test item",
        "price": 9.99
    }
    client.post("/restaurant/10/menu-items/create", json=payload)
    response = client.post("/restaurant/10/menu-items/create", json=payload)
    assert response.json()["detail"] ==  "Test Item is Duplicate"
    assert response.status_code == 409

def test_menu_route_delete_item_good(client):
    response = client.delete("/restaurant/1/menu-items/delete/1")
    assert response.status_code == 204

def test_menu_route_delete_item_bad(client):
    response = client.delete("/restaurant/10/menu-items/delete/10")
    assert response.json()["detail"] ==  "restaurant or item does not exit"
    assert response.status_code == 404

def test_menu_route_update_item_good(client):
    payload={
        "name": "Iceds Peach Green Tea Lemonade",
        "description": "As refreshing blend of green tea, fresh peach syrup, and lemonade.",
        "price": 0.1,
        "availability": False
    }
    response = client.patch("/restaurant/1/menu-items/update/1", json=payload)
    assert response.status_code == 200
    response = response.json()
    assert response["name"] == payload["name"]
    assert response["description"] == "As refreshing blend of green tea, fresh peach syrup, and lemonade."
    assert response["price"] == 0.1
    assert response["availability"] is False

def test_menu_route_update_item_bad(client):
    payload = {
        "name": "Updated Test Item",
        "description": "This is an updated test item",
        "price": 10.99
    }
    response = client.patch("/restaurant/10/menu-items/update/10", json=payload)
    data = response.json()
    assert response.status_code == 404
    assert data["detail"] == "No menu item 10 on restaurant 10"
