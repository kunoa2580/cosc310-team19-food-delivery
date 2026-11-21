import json

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.api.routes.menu_item_route import menu_route_update_item, menu_route_validate_preview
from app.api.routes.restaurant_route import restaurant_route_validate_preview
from app.schemas.menu_item import MenuItemPreview, MenuItemUpdate
from app.schemas.restaurant import RestaurantPreview


@pytest.mark.parametrize("price", ["", None, -1, "Infinity"])
def test_demo_menu_uses_the_backend_price_model(price):
    with pytest.raises(ValidationError, match=r"item\.price"):
        MenuItemPreview(item={"name": "Tea", "description": "Black tea", "price": price}, other_names=[])


def test_demo_menu_rejects_duplicates_and_validates_without_saving(tmp_path):
    path = tmp_path / "menu_items.json"
    before = path.read_bytes()
    draft = MenuItemPreview(item={"name": "Tea", "description": "Black tea", "price": "0"}, other_names=["Tea"])

    with pytest.raises(HTTPException) as error:
        menu_route_validate_preview(draft)
    assert error.value.status_code == 409

    draft.other_names.clear()
    assert menu_route_validate_preview(draft).price == 0
    assert path.read_bytes() == before


@pytest.mark.parametrize(("changes", "expected"), [({"price": None}, 400), ({"name": "Iced Peach Green Tea Lemonade"}, 409)])
def test_real_menu_update_rejects_invalid_changes_before_writing(tmp_path, changes, expected):
    path = tmp_path / "menu_items.json"
    before = path.read_bytes()

    with pytest.raises(HTTPException) as error:
        menu_route_update_item(1, 2, MenuItemUpdate(**changes))

    assert error.value.status_code == expected
    assert path.read_bytes() == before


def test_demo_restaurant_uses_backend_model_and_duplicate_rule(tmp_path):
    path = tmp_path / "restaurants.json"
    before = path.read_bytes()
    restaurant = json.loads(before)[0]
    draft = RestaurantPreview(restaurant=restaurant, other_names=[restaurant["name"]])

    with pytest.raises(HTTPException) as error:
        restaurant_route_validate_preview(draft)
    assert error.value.status_code == 409

    draft.other_names.clear()
    assert restaurant_route_validate_preview(draft).name == restaurant["name"]
    assert path.read_bytes() == before
