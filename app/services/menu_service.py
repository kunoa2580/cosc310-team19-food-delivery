from app.repositories.menu_repository import (
    menu_repo_list,
    menu_repo_get_by_id
)
from app.schemas.menu_item import MenuItemRead
from app.errors import MenuItemNotFoundError


def menu_service_list(restaurant_id: int) -> list[MenuItemRead]:# get all items from repo layer
    items = menu_repo_list(restaurant_id)
    return [MenuItemRead(**item) for item in items]


def menu_service_get_by_id(restaurant_id: int,item_id: int) -> MenuItemRead:# get the item from repo layer
    item = menu_repo_get_by_id(restaurant_id, item_id)
    if item is None:# check the error
        raise MenuItemNotFoundError(
            f"Menu item {item_id} not found in restaurant {restaurant_id}"
        )
    return MenuItemRead(**item)