from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.errors import InvalidCartError
from app.main import create_local_demo_app
from app.repositories.shopping_cart_repository import ShoppingCartRepository
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
    assert client.post("/cart/add/1/2/2").status_code == 201

    response = client.post(f"/customers/{customer_id}/checkout")
    assert response.status_code == 201
    order = response.json()
    assert order["customer_id"] == customer_id
    assert order["restaurant_id"] == 1
    assert order["total"] == 9.98
    assert order["items"] == [
        {"item_id": 2, "name": "Iced Peach Black Tea Lemonade", "unit_price": 4.99, "quantity": 2}
    ]

    assert client.get("/cart/view/").json()["items"] == []

    assert client.get(f"/orders/{order['order_id']}").json() == order


def test_menu_price_change_updates_existing_cart_and_checkout(client):
    customer_id = register_customer(client)
    assert client.post("/cart/add/1/2/2").status_code == 201
    original = client.get("/cart/view/").json()
    assert original["items"][0]["price"] == 4.99
    assert original["total"] == 9.98

    menu_service_update(1, 2, MenuItemUpdate(price=6.0))

    refreshed = client.get("/cart/view/").json()
    assert refreshed["cart_id"] == original["cart_id"]
    assert refreshed["items"][0]["price"] == 6.0
    assert refreshed["subtotal"] == refreshed["total"] == 12.0

    response = client.post(f"/customers/{customer_id}/checkout")
    assert response.status_code == 201
    order = response.json()
    assert order["items"][0]["unit_price"] == 6.0
    assert order["total"] == 12.0


def test_local_demo_menu_edits_update_existing_cart_and_keep_regular_route_protected(client):
    path = "/restaurant/1/menu-items/update/2"
    assert client.patch(path, json={"price": 5.0}).status_code == 401
    register_customer(client)
    assert client.patch(path, json={"price": 5.0}).status_code == 403
    assert client.post("/cart/add/1/2/2").status_code == 201

    application = create_local_demo_app()
    with TestClient(application, base_url="http://127.0.0.1", client=("127.0.0.1", 50000)) as demo:
        assert demo.get("/ui-config").json() == {"local_menu_edits": True}
        assert demo.get("/cart/view/").status_code == 401
        assert demo.patch(path, json={"price": ""}).status_code == 422
        assert demo.patch(path, json={"price": 5.0}).status_code == 200
        assert client.get("/cart/view/").json()["subtotal"] == 10.0
        assert demo.patch(path, json={"price": 10.0}).status_code == 200
        assert client.get("/cart/view/").json()["subtotal"] == 20.0

    with TestClient(application, base_url="http://127.0.0.1", client=("192.0.2.1", 50000)) as remote:
        assert remote.get("/ui-config").json() == {"local_menu_edits": False}
        assert remote.patch(path, json={"price": 15.0}).status_code == 403


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
    client.post("/cart/add/1/2/2")
    update_customer(customer_id, {"is_active": False})

    response = client.post(f"/customers/{customer_id}/checkout")
    assert response.status_code == 403
    assert order_service.order_service_get_by_customer(customer_id) == []
    assert len(ShoppingCartRepository().cart_view_by_customer_repo(customer_id)["items"]) == 1


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
        order_service._get_active_cart(4)


def test_Lucas_Liu_integration_test(client):
    buyer_id = register_customer(client, email="buyer@email.com")

    restaurants = client.get("/restaurants")
    assert restaurants.status_code == 200
    restaurant_id = restaurants.json()[0]["id"]

    menu = client.get(f"/restaurant/{restaurant_id}/menu-items")
    assert menu.status_code == 200
    item = next(entry for entry in menu.json() if entry["availability"] and entry["price"] > 0)
    item_id = item["item_id"]
    quantity = 2

    cart_response = client.post(f"/cart/add/{restaurant_id}/{item_id}/{quantity}")
    assert cart_response.status_code == 201
    cart = cart_response.json()
    assert cart["customer_id"] == buyer_id
    assert cart["items"][0]["item_id"] == item_id
    assert cart["items"][0]["quantity"] == quantity

    checkout = client.post(f"/customers/{buyer_id}/checkout")
    assert checkout.status_code == 201
    order = checkout.json()
    assert order["customer_id"] == buyer_id
    assert order["restaurant_id"] == restaurant_id
    assert order["items"][0]["item_id"] == item_id
    assert order["items"][0]["quantity"] == quantity

    history_url = f"/customers/{buyer_id}/orders"
    history = client.get(history_url)
    assert history.status_code == 200
    assert history.json() == [order]

    with TestClient(client.app) as other_client:
        other_id = register_customer(other_client, email="history-other")
        assert other_id != buyer_id
        assert other_client.get(history_url).status_code == 403

        other_history = other_client.get(f"/customers/{other_id}/orders")
        assert other_history.status_code == 200
        assert other_history.json() == []
