from collections.abc import Iterable

from app.repositories.restaurant_repository import (
    RestaurantRepository

)
from app.schemas.restaurant import RestaurantCreate, RestaurantUpdate, RestaurantRead
from app.errors import DuplicateRestaurantError, RestaurantNotFoundError, ResourceInUseError
from app.repositories.account_repository import AccountRepository
from app.repositories.menu_item_repository import MenuItemRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.shopping_cart_repository import ShoppingCartRepository

cart_repo = ShoppingCartRepository()
order_repo = OrderRepository()
restaurant_repo = RestaurantRepository()
account_repo = AccountRepository()
menu_repo = MenuItemRepository()


def require_unique_restaurant_name(name: str, other_names: Iterable[str]) -> None:
    if name in other_names:
        raise DuplicateRestaurantError(f"A restaurant with the name {name} already exists")


def restaurant_service_update(restaurant_id: int, updates: RestaurantUpdate) -> RestaurantRead:
    restaurant_service_get_by_id(restaurant_id)
    changes = updates.model_dump(exclude_unset=True, exclude_none = True) #excluding updates with unfilled values

    if "name" in changes:
        require_unique_restaurant_name(
            changes["name"],
            (restaurant["name"] for restaurant in restaurant_repo.restaurant_repo_list()
             if restaurant["id"] != restaurant_id),
        )

    restaurant = restaurant_repo.restaurant_repo_update_by_id(restaurant_id, changes)
    if restaurant is None:
        raise RestaurantNotFoundError(f"Restaurant with id {restaurant_id} was not found.")
    return RestaurantRead(**restaurant)

def restaurant_service_create(new_restaurant: RestaurantCreate) -> RestaurantRead:

    restaurants = restaurant_repo.restaurant_repo_list()
    require_unique_restaurant_name(new_restaurant.name, (restaurant["name"] for restaurant in restaurants))

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
    restaurant_service_get_by_id(restaurant_id)

    if (
        menu_repo.menu_repo_list(restaurant_id)
        or cart_repo.cart_repo_has_reference(restaurant_id)
        or order_repo.order_repo_has_reference(restaurant_id)
        or any(
            restaurant_id in account.get("restaurant_ids", [])
            for account in account_repo.list_accounts()
        )
    ):
        raise ResourceInUseError(
            "This restaurant is still in use. Mark it unavailable instead."
        )

    if not restaurant_repo.restaurant_repo_delete_by_id(restaurant_id):
        raise RestaurantNotFoundError(f"Restaurant with id {restaurant_id} was not found.")