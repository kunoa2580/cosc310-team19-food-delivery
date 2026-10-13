
from fastapi import APIRouter, HTTPException, status
from app.services.menu_item_service import (
    menu_service_list,
    menu_service_get_by_id,
    menu_service_add,
    menu_service_update,
    menu_service_delete,
)
from app.errors import MenuItemNotFoundError, DuplicateMenuItemError, InvalidMenuItemUpdateError
from app.schemas.menu_item import MenuItemUpdate ,MenuItemCreate, MenuItemRead

router = APIRouter(prefix="/restaurant")

# api endpoint assumed that user have already selected restaurant
@router.get("/{restaurant_id}/menu-items", status_code=status.HTTP_200_OK)
def menu_route_list_items(restaurant_id: int) -> list[MenuItemRead]:
    return menu_service_list(restaurant_id)

@router.get("/{restaurant_id}/menu-items/{item_id}", status_code=status.HTTP_200_OK)
def menu_route_get_by_id(restaurant_id: int, item_id: int) -> MenuItemRead:
    try:
        item = menu_service_get_by_id(restaurant_id, item_id)
    except MenuItemNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    return item

@router.post("/{restaurant_id}/menu-items/create", status_code=status.HTTP_201_CREATED)
def menu_route_add_item(restaurant_id: int, payload: MenuItemCreate) -> MenuItemRead:
    try:
        item = menu_service_add(restaurant_id, payload)
    except DuplicateMenuItemError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    return item
	
@router.delete("/{restaurant_id}/menu-items/delete/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def menu_route_delete_item(restaurant_id: int, item_id: int) -> None:
    try:
        menu_service_delete(restaurant_id, item_id)
    except MenuItemNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    return None

@router.patch("/{restaurant_id}/menu-items/update/{item_id}", status_code=status.HTTP_200_OK)
def menu_route_update_item(restaurant_id: int, item_id: int, payload: MenuItemUpdate) -> MenuItemRead:
    try:
        item = menu_service_update(restaurant_id, item_id, payload)
    except MenuItemNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InvalidMenuItemUpdateError as x:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(x),
        )
    except DuplicateMenuItemError as d:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(d),
        )
    return item
