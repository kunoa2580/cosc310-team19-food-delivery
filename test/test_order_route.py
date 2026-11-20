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
def signed_in(client):
    response = client.post(
        "/customers",
        json={"name": "Alice", "email": "alice@example.com", "password": "correct-password"},
    )
    customer_id = response.json()["id"]
    token = client.post(
        "/auth/login",
        json={"email": "alice@example.com", "password": "correct-password"},
    ).json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return customer_id


@pytest.fixture
def env(monkeypatch):
    fake = FakeCartEnv()
    monkeypatch.setattr(order_service, "_customer_is_active", lambda customer_id: fake.active)
    monkeypatch.setattr(order_service, "_get_active_cart", lambda customer_id: fake.cart)
    monkeypatch.setattr(order_service, "_clear_cart", lambda customer_id: fake.cleared.append(customer_id))
    return fake


def test_order_route_checkout_good(client, env, signed_in):
    response = client.post(f"/customers/{signed_in}/checkout")
    data = response.json()
    assert response.status_code == 201
    assert data["order_id"] == 1
    assert data["customer_id"] == signed_in
    assert data["restaurant_id"] == 1
    assert data["status"] == "placed"
    assert data["total"] == 9.98
    assert data["items"] == [
        {"item_id": 2, "name": "Iced Peach Black Tea Lemonade", "unit_price": 4.99, "quantity": 2}
    ]
    assert env.cleared == [signed_in]


def test_order_route_checkout_empty_cart(client, env, signed_in):
    env.cart = CheckoutCart(restaurant_id=1, items=[])
    response = client.post(f"/customers/{signed_in}/checkout")
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot check out an empty cart"
    assert env.cleared == []


def test_order_route_checkout_inactive_customer(client, env, signed_in):
    env.active = False
    response = client.post(f"/customers/{signed_in}/checkout")
    assert response.status_code == 403
    assert response.json()["detail"] == f"Customer {signed_in} is not active"
    assert env.cleared == []


def test_order_route_checkout_without_sign_in(client, env):
    response = client.post("/customers/1/checkout")
    assert response.status_code == 401
    assert env.cleared == []


def test_order_route_checkout_for_another_customer(client, env, signed_in):
    response = client.post(f"/customers/{signed_in + 1}/checkout")
    assert response.status_code == 403
    assert env.cleared == []


def test_order_route_get_by_id_good(client, env, signed_in):
    created = client.post(f"/customers/{signed_in}/checkout").json()
    response = client.get(f"/orders/{created['order_id']}")
    assert response.status_code == 200
    assert response.json() == created


def test_order_route_get_by_id_not_found(client, signed_in):
    response = client.get("/orders/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Order 999 was not found"


def test_order_route_get_by_id_without_sign_in(client, env, signed_in):
    created = client.post(f"/customers/{signed_in}/checkout").json()
    client.headers.pop("Authorization")
    response = client.get(f"/orders/{created['order_id']}")
    assert response.status_code == 401


def test_order_route_get_by_id_of_another_customer(client, env, signed_in):
    created = client.post(f"/customers/{signed_in}/checkout").json()
    client.post(
        "/customers",
        json={"name": "Bob", "email": "bob@example.com", "password": "correct-password"},
    )
    token = client.post(
        "/auth/login",
        json={"email": "bob@example.com", "password": "correct-password"},
    ).json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    response = client.get(f"/orders/{created['order_id']}")
    assert response.status_code == 403


def test_order_route_get_by_customer_good(client, env, signed_in):
    first = client.post(f"/customers/{signed_in}/checkout").json()
    second = client.post(f"/customers/{signed_in}/checkout").json()
    response = client.get(f"/customers/{signed_in}/orders")
    assert response.status_code == 200
    assert response.json() == [first, second]


def test_order_route_get_by_customer_none(client, signed_in):
    response = client.get(f"/customers/{signed_in}/orders")
    assert response.status_code == 200
    assert response.json() == []


def test_order_route_get_by_customer_without_sign_in(client, signed_in):
    client.headers.pop("Authorization")
    response = client.get(f"/customers/{signed_in}/orders")
    assert response.status_code == 401


def test_order_route_get_by_customer_unknown_customer(client, signed_in):
    response = client.get("/customers/999/orders")
    assert response.status_code == 404


def test_order_route_get_by_customer_of_another_customer(client, env, signed_in):
    client.post(f"/customers/{signed_in}/checkout")
    other = client.post(
        "/customers",
        json={"name": "Bob", "email": "bob@example.com", "password": "correct-password"},
    ).json()["id"]
    response = client.get(f"/customers/{other}/orders")
    assert response.status_code == 403