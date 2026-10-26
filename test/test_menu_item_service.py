from app.services.menu_item_service import (
    menu_service_list,
    menu_service_get_by_id,
    menu_service_add,
    menu_service_update,
    menu_service_delete,
)

from app.errors import MenuItemNotFoundError, DuplicateMenuItemError, InvalidMenuItemUpdateError, MenuItemRestaurantNotFoundError
import pytest
from app.schemas.menu_item import MenuItemCreate,MenuItemRead,MenuItemUpdate

sample= MenuItemCreate(  **{
    "name": "Iced Peach Green Tea Lemonade",
    "description": "A refreshing blend of green tea, fresh peach syrup, and lemonade.",
    "price": 0.0,
    "availability": True
  })

def test_menu_service_add_bad():
    with pytest.raises(DuplicateMenuItemError):
        menu_service_add(1, sample)

def test_menu_service_add_restaurant_not_found():
    with pytest.raises(MenuItemRestaurantNotFoundError):
        menu_service_add(999, sample)

def test_menu_service_add_good():
    response = menu_service_add(2, sample)
    assert isinstance(response, MenuItemRead)
    assert response.restaurant_id == 2
    assert response.name ==  "Iced Peach Green Tea Lemonade"

def test_menu_service_delete_good():
    response = menu_service_delete(1,1)
    assert response is None

def test_menu_service_delete_bad():
    with pytest.raises(MenuItemNotFoundError):
        menu_service_delete(999,999)

def test_menu_service_get_by_id():
    response = menu_service_get_by_id(1,1)
    response.model_dump() == {
    "item_id": 1,
    "restaurant_id": 1,
    "name": "Iced Peach Green Tea Lemonade",
    "description": "A refreshing blend of green tea, fresh peach syrup, and lemonade.",
    "price": 0.0,
    "availability": True
  }

def test_menu_service_get_by_id_bad():
    with pytest.raises(MenuItemNotFoundError) as exc_info:
        menu_service_get_by_id(1000,12311)
    assert str(exc_info.value) == "No menu item 12311 on restaurant 1000"


def test_menu_service_list():
    r = menu_service_list(1)
    assert isinstance(r,list)
    assert len(r) == 4
    sample= MenuItemCreate(  **{
    "name": "Iced Peach Green AND BLACK Tea Lemonade",
    "description": "A refreshing blend of Green AND BLACK tea, fresh peach syrup, and lemonade.",
    "price": 0.0,
    "availability": True
    })
    menu_service_add(1, sample)
    after = menu_service_list(1)
    assert len(after) == 5
    assert after[len(after)-1].restaurant_id == 1
    assert after[len(after)-1].name == "Iced Peach Green AND BLACK Tea Lemonade"



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