import pytest
from app.errors import DuplicateRestaurantError, RestaurantNotFoundError

from app.services.restaurant_service import (
    restaurant_service_create, 
    restaurant_service_list, 
    restaurant_service_get_by_id,
    restaurant_service_get_by_cuisine,
    restaurant_service_delete
)
from app.schemas.restaurant import RestaurantCreate, RestaurantRead


sample_data = [
    {
    "name": "sample_data_name",
    "address": "sample_data_name",
    "phone_number": "sample_data_name",
    "email": "sample_data_name",
    "website": "sample_data",
    "cuisine_type": "sample_data_name",
    "opening_hours": "sample_data_name",
    "rating": 4.5,
    "availability": True
  }
]



def test_restaurant_service_create_good(client):
    new_restaurant = RestaurantCreate(**sample_data[0])
    response = restaurant_service_create(new_restaurant)

    assert response.name == sample_data[0]["name"]

# Implemented test for test_restaurant_service_create_conflict to test DuplicateRestaurantError exception
def test_restaurant_service_create_conflict (client):
    new_restaurant = RestaurantCreate(**sample_data[0])

    # Create it first the test the Conflict 
    restaurant_service_create(new_restaurant)
    with pytest.raises(DuplicateRestaurantError):
        restaurant_service_create(new_restaurant)
    

# Implemented test for restaurant_service_list to test returned list of restaurant
# and the model is correct
def test_restaurant_service_list(client):
    response = restaurant_service_list()
    assert isinstance(response, list) 
    assert isinstance(response[0], RestaurantRead)

# Implenmented test for restaurant_service get id 
def test_restaurant_service_get_by_id_good(client):
    response = restaurant_service_get_by_id(1)
    assert isinstance(response, RestaurantRead)
    assert response.id == 1

def test_restaurant_service_get_by_id_not_found(client):
    with pytest.raises(RestaurantNotFoundError):
        restaurant_service_get_by_id(1020123)


def test_restaurant_service_get_by_cuisine_good(client):
    respone = restaurant_service_get_by_cuisine("Italian")
    assert isinstance(respone, list)
    assert isinstance(respone[0], RestaurantRead)
    assert respone[0].cuisine_type == "Italian"


def test_restaurant_service_get_by_cuisine_not_found(client):
    with pytest.raises(RestaurantNotFoundError):
        restaurant_service_get_by_cuisine("the cuisine")

@pytest.mark.skip("Not required for M1")
def test_restaurant_service_delete_good(client):
    response = restaurant_service_list()
    len_before_delete = len(response)
    restaurant_service_delete(1)
    after_delete = restaurant_service_list()
    len_after_delete = len(after_delete)
    assert len_before_delete-1 ==  len_after_delete

@pytest.mark.skip("Not required for M1")
def test_restaurant_service_delete_not_found(client):
    with pytest.raises(RestaurantNotFoundError):
        restaurant_service_delete(1000)