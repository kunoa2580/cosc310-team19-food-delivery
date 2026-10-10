
from fastapi import APIRouter, HTTPException, status
from app.services.menu_item_service import (
    menu_item_service_create,
    menu_item_service_list,
    menu_item_service_get_by_id,
    menu_item_service_update,
    menu_item_service_delete,
    menu_item_service_get_by_restaurant,
    menu_item_service_create_by_restaurant_name
)
# from app.errors import MenuItemNotFoundError, DuplicateMenuItemError
from app.schemas.menu_item import Menu_item_Create, Menu_item_Read, Menu_item_Update

router = APIRouter(prefix="/menu-items")

# api endpoint assumed that user have already selected restaurant


# @TheTureFADED
@router.get("")
def menu_item_route_get_list() -> list[Menu_item_Read]:
    return menu_item_service_list()


# @TheTureFADED
@router.post("/{restaurant_id}/create")
def menu_item_route_create(restaurant_id:int,new_menu_item: Menu_item_Create) -> Menu_item_Read:

    try:
        return menu_item_service_create(restaurant_id,new_menu_item)
    except Exception as e:
        raise e
# @TheTureFADED
@router.post("/by-name/{restaurant_name}/create")
def menu_item_route_create(restaurant_name:str,new_menu_item: Menu_item_Create) -> Menu_item_Read:
    return menu_item_service_create_by_restaurant_name(restaurant_name,new_menu_item)

# @router.get("{restaurant_id}/menu-items/{menu_items_id}")
# def menu_item_route_get_by_id(menu_items_id:int) -> Menu_item_Read:
#     return menu_item_service_get_by_id(menu_items_id)


# @router.put("{res}/menu-items-update/{item_id}")
# def menu_item_route_update(item_id:int, updated_menu_item: Menu_item_Update) -> None:
#     return menu_item_service_update(item_id, updated_menu_item)


# @router.get("/menu-items-filtered-by/{restaurant_name}")
# def menu_item_route_get_by_restaurant(restaurant_name:str) -> list[Menu_item_Read]:
#     return menu_item_service_get_by_restaurant(restaurant_name)