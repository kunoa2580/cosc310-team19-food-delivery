from fastapi.testclient import TestClient
import pytest
from fastapi import APIRouter, FastAPI, HTTPException, status
import json
from pathlib import Path
from app.main import app
from pydantic import BaseModel
DATA = Path("data/restaurants.json")

def restaurant_repo_read_json() -> list[dict]:
    with DATA.open() as file:
        return json.load(file)

client = TestClient(app)
@pytest.fixture
def restore_data():
    original = DATA.read_text()
    yield
    DATA.write_text(original)


def test_get_restaurants_list():
    
    response = client.get("/restaurants/restaurant-list")
    print(response.json() == restaurant_repo_read_json())
    assert response.status_code == 200
    assert response.json() == restaurant_repo_read_json()

def test_get_restaurants_by_id():
    response = client.get("/restaurants/1")
    assert response.status_code == 200
    response = response.json()
    assert response["id"] == 1



def test_get_by_cuisine():
    response = client.get("/restaurants?cuisine=st12ring")
    assert response.status_code == 200
    response = response.json()
    assert response == [{
    "id": 4,
    "name": "st12ring",
    "address": "stri12ng",
    "phone_number": "s12tring",
    "email": "str12ing",
    "website": "s12tring",
    "cuisine_type": "st12ring",
    "opening_hours": "str12ing",
    "rating": 0.0
  }]



def test_add_new_restaurants_created(restore_data):
    response = client.post(
        "/restaurants/restaurant-list", json=  {
    "id":6,
    "name":"testRestaurant",
    "address":"testAddress",
    "phone_number":"testPhone",
    "email":"testEmail",
    "website":"testWebsite",
    "cuisine_type":"testCuisine",
    "opening_hours":"testHours",
    "rating":5.0
  
    })
    
    assert response.status_code == 201
    

def test_add_new_restaurants_conflict(restore_data):

    client.post(
        "/restaurants/restaurant-list", json=  {
    "id":6,
    "name":"testRestaurant",
    "address":"testAddress",
    "phone_number":"testPhone",
    "email":"testEmail",
    "website":"testWebsite",
    "cuisine_type":"testCuisine",
    "opening_hours":"testHours",
    "rating":5.0
  
    })
    
    response = client.post(
        "/restaurants/restaurant-list", json=  {
    "id":6,
    "name":"testRestaurant",
    "address":"testAddress",
    "phone_number":"testPhone",
    "email":"testEmail",
    "website":"testWebsite",
    "cuisine_type":"testCuisine",
    "opening_hours":"testHours",
    "rating":5.0
  
    })
    
    assert response.status_code == 409
    
    
    