""" from types import SimpleNamespace

import pytest

from app.errors import InvalidCartError
from app.schemas.menu_item import MenuItemUpdate
from app.services import order_service
from app.services.account_service import update_customer
from app.services.menu_item_service import menu_service_update


@pytest.fixture(autouse=True)
def empty_carts(isolated_data, tmp_path):
    (tmp_path / "shopping_cart.json").write_text("[]")


def register_customer(client, email="alice@example.com"):
    response = client.post(
        "/customers",
        json={"name": "Alice", "email": email, "password": "correct-password"},
    )
    assert response.status_code == 201
    token = client.post(
        "/auth/login",
        json={"email": email, "password": "correct-password"},
    ).json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return response.json()["id"]


# Register and sign in a customer → Add items to the real shopping cart → Place order → Confirm that the order is correct.
# The shopping cart is cleared, and the order can be retrieved.
def test_checkout_with_real_cart_creates_order_and_clears_cart(client):
    customer_id = register_customer(client)
    assert client.post(f"/cart/add/{customer_id}/1/2/2").status_code == 201

    response = client.post(f"/customers/{customer_id}/checkout")
    assert response.status_code == 201
    order = response.json()
    assert order["customer_id"] == customer_id
    assert order["restaurant_id"] == 1
    assert order["total"] == 9.98
    assert order["items"] == [
        {"item_id": 2, "name": "Iced Peach Black Tea Lemonade", "unit_price": 4.99, "quantity": 2}
    ]

    assert client.get(f"/cart/view/{customer_id}").json()["items"] == []

    assert client.get(f"/orders/{order['order_id']}").json() == order


# Add an item to the cart → Change the menu price → Place order → Confirm the order uses the current menu price, not the old price stored in the cart.
def test_checkout_uses_current_menu_price_not_the_price_stored_in_cart(client):
    customer_id = register_customer(client)
    client.post(f"/cart/add/{customer_id}/1/2/2")
    assert client.get(f"/cart/view/{customer_id}").json()["items"][0]["price"] == 4.99

    menu_service_update(1, 2, MenuItemUpdate(price=6.0))

    order = client.post(f"/customers/{customer_id}/checkout").json()
    assert order["items"][0]["unit_price"] == 6.0
    assert order["total"] == 12.0


# Sign in a customer who has no active cart → Place order → Confirm it is rejected with 400 and no order is created.
def test_checkout_without_an_active_cart_is_rejected(client):
    customer_id = register_customer(client)

    response = client.post(f"/customers/{customer_id}/checkout")
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot check out an empty cart"
    assert order_service.order_service_get_by_customer(customer_id) == []


# Sign in → Add items to the cart → Deactivate the account while the session is still valid → Place order.
# Confirm it is rejected with 403, no order is created, and the cart is unchanged.
def test_checkout_by_a_deactivated_customer_is_rejected(client):
    customer_id = register_customer(client)
    client.post(f"/cart/add/{customer_id}/1/2/2")
    update_customer(customer_id, {"is_active": False})

    response = client.post(f"/customers/{customer_id}/checkout")
    assert response.status_code == 403
    assert order_service.order_service_get_by_customer(customer_id) == []
    assert len(client.get(f"/cart/view/{customer_id}").json()["items"]) == 1


# Check an active, a deactivated and an unknown account → Confirm only the active one counts as an active customer.
def test_customer_is_active_only_for_active_customer_accounts(client):
    customer_id = register_customer(client)
    assert order_service._customer_is_active(customer_id) is True

    update_customer(customer_id, {"is_active": False})
    assert order_service._customer_is_active(customer_id) is False

    assert order_service._customer_is_active(99) is False


# The cart service returns items from two restaurants (it normally rejects this) → Confirm _get_active_cart still rejects it.
def test_get_active_cart_rejects_items_from_two_restaurants(monkeypatch):
    def line(item_id, restaurant_id):
        return SimpleNamespace(item_id=item_id, restaurant_id=restaurant_id, quantity=1)

    fake_cart = SimpleNamespace(items=[line(2, 1), line(3, 2)])
    monkeypatch.setattr(order_service.cart_service, "cart_view_by_customer_service", lambda customer_id: fake_cart)

    with pytest.raises(InvalidCartError):
        order_service._get_active_cart(4) """