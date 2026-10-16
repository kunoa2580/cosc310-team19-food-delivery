from fastapi import APIRouter, HTTPException, status

from app.services.menu_service import (
    menu_service_list,
    menu_service_get_by_id
)

from app.schemas.menu_item import menu_item_read
from app.errors import MenuItemNotFoundError


router = APIRouter(prefix="/restaurants", tags=["Menus"])


@router.get(# get the menu
    "/{restaurant_id}/menu-items",
    response_model=list[menu_item_read]
)
def get_menu_items(restaurant_id: int):
    return menu_service_list(restaurant_id)


@router.get(# get the item
    "/{restaurant_id}/menu-items/{item_id}",
    response_model=menu_item_read
)
def get_menu_item(restaurant_id: int, item_id: int):
    try:
        return menu_service_get_by_id(restaurant_id, item_id)

    # Return 404 if the menu item does not exist
    except MenuItemNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        ) from e