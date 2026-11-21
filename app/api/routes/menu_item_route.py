from fastapi import APIRouter, HTTPException, status, Depends
from app.api.auth import reject_customer_edit
from app.services.menu_item_service import (
    menu_service_list,
    menu_service_get_by_id,
    menu_service_add,
    menu_service_update,
    menu_service_delete,
    require_unique_menu_item_name,
)
from app.errors import MenuItemNotFoundError, DuplicateMenuItemError, InvalidMenuItemUpdateError, MenuItemRestaurantNotFoundError, ResourceInUseError
from app.schemas.menu_item import MenuItemUpdate, MenuItemCreate, MenuItemRead, MenuItemPreview

router = APIRouter(prefix="/restaurant")


@router.post(
    "/menu-items/validate",
    response_model=MenuItemCreate,
    summary="Validate a demo menu item",
    description="Check submitted fields and names from the demo menu without reading or saving menu records.",
    responses={409: {"description": "Another item in the submitted menu already uses this name"}},
)
def menu_route_validate_preview(payload: MenuItemPreview) -> MenuItemCreate:
    try:
        require_unique_menu_item_name(payload.item.name, payload.other_names)
    except DuplicateMenuItemError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    return payload.item


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

@router.post("/{restaurant_id}/menu-items/create", status_code=status.HTTP_201_CREATED,
            dependencies=[Depends(reject_customer_edit)],
            responses={
                401: {"description": "Sign-in required"},
                403: {"description": "Customers cannot edit restaurant or menu information"},
            })
def menu_route_add_item(restaurant_id: int, payload: MenuItemCreate) -> MenuItemRead:
    try:
        item = menu_service_add(restaurant_id, payload)
    except MenuItemRestaurantNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except DuplicateMenuItemError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    return item
	
@router.delete("/{restaurant_id}/menu-items/delete/{item_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(reject_customer_edit)],
                responses={
                    401: {"description": "Sign-in required"},
                    403: {"description": "Customers cannot edit restaurant or menu information"},
                    409: {"description": "Item is still in use and cannot be deleted"},
                })
def menu_route_delete_item(restaurant_id: int, item_id: int) -> None:
    try:
        menu_service_delete(restaurant_id, item_id)
    except MenuItemNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ResourceInUseError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    return None

@router.patch("/{restaurant_id}/menu-items/update/{item_id}", status_code=status.HTTP_200_OK,
              dependencies=[Depends(reject_customer_edit)],
                responses={
                400: {"description": "Empty update or invalid fields"},
                401: {"description": "Sign-in required"},
                403: {"description": "Customers cannot edit restaurant or menu information"},
                404: {"description": "Menu item not found"},
                409: {"description": "Duplicate menu item name"},
                })
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
            status_code=status.HTTP_409_CONFLICT,
            detail=str(d),
        )
    return item
