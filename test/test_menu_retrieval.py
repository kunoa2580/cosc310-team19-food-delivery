
import pytest

from app.services.menu_service import (
    menu_service_list,
    menu_service_get_by_id
)
from app.errors import MenuItemNotFoundError



def test_menu_service_list():# get all items from restaruant 1
    items = menu_service_list(1)

    assert isinstance(items, list)
    assert len(items) > 0

    for item in items:
        assert item.restaurant_id == 1


def test_menu_service_get_by_id():# get first item from restaruant 1
    items = menu_service_list(1)
    assert len(items) > 0

    first_item = items[0]

    result = menu_service_get_by_id(1, first_item.item_id)

    assert result.item_id == first_item.item_id
    assert result.restaurant_id == 1
    assert result.name == first_item.name


def test_menu_service_get_not_found():# get the item does not exist
    with pytest.raises(MenuItemNotFoundError):
        menu_service_get_by_id(1, 999999)


def test_menu_service_empty():# get the item from the restaurant does not exist
    items = menu_service_list(999999)

    assert items == []