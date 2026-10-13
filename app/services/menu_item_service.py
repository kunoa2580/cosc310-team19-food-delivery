from app.repositories.menu_item_repository import MenuItemRepository
from app.schemas.menu_item import MenuItemUpdate ,MenuItemCreate, MenuItemRead
from app.errors import (
    MenuItemNotFoundError,
    DuplicateMenuItemError,
    MenuItemRestaurantNotFoundError,
    InvalidMenuItemUpdateError
)

menu_repo = MenuItemRepository() 

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
    menu_items = menu_service_list(restaurant_id)
    for i in menu_items:
        if i.name == payload.name:
            raise DuplicateMenuItemError(f"{payload.name} is Duplicate")

    record = menu_repo.menu_repo_create(payload.model_dump(), restaurant_id)
    return MenuItemRead(**record)


def menu_service_update(restaurant_id: int, item_id: int, payload: MenuItemUpdate) -> MenuItemRead:
    menu_ = menu_service_list(restaurant_id)
    if not payload.model_dump(exclude_unset=True): 
        raise InvalidMenuItemUpdateError("can not input nothing")
    for i in menu_:
        if i.restaurant_id == restaurant_id and i.item_id != item_id and i.name == payload.name:
            raise DuplicateMenuItemError (f"Item is duplicated")    
    record = menu_repo.menu_repo_update(restaurant_id, item_id, payload.model_dump(exclude_unset=True))
    if record is None:
        raise MenuItemNotFoundError(f"No menu item {item_id} on restaurant {restaurant_id}")
    
    return MenuItemRead(**record)


def menu_service_delete( restaurant_id: int, item_id: int) -> None:
    if not menu_repo.menu_repo_delete(restaurant_id, item_id):
        raise MenuItemNotFoundError (f"restaurant or item does not exit") 
    return None