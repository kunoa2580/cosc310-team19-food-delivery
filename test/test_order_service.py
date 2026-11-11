import pytest

from app.schemas.order import CheckoutCart, CheckoutCartItem
from app.schemas.menu_item import MenuItemUpdate
from app.schemas.restaurant import RestaurantUpdate
from app.services import order_service
from app.services.order_service import order_service_checkout
from app.services.menu_item_service import menu_service_update
from app.services.restaurant_service import restaurant_service_update
from app.errors import CheckoutCustomerInactiveError, EmptyCartError, InvalidCartError


class FakeCartEnv:
    def __init__(self):
        self.active = True
        self.cart = CheckoutCart(
            restaurant_id=1,
            items=[
                CheckoutCartItem(item_id=1, quantity=1),
                CheckoutCartItem(item_id=2, quantity=2),
            ],
        )
        self.cleared = []
        self.cart_requested = []


@pytest.fixture
def env(monkeypatch):
    fake = FakeCartEnv()

    def get_cart(customer_id):
        fake.cart_requested.append(customer_id)
        return fake.cart

    monkeypatch.setattr(order_service, "_customer_is_active", lambda customer_id: fake.active)
    monkeypatch.setattr(order_service, "_get_active_cart", get_cart)
    monkeypatch.setattr(order_service, "_clear_cart", lambda customer_id: fake.cleared.append(customer_id))
    return fake


def test_checkout_creates_order_with_current_prices(env):
    order = order_service_checkout(7)
    assert order.order_id == 1
    assert order.customer_id == 7
    assert order.restaurant_id == 1
    assert order.status == "placed"
    assert [(i.item_id, i.name, i.unit_price, i.quantity) for i in order.items] == [
        (1, "Iced Peach Green Tea Lemonade", 0.0, 1),
        (2, "Iced Peach Black Tea Lemonade", 4.99, 2),
    ]
    assert order.total == 9.98


def test_checkout_uses_price_changed_after_adding_to_cart(env):
    menu_service_update(1, 2, MenuItemUpdate(price=6.0))
    order = order_service_checkout(7)
    assert order.total == 12.0
    assert order.items[1].unit_price == 6.0


def test_order_keeps_checkout_price_when_menu_changes_later(env):
    order = order_service_checkout(7)
    menu_service_update(1, 2, MenuItemUpdate(price=20.0))
    saved = order_service.order_repo.order_repo_get_by_id(order.order_id)
    assert saved["items"][1]["unit_price"] == 4.99
    assert saved["total"] == 9.98


def test_checkout_clears_cart_only_after_order_is_saved(env, monkeypatch):
    calls = []
    real_create = order_service.order_repo.order_repo_create

    def save(record):
        calls.append("save")
        return real_create(record)

    monkeypatch.setattr(order_service.order_repo, "order_repo_create", save)
    monkeypatch.setattr(order_service, "_clear_cart", lambda customer_id: calls.append("clear"))
    order_service_checkout(7)
    assert calls == ["save", "clear"]


def test_checkout_does_not_clear_cart_when_save_fails(env, monkeypatch):
    def save(record):
        raise RuntimeError("disk error")

    monkeypatch.setattr(order_service.order_repo, "order_repo_create", save)
    with pytest.raises(RuntimeError):
        order_service_checkout(7)
    assert env.cleared == []

def test_checkout_empty_cart(env):
    env.cart = CheckoutCart(restaurant_id=1, items=[])
    with pytest.raises(EmptyCartError):
        order_service_checkout(7)
    assert env.cleared == []
    assert order_service.order_repo.order_repo_get_by_id(1) is None


def test_checkout_unavailable_item(env):
    menu_service_update(1, 2, MenuItemUpdate(availability=False))
    with pytest.raises(InvalidCartError):
        order_service_checkout(7)
    assert env.cleared == []
    assert order_service.order_repo.order_repo_get_by_id(1) is None


def test_checkout_item_from_another_restaurant(env):
    env.cart = CheckoutCart(restaurant_id=1, items=[CheckoutCartItem(item_id=3, quantity=1)])
    with pytest.raises(InvalidCartError):
        order_service_checkout(7)
    assert env.cleared == []


def test_checkout_inactive_customer(env):
    env.active = False
    with pytest.raises(CheckoutCustomerInactiveError):
        order_service_checkout(7)
    assert env.cart_requested == []
    assert env.cleared == []
    assert order_service.order_repo.order_repo_get_by_id(1) is None