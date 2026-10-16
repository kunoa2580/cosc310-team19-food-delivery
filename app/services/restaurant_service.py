from app.repositories.restaurant_repository import (
    RestaurantRepository

)
from app.schemas.restaurant import RestaurantCreate, RestaurantUpdate, RestaurantRead
from app.errors import DuplicateRestaurantError, RestaurantNotFoundError

restaurant_repo = RestaurantRepository()


def restaurant_service_update(restaurant_id: int, updates: RestaurantUpdate) -> RestaurantRead:
    restaurant_service_get_by_id(restaurant_id)
    changes = updates.model_dump(exclude_unset=True, exclude_none = True) #excluding updates with unfilled values

    if "name" in changes:
        for restaurant in restaurant_repo.restaurant_repo_list():
            if restaurant["id"] != restaurant_id and restaurant["name"] == changes["name"]:
                raise DuplicateRestaurantError(
                    f"A restaurant with the name {changes['name']} already exists"
                )

    restaurant = restaurant_repo.restaurant_repo_update_by_id(restaurant_id, changes)
    if restaurant is None:
        raise RestaurantNotFoundError(f"Restaurant with id {restaurant_id} was not found.")
    return RestaurantRead(**restaurant)

def restaurant_service_create(new_restaurant: RestaurantCreate) -> RestaurantRead:

    restaurants = restaurant_repo.restaurant_repo_list()
    for restaurant in restaurants:
        if restaurant["name"] == new_restaurant.name:
            raise DuplicateRestaurantError(
                f"A restaurant with the name {new_restaurant.name} already exists"
            )

    restaurant = restaurant_repo.restaurant_repo_create(
        new_restaurant.model_dump()
    )

    return RestaurantRead(**restaurant)


def restaurant_service_list() -> list[RestaurantRead]:
    restaurants = restaurant_repo.restaurant_repo_list()
    return [RestaurantRead(**restaurant) for restaurant in restaurants]

def restaurant_service_get_by_id(restaurant_id: int) -> RestaurantRead:
    restaurant = restaurant_repo.restaurant_repo_get_by_id(
        restaurant_id
    )
    if restaurant is None:
        raise RestaurantNotFoundError(
            f"Restaurant with id {restaurant_id} was not found."
        )

    return RestaurantRead(**restaurant)

def restaurant_service_get_by_cuisine(cuisine: str) -> list[RestaurantRead]:
    restaurants = restaurant_repo.restaurant_repo_list()
    matched = [
        RestaurantRead(**restaurant)
        for restaurant in restaurants
        if restaurant["cuisine_type"].lower() == cuisine.lower()]
    
    if not matched:
        raise RestaurantNotFoundError(
            f"Restaurant of {cuisine} was not found"
        )
    return matched

def restaurant_service_delete(restaurant_id: int) -> None:
    deleted = restaurant_repo.restaurant_repo_delete_by_id(restaurant_id)

    if not deleted:
        raise RestaurantNotFoundError(
            f"Restaurant with id {restaurant_id} was not found."
        )
