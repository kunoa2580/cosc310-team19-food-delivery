import pytest

from app.schemas.menu_item import MenuItemUpdate
from app.services import order_service
from app.services.menu_item_service import menu_service_update

#Add items to the real shopping cart → Place order → Confirm that the order is correct.
#The shopping cart is cleared, and the order can be retrieved.
@pytest.fixture(autouse=True)
def active_customer(monkeypatch):
    monkeypatch.setattr(order_service, "_customer_is_active", lambda customer_id: True)


def test_checkout_with_real_cart_creates_order_and_clears_cart(client):
    assert client.post("/cart/add/1/1/2/2").status_code == 201

    response = client.post("/customers/1/checkout")
    assert response.status_code == 201
    order = response.json()
    assert order["customer_id"] == 1
    assert order["restaurant_id"] == 1
    assert order["total"] == 9.98
    assert order["items"] == [
        {"item_id": 2, "name": "Iced Peach Black Tea Lemonade", "unit_price": 4.99, "quantity": 2}
    ]

    assert client.get("/cart/view/1").json()["items"] == []

    assert client.get(f"/orders/{order['order_id']}").json() == order

# Add an item to the cart → Change the menu price → Place order → Confirm the order uses the current menu price, not the old price stored in the cart.
def test_checkout_uses_current_menu_price_not_the_price_stored_in_cart(client):
    client.post("/cart/add/1/1/2/2")
    assert client.get("/cart/view/1").json()["items"][0]["price"] == 4.99

    menu_service_update(1, 2, MenuItemUpdate(price=6.0))

    order = client.post("/customers/1/checkout").json()
    assert order["items"][0]["unit_price"] == 6.0
    assert order["total"] == 12.0

# Add items from two restaurants to the cart → Place order → Confirm it is rejected with 400, no order is created, and the cart is unchanged.
def test_checkout_rejects_cart_with_items_from_two_restaurants(client):
    client.post("/cart/add/1/1/2/1")
    client.post("/cart/add/1/2/3/1")

    response = client.post("/customers/1/checkout")
    assert response.status_code == 400
    assert response.json()["detail"] == "Cart contains items from more than one restaurant"

    assert client.get("/customers/1/orders").json() == []
    assert len(client.get("/cart/view/1").json()["items"]) == 2