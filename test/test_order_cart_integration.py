from types import SimpleNamespace

import pytest

from app.errors import InvalidCartError
from app.schemas.menu_item import MenuItemUpdate
from app.services import order_service
from app.services.menu_item_service import menu_service_update


@pytest.fixture(autouse=True)
def active_customer(monkeypatch):
    monkeypatch.setattr(order_service, "_customer_is_active", lambda customer_id: True)


# Add items to the real shopping cart → Place order → Confirm that the order is correct.
# The shopping cart is cleared, and the order can be retrieved.
def test_checkout_with_real_cart_creates_order_and_clears_cart(client):
    assert client.post("/cart/add/4/1/2/2").status_code == 201

    response = client.post("/customers/4/checkout")
    assert response.status_code == 201
    order = response.json()
    assert order["customer_id"] == 4
    assert order["restaurant_id"] == 1
    assert order["total"] == 9.98
    assert order["items"] == [
        {"item_id": 2, "name": "Iced Peach Black Tea Lemonade", "unit_price": 4.99, "quantity": 2}
    ]

    assert client.get("/cart/view/4").json()["items"] == []

    assert client.get(f"/orders/{order['order_id']}").json() == order


# Add an item to the cart → Change the menu price → Place order → Confirm the order uses the current menu price, not the old price stored in the cart.
def test_checkout_uses_current_menu_price_not_the_price_stored_in_cart(client):
    client.post("/cart/add/4/1/2/2")
    assert client.get("/cart/view/4").json()["items"][0]["price"] == 4.99

    menu_service_update(1, 2, MenuItemUpdate(price=6.0))

    order = client.post("/customers/4/checkout").json()
    assert order["items"][0]["unit_price"] == 6.0
    assert order["total"] == 12.0


# Check out a customer who has no active cart → Confirm it is rejected with 400 and no order is created.
def test_checkout_without_an_active_cart_is_rejected(client):
    response = client.post("/customers/7/checkout")
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot check out an empty cart"
    assert client.get("/customers/7/orders").json() == []


# The cart service returns items from two restaurants (it normally rejects this) → Confirm _get_active_cart still rejects it.
def test_get_active_cart_rejects_items_from_two_restaurants(monkeypatch):
    def line(item_id, restaurant_id):
        return SimpleNamespace(item_id=item_id, restaurant_id=restaurant_id, quantity=1)

    fake_cart = SimpleNamespace(items=[line(2, 1), line(3, 2)])
    monkeypatch.setattr(order_service.cart_service, "cart_view_by_customer_service", lambda customer_id: fake_cart)

    with pytest.raises(InvalidCartError):
        order_service._get_active_cart(4)