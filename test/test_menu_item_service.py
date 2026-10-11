from app.services.menu_item_service import (
    menu_service_list,
    menu_service_get_by_id,
    menu_service_add,
    menu_service_update,
    menu_service_delete,
)

from app.errors import MenuItemNotFoundError, DuplicateMenuItemError, InvalidMenuItemUpdateError
import pytest
from app.schemas.menu_item import MenuItemCreate,MenuItemRead,MenuItemUpdate






def test_menu_service_update_not_found():
    payload = MenuItemUpdate( price=7.0)
    with pytest.raises(MenuItemNotFoundError):
        menu_service_update(21,21,payload)

def test_menu_service_update_good():
    payload = MenuItemUpdate( price=7.0)
    after = menu_service_update(1,1,payload)
    assert after.price == 7.0
    assert after.name == "Iced Peach Green Tea Lemonade"
    assert after.item_id == 1
    assert after.restaurant_id == 1
    assert after.description == "A refreshing blend of green tea, fresh peach syrup, and lemonade."
    assert after.availability

def test_menu_service_update_empty():
    payload = MenuItemUpdate()
    with pytest.raises(InvalidMenuItemUpdateError):
        menu_service_update(1,1,payload)
    

def test_menu_service_update_duplicate():
    payload = MenuItemUpdate(name="Iced Peach Green Tea Lemonade")
    with pytest.raises(DuplicateMenuItemError):
        menu_service_update(1,2,payload)

def test_menu_service_update_own_name():
    payload = MenuItemUpdate(name="Iced Peach Black Tea Lemonade")
    
    after = menu_service_update(1,2,payload)
    assert after.availability
    assert after.description == "A refreshing blend of Black tea, fresh peach syrup, and lemonade."
    assert after.restaurant_id == 1
    assert after.item_id == 2
    assert after.price == 4.99
    assert after.name == "Iced Peach Black Tea Lemonade"