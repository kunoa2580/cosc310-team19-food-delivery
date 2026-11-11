import pytest

from app.schemas.order import CheckoutCart, CheckoutCartItem
from app.services import order_service


class FakeCartEnv:
    def __init__(self):
        self.active = True
        self.cart = CheckoutCart(
            restaurant_id=1,
            items=[CheckoutCartItem(item_id=2, quantity=2)],
        )
        self.cleared = []


@pytest.fixture
def env(monkeypatch):
    fake = FakeCartEnv()
    monkeypatch.setattr(order_service, "_customer_is_active", lambda customer_id: fake.active)
    monkeypatch.setattr(order_service, "_get_active_cart", lambda customer_id: fake.cart)
    monkeypatch.setattr(order_service, "_clear_cart", lambda customer_id: fake.cleared.append(customer_id))
    return fake


def test_order_route_checkout_good(client, env):
    response = client.post("/customers/7/checkout")
    data = response.json()
    assert response.status_code == 201
    assert data["order_id"] == 1
    assert data["customer_id"] == 7
    assert data["restaurant_id"] == 1
    assert data["status"] == "placed"
    assert data["total"] == 9.98
    assert data["items"] == [
        {"item_id": 2, "name": "Iced Peach Black Tea Lemonade", "unit_price": 4.99, "quantity": 2}
    ]
    assert env.cleared == [7]


def test_order_route_checkout_empty_cart(client, env):
    env.cart = CheckoutCart(restaurant_id=1, items=[])
    response = client.post("/customers/7/checkout")
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot check out an empty cart"
    assert env.cleared == []


def test_order_route_checkout_inactive_customer(client, env):
    env.active = False
    response = client.post("/customers/7/checkout")
    assert response.status_code == 403
    assert response.json()["detail"] == "Customer 7 is not active"
    assert env.cleared == []

def test_order_route_get_by_id_good(client, env):
    created = client.post("/customers/7/checkout").json()
    response = client.get(f"/orders/{created['order_id']}")
    assert response.status_code == 200
    assert response.json() == created


def test_order_route_get_by_id_not_found(client):
    response = client.get("/orders/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Order 999 was not found"


def test_order_route_get_by_customer_good(client, env):
    first = client.post("/customers/7/checkout").json()
    second = client.post("/customers/7/checkout").json()
    response = client.get("/customers/7/orders")
    assert response.status_code == 200
    assert response.json() == [first, second]


def test_order_route_get_by_customer_none(client):
    response = client.get("/customers/999/orders")
    assert response.status_code == 200
    assert response.json() == []