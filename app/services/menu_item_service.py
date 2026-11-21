from collections.abc import Iterable

from pydantic import ValidationError
from app.repositories.order_repository import OrderRepository
from app.repositories.shopping_cart_repository import ShoppingCartRepository
from app.repositories.menu_item_repository import MenuItemRepository
from app.schemas.menu_item import MenuItemUpdate, MenuItemCreate, MenuItemRead
from app.services.restaurant_service import restaurant_service_get_by_id
from app.errors import (
    MenuItemNotFoundError,
    DuplicateMenuItemError,
    MenuItemRestaurantNotFoundError,
    InvalidMenuItemUpdateError,
    RestaurantNotFoundError,
    ResourceInUseError
)

menu_repo = MenuItemRepository() 
cart_repo = ShoppingCartRepository()
order_repo = OrderRepository()


def require_unique_menu_item_name(name: str, other_names: Iterable[str]) -> None:
    if name in other_names:
        raise DuplicateMenuItemError(f"{name} is Duplicate")

def menu_service_list(restaurant_id: int) -> list[MenuItemRead]: 
    menu_items = menu_repo.menu_repo_list(restaurant_id)
    L = []
    for i in menu_items:
        i = MenuItemRead(**i)
        L.append(i)
    return L

def menu_service_get_by_id(restaurant_id: int, item_id: int) -> MenuItemRead :
    record = menu_repo.menu_repo_get_by_id(restaurant_id, item_id)
    if  record is None:                                                          
        raise MenuItemNotFoundError(f"No menu item {item_id} on restaurant {restaurant_id}")    
    return MenuItemRead(**record)

def menu_service_add(restaurant_id: int, payload: MenuItemCreate) -> MenuItemRead:
    try:
        restaurant_service_get_by_id(restaurant_id)
    except RestaurantNotFoundError:
        raise MenuItemRestaurantNotFoundError(f"Restaurant with id {restaurant_id} was not found.")
    menu_items = menu_repo.menu_repo_list(restaurant_id)
    require_unique_menu_item_name(payload.name, (item["name"] for item in menu_items))

    record = menu_repo.menu_repo_create(payload.model_dump(), restaurant_id)
    return MenuItemRead(**record)


def menu_service_update(restaurant_id: int, item_id: int, payload: MenuItemUpdate) -> MenuItemRead:
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise InvalidMenuItemUpdateError("Provide at least one field to update.")

    current = menu_repo.menu_repo_get_by_id(restaurant_id, item_id)
    if current is None:
        raise MenuItemNotFoundError(f"No menu item {item_id} on restaurant {restaurant_id}")

    try:
        candidate = MenuItemCreate.model_validate({**current, **changes})
    except ValidationError as error:
        raise InvalidMenuItemUpdateError("Menu item fields must have valid, non-null values.") from error

    if "name" in changes:
        menu_items = menu_repo.menu_repo_list(restaurant_id)
        require_unique_menu_item_name(
            candidate.name, (item["name"] for item in menu_items if item["item_id"] != item_id)
        )

    record = menu_repo.menu_repo_update(restaurant_id, item_id, changes)
    if record is None:
        raise MenuItemNotFoundError(f"No menu item {item_id} on restaurant {restaurant_id}")
    
    return MenuItemRead(**record)


def menu_service_delete(restaurant_id: int, item_id: int) -> None:
    if menu_repo.menu_repo_get_by_id(restaurant_id, item_id) is None:
        raise MenuItemNotFoundError("restaurant or item does not exit")

    if (
        cart_repo.cart_repo_has_reference(restaurant_id, item_id)
        or order_repo.order_repo_has_reference(restaurant_id, item_id)
    ):
        raise ResourceInUseError(
            "This menu item is in use by a cart or order. Mark it unavailable instead."
        )

    if not menu_repo.menu_repo_delete(restaurant_id, item_id):
        raise MenuItemNotFoundError("restaurant or item does not exit")