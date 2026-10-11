import json
from pathlib import Path


def test_get_restaurants_list(client):
    
    response = client.get("/restaurants")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 3
    assert data[0]["id"] == 1
    assert data[0]["name"] == "Green Bowl Cafe"
    assert data[1]["id"] == 2
    assert data[2]["id"] == 3

def test_get_restaurants_by_id(client):
    response = client.get("/restaurants/1")
    assert response.status_code == 200
    response = response.json()
    assert response["id"] == 1

def test_get_by_cuisine(client):
    response = client.get("/restaurants/filtered-by-Italian-type")
    assert response.status_code == 200
    response = response.json()
    assert response == [{
    "id": 2,
    "name": "Cedar & Co.",
    "address": "45 Oak Avenue, Burnaby, BC",
    "phone_number": "604-555-0102",
    "email": "contact@cedarco.ca",
    "website": "https://cedarco.ca",
    "cuisine_type": "Italian",
    "opening_hours": "Tue-Sun: 11:30 AM - 10:00 PM",
    "rating": 4.5,
    "availability": True
  }]



def test_add_new_restaurants_created(client):
    response = client.post(
        "/restaurants", 
        json =  {
            "id":6,
            "name":"testRestaurant",
            "address":"testAddress",
            "phone_number":"testPhone",
            "email":"testEmail",
            "website":"testWebsite",
            "cuisine_type":"testCuisine",
            "opening_hours":"testHours",
            "rating":5.0,
            "availability": True
        }
    )
    
    assert response.status_code == 201
    

def test_add_new_restaurants_conflict(client):

    client.post(
        "/restaurants", 
        json = {
            "id":6,
            "name":"testRestaurant",
            "address":"testAddress",
            "phone_number":"testPhone",
            "email":"testEmail",
            "website":"testWebsite",
            "cuisine_type":"testCuisine",
            "opening_hours":"testHours",
            "rating":5.0,
            "availability": True
        }
    )
    
    response = client.post(
        "/restaurants", 
        json =  {
            "id":6,
            "name":"testRestaurant",
            "address":"testAddress",
            "phone_number":"testPhone",
            "email":"testEmail",
            "website":"testWebsite",
            "cuisine_type":"testCuisine",
            "opening_hours":"testHours",
            "rating":5.0,
            "availability": True
        }
    )
    
    assert response.json() == {"detail": "A restaurant with the name testRestaurant already exists"}
    assert response.status_code == 409

def test_delete_restaurant_not_found(client):
    response = client.delete("/restaurants/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Restaurant with id 999 was not found."
    }
    
    
    