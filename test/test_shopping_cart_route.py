import os
from pathlib import Path
from types import SimpleNamespace
import json


import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.api.auth import customer
from app.api.routes import shopping_cart_route as cart_route_module
from app.repositories.shopping_cart_repository import ShoppingCartRepository
from app.services.shopping_cart_service import shopping_cart_service
from app.services.account_service import AccountNotFound, Forbidden
from app.schemas.shopping_cart import ShoppingCartRead
from app.errors import (
    CartItemNotFoundError,
    CartNotFoundError,
    CartRestaurantMismatchError,
    MenuItemIsNotAvailableError,
    MenuItemNotFoundError,
)

CUSTOMER_ID = 1
MISSING_CUSTOMER_ID = 999999

SERVICE = "app.services.shopping_cart_service"


class FakeCartStore:

    def __init__(self):
        self.carts = []

    def _active(self, customer_id):
        return next((c for c in self.carts
                     if c["customer_id"] == customer_id and not c["checkout_status"]), None)

    def cart_repo_get_create_cart(self, customer_id: int) -> bool:
        if self._active(customer_id) is not None:
            return False
        self.carts.append({"cart_id": len(self.carts) + 1, "customer_id": customer_id,
                           "items": [], "checkout_status": False})
        return True

    def cart_view_by_customer_repo(self, customer_id: int) -> dict | None:
        return self._active(customer_id)

    def cart_add_item_to_cart_repo(self, customer_id: int, item: dict) -> dict | None:
        cart = self._active(customer_id)
        if cart is None:
            return None
        existing = next((l for l in cart["items"] if l["item_id"] == item["item_id"]), None)
        if existing is None:
            cart["items"].append(dict(item))
        else:
            existing["quantity"] += item["quantity"]
        return cart

    def cart_edit_item_repo(self, customer_id: int, item_id: int, quantity: int) -> dict | None:
        cart = self._active(customer_id)
        if cart is None:
            return None
        found = next((l for l in cart["items"] if l["item_id"] == item_id), None)
        if found is None:
            return None
        if quantity <= 0:
            cart["items"].remove(found)
        else:
            found["quantity"] = quantity
        return cart

    def cart_empty_items_repo(self, customer_id: int) -> dict | None:
        cart = self._active(customer_id)
        if cart is None:
            return None
        cart["items"] = []
        return cart

    def cart_close_repo(self, customer_id: int) -> dict | None:
        cart = self._active(customer_id)
        if cart is None:
            return None
        cart["checkout_status"] = True
        return cart


def stub_account(customer_id=CUSTOMER_ID, is_active=True, role="customer"):
    return SimpleNamespace(id=customer_id, name="Test Customer",
                           email="test@example.com", role=role,
                           is_active=is_active, restaurant_ids=[])


def stub_customer(mocker, *, exists=True, active=True):
    if not exists:
        return mocker.patch(f"{SERVICE}.require_active_customer",
                            side_effect=AccountNotFound("Account not found"))
    if not active:
        return mocker.patch(f"{SERVICE}.require_active_customer",
                            side_effect=Forbidden("Account is inactive"))
    return mocker.patch(f"{SERVICE}.require_active_customer",
                        return_value=stub_account())


def a_menu_item(item_id=1, restaurant_id=1, name="Burger", price=10.0, availability=True):
    return SimpleNamespace(item_id=item_id, restaurant_id=restaurant_id,
                           name=name, price=price, availability=availability)


def a_cart_line(item_id=1, restaurant_id=1, name="Burger",
                price=10.0, availability=True, quantity=1):
    return {"item_id": item_id, "restaurant_id": restaurant_id, "name": name,
            "price": price, "availability": availability, "quantity": quantity}


def a_cart_read(items=None, subtotal=0.0, total=0.0):
    return ShoppingCartRead(cart_id=1, customer_id=CUSTOMER_ID, checkout_status=False,
                            items=items or [], subtotal=subtotal, total=total)


@pytest.fixture
def data_dir(isolated_data):
    return Path(os.environ["COSC310_DATA_DIR"])


@pytest.fixture
def empty_carts(data_dir):
    (data_dir / "shopping_cart.json").write_text("[]", encoding="utf-8")
    return data_dir


@pytest.fixture
def repository(empty_carts):
    return ShoppingCartRepository()


@pytest.fixture
def fake_store():
    return FakeCartStore()


@pytest.fixture
def service(fake_store, mocker):
    stub_customer(mocker)
    return shopping_cart_service(fake_store)


@pytest.fixture
def stub_customer_client(mocker):
    account = stub_account()
    app.dependency_overrides[customer] = lambda: account
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(customer, None)


def test_repo_creates_one_cart_and_refuses_a_second(repository):
    assert repository.cart_repo_get_create_cart(CUSTOMER_ID) is True
    assert repository.cart_repo_get_create_cart(CUSTOMER_ID) is False


def test_repo_merges_a_duplicate_item_instead_of_duplicating_the_line(repository):
    repository.cart_repo_get_create_cart(CUSTOMER_ID)
    repository.cart_add_item_to_cart_repo(CUSTOMER_ID, a_cart_line(quantity=2))
    cart = repository.cart_add_item_to_cart_repo(CUSTOMER_ID, a_cart_line(quantity=3))

    matching = [l for l in cart["items"] if l["item_id"] == 1]
    assert len(matching) == 1
    assert matching[0]["quantity"] == 5


def test_repo_edit_sets_the_quantity(repository):
    repository.cart_repo_get_create_cart(CUSTOMER_ID)
    repository.cart_add_item_to_cart_repo(CUSTOMER_ID, a_cart_line())

    cart = repository.cart_edit_item_repo(CUSTOMER_ID, 1, 7)
    assert cart["items"][0]["quantity"] == 7


def test_repo_edit_to_zero_removes_the_line(repository):
    repository.cart_repo_get_create_cart(CUSTOMER_ID)
    repository.cart_add_item_to_cart_repo(CUSTOMER_ID, a_cart_line())

    assert repository.cart_edit_item_repo(CUSTOMER_ID, 1, 0)["items"] == []


def test_repo_returns_none_for_an_item_not_in_the_cart(repository):
    repository.cart_repo_get_create_cart(CUSTOMER_ID)
    assert repository.cart_edit_item_repo(CUSTOMER_ID, 999, 2) is None


def test_repo_empty_clears_items_but_keeps_the_cart(repository):
    repository.cart_repo_get_create_cart(CUSTOMER_ID)
    repository.cart_add_item_to_cart_repo(CUSTOMER_ID, a_cart_line(quantity=2))

    assert repository.cart_empty_items_repo(CUSTOMER_ID)["items"] == []
    assert repository.cart_view_by_customer_repo(CUSTOMER_ID) is not None


def test_repo_close_hides_the_cart_and_allows_a_new_one(repository):
    repository.cart_repo_get_create_cart(CUSTOMER_ID)

    closed = repository.cart_close_repo(CUSTOMER_ID)
    assert closed["checkout_status"] is True
    assert repository.cart_view_by_customer_repo(CUSTOMER_ID) is None
    assert repository.cart_repo_get_create_cart(CUSTOMER_ID) is True


def test_repo_writes_survive_a_new_repository_instance(repository):
    repository.cart_repo_get_create_cart(CUSTOMER_ID)
    repository.cart_add_item_to_cart_repo(CUSTOMER_ID, a_cart_line())

    fresh = ShoppingCartRepository()
    assert any(l["item_id"] == 1
               for l in fresh.cart_view_by_customer_repo(CUSTOMER_ID)["items"])


def test_repo_one_customers_cart_does_not_disturb_another(repository):
    repository.cart_repo_get_create_cart(CUSTOMER_ID)
    repository.cart_repo_get_create_cart(CUSTOMER_ID + 1)
    repository.cart_add_item_to_cart_repo(CUSTOMER_ID, a_cart_line())

    assert repository.cart_view_by_customer_repo(CUSTOMER_ID + 1)["items"] == []


def test_service_accepts_an_active_customer(fake_store, mocker):
    stub_customer(mocker)
    mocker.patch(f"{SERVICE}.menu_service_get_by_id", return_value=a_menu_item())

    cart = shopping_cart_service(fake_store).cart_add_item_to_cart_service(
        CUSTOMER_ID, 1, 1, 1)

    assert cart.customer_id == CUSTOMER_ID


def test_service_rejects_a_customer_who_does_not_exist(fake_store, mocker):
    stub_customer(mocker, exists=False)

    with pytest.raises(AccountNotFound):
        shopping_cart_service(fake_store).cart_add_item_to_cart_service(
            MISSING_CUSTOMER_ID, 1, 1, 1)


def test_service_rejects_a_deactivated_customer(fake_store, mocker):
    stub_customer(mocker, active=False)

    with pytest.raises(Forbidden):
        shopping_cart_service(fake_store).cart_add_item_to_cart_service(
            CUSTOMER_ID, 1, 1, 1)


def test_service_checks_the_customer_before_touching_storage(fake_store, mocker):
    check = stub_customer(mocker, exists=False)

    with pytest.raises(AccountNotFound):
        shopping_cart_service(fake_store).cart_add_item_to_cart_service(
            CUSTOMER_ID, 1, 1, 1)

    check.assert_called_once_with(CUSTOMER_ID)
    assert fake_store.carts == []


def test_service_creates_the_cart_on_first_add(service, mocker):
    mocker.patch(f"{SERVICE}.menu_service_get_by_id", return_value=a_menu_item())

    cart = service.cart_add_item_to_cart_service(CUSTOMER_ID, 1, 1, 1)

    assert cart.customer_id == CUSTOMER_ID
    assert any(l.item_id == 1 for l in cart.items)


def test_service_merges_a_repeated_item(service, mocker):
    mocker.patch(f"{SERVICE}.menu_service_get_by_id", return_value=a_menu_item())
    service.cart_add_item_to_cart_service(CUSTOMER_ID, 1, 1, 2)

    cart = service.cart_add_item_to_cart_service(CUSTOMER_ID, 1, 1, 3)

    assert len(cart.items) == 1
    assert cart.items[0].quantity == 5


def test_service_rejects_an_unavailable_item(service, mocker):
    mocker.patch(f"{SERVICE}.menu_service_get_by_id",
                 return_value=a_menu_item(availability=False))

    with pytest.raises(MenuItemIsNotAvailableError):
        service.cart_add_item_to_cart_service(CUSTOMER_ID, 1, 1, 1)


def test_service_rejects_an_item_from_a_second_restaurant(service, mocker):
    menu = mocker.patch(f"{SERVICE}.menu_service_get_by_id")
    menu.return_value = a_menu_item(item_id=1, restaurant_id=1)
    service.cart_add_item_to_cart_service(CUSTOMER_ID, 1, 1, 1)

    menu.return_value = a_menu_item(item_id=9, restaurant_id=2)
    with pytest.raises(CartRestaurantMismatchError):
        service.cart_add_item_to_cart_service(CUSTOMER_ID, 2, 9, 1)

    assert len(service.cart_view_by_customer_service(CUSTOMER_ID).items) == 1


def test_service_propagates_an_unknown_menu_item(service, mocker):
    mocker.patch(f"{SERVICE}.menu_service_get_by_id",
                 side_effect=MenuItemNotFoundError("no menu item 99"))

    with pytest.raises(MenuItemNotFoundError):
        service.cart_add_item_to_cart_service(CUSTOMER_ID, 1, 99, 1)


def test_service_calculates_the_total_from_price_times_quantity(service, mocker):
    mocker.patch(f"{SERVICE}.menu_service_get_by_id", return_value=a_menu_item(price=4.99))

    cart = service.cart_add_item_to_cart_service(CUSTOMER_ID, 1, 1, 3)

    assert cart.subtotal == 14.97
    assert cart.total == 14.97
    assert service.total_cart_price_service(CUSTOMER_ID) == 14.97


def test_service_refreshes_an_existing_cart_price(service, mocker):
    menu = mocker.patch(f"{SERVICE}.menu_service_get_by_id", return_value=a_menu_item(price=4.99))
    original = service.cart_add_item_to_cart_service(CUSTOMER_ID, 1, 1, 2)
    assert original.total == 9.98

    menu.return_value = a_menu_item(price=6.0)
    refreshed = service.cart_view_by_customer_service(CUSTOMER_ID)

    assert refreshed.cart_id == original.cart_id
    assert refreshed.items[0].quantity == 2
    assert refreshed.items[0].price == 6.0
    assert refreshed.subtotal == refreshed.total == 12.0
    assert service.total_cart_price_service(CUSTOMER_ID) == 12.0
    assert service.repository.cart_view_by_customer_repo(CUSTOMER_ID)["items"][0]["price"] == 4.99


def test_service_total_is_zero_for_an_empty_cart(service, mocker):
    mocker.patch(f"{SERVICE}.menu_service_get_by_id", return_value=a_menu_item())
    service.cart_add_item_to_cart_service(CUSTOMER_ID, 1, 1, 1)

    assert service.cart_empty_items_service(CUSTOMER_ID).total == 0


def test_service_edit_rejects_an_item_not_in_the_cart(service, mocker):
    mocker.patch(f"{SERVICE}.menu_service_get_by_id", return_value=a_menu_item())
    service.cart_add_item_to_cart_service(CUSTOMER_ID, 1, 1, 1)

    with pytest.raises(CartItemNotFoundError):
        service.cart_edit_item_to_cart_service(CUSTOMER_ID, 999, 2)


def test_service_view_raises_when_there_is_no_cart(service):
    with pytest.raises(CartNotFoundError):
        service.cart_view_by_customer_service(CUSTOMER_ID)


def test_service_remove_delegates_as_a_quantity_of_zero(mocker):
    stub_customer(mocker)
    repo = mocker.Mock()
    repo.cart_edit_item_repo.return_value = {
        "cart_id": 1, "customer_id": CUSTOMER_ID, "checkout_status": False, "items": []}

    shopping_cart_service(repo).cart_remove_item_from_cart_service(CUSTOMER_ID, 5)

    repo.cart_edit_item_repo.assert_called_once_with(CUSTOMER_ID, 5, 0)


def test_service_close_marks_the_cart_checked_out(service, mocker):
    mocker.patch(f"{SERVICE}.menu_service_get_by_id", return_value=a_menu_item())
    service.cart_add_item_to_cart_service(CUSTOMER_ID, 1, 1, 1)

    assert service.cart_close_service(CUSTOMER_ID).checkout_status is True
    with pytest.raises(CartNotFoundError):
        service.cart_view_by_customer_service(CUSTOMER_ID)


def test_route_add_returns_201_and_the_service_result(stub_customer_client, mocker):
    mocker.patch.object(cart_route_module.service, "cart_add_item_to_cart_service",
                        return_value=a_cart_read([a_cart_line(quantity=2)], 20.0, 20.0))

    response = stub_customer_client.post("/cart/add/1/1/2")

    assert response.status_code == 201
    assert response.json()["total"] == 20.0


def test_route_passes_the_signed_in_account_id_to_the_service(stub_customer_client, mocker):
    add = mocker.patch.object(cart_route_module.service, "cart_add_item_to_cart_service",
                              return_value=a_cart_read())

    stub_customer_client.post("/cart/add/3/7/2")

    add.assert_called_once_with(CUSTOMER_ID, 3, 7, 2)


def test_route_maps_restaurant_mismatch_to_400(stub_customer_client, mocker):
    mocker.patch.object(cart_route_module.service, "cart_add_item_to_cart_service",
                        side_effect=CartRestaurantMismatchError("different restaurant"))

    response = stub_customer_client.post("/cart/add/1/1/1")

    assert response.status_code == 400
    assert response.json()["detail"] == "different restaurant"


def test_route_maps_unavailable_item_to_409(stub_customer_client, mocker):
    mocker.patch.object(cart_route_module.service, "cart_add_item_to_cart_service",
                        side_effect=MenuItemIsNotAvailableError("not available"))

    assert stub_customer_client.post("/cart/add/1/1/1").status_code == 409


def test_route_maps_unknown_menu_item_to_404(stub_customer_client, mocker):
    mocker.patch.object(cart_route_module.service, "cart_add_item_to_cart_service",
                        side_effect=MenuItemNotFoundError("no such item"))

    assert stub_customer_client.post("/cart/add/1/99/1").status_code == 404


def test_route_maps_missing_cart_item_to_404(stub_customer_client, mocker):
    mocker.patch.object(cart_route_module.service, "cart_edit_item_to_cart_service",
                        side_effect=CartItemNotFoundError("not in cart"))

    assert stub_customer_client.patch("/cart/edit/99/2").status_code == 404


def test_route_maps_missing_cart_to_404(stub_customer_client, mocker):
    mocker.patch.object(cart_route_module.service, "cart_view_by_customer_service",
                        side_effect=CartNotFoundError("no cart"))

    assert stub_customer_client.get("/cart/view/").status_code == 404


def test_route_view_returns_the_service_result(stub_customer_client, mocker):
    mocker.patch.object(cart_route_module.service, "cart_view_by_customer_service",
                        return_value=a_cart_read([a_cart_line(quantity=3)], 30.0, 30.0))

    response = stub_customer_client.get("/cart/view/")

    assert response.status_code == 200
    assert response.json()["items"][0]["quantity"] == 3


def test_route_clear_returns_200(stub_customer_client, mocker):
    mocker.patch.object(cart_route_module.service, "cart_empty_items_service",
                        return_value=a_cart_read())

    response = stub_customer_client.delete("/cart/clear/")

    assert response.status_code == 200
    assert response.json()["items"] == []


def test_route_total_returns_the_backend_figure(stub_customer_client, mocker):
    mocker.patch.object(cart_route_module.service, "total_cart_price_service",
                        return_value=14.97)

    response = stub_customer_client.get("/cart/total")

    assert response.status_code == 200
    assert response.json()["total_price"] == 14.97


def test_route_rejects_quantity_zero_before_reaching_the_service(stub_customer_client, mocker):
    add = mocker.patch.object(cart_route_module.service, "cart_add_item_to_cart_service")

    assert stub_customer_client.post("/cart/add/1/1/0").status_code == 422
    add.assert_not_called()


def test_route_requires_a_session(client):
    assert client.get("/cart/view/").status_code == 401


def _first_available_item(data_dir):
    items = json.loads((data_dir / "menu_items.json").read_text(encoding="utf-8"))
    for item in items:
        if item.get("availability"):
            return item
    pytest.skip("seed data has no available menu item")


def test_customer_registered_singedin_menu_cart_integration(client, data_dir, empty_carts):
    item = _first_available_item(data_dir)

    registered = client.post("/customers", json={
        "name": "Integration Tester",
        "email": "integration@example.com",
        "password": "Password123",
        "delivery_address": "UBC",
    })
    assert registered.status_code == 201

    signed_in = client.post("/auth/login", json={
        "email": "integration@example.com",
        "password": "Password123",
    })
    assert signed_in.status_code == 200
    client.headers["Authorization"] = "Bearer " + signed_in.json()["access_token"]

    added = client.post(f"/cart/add/{item['restaurant_id']}/{item['item_id']}/2")
    assert added.status_code == 201

    body = added.json()
    stored = next(l for l in body["items"] if l["item_id"] == item["item_id"])
    assert stored["name"] == item["name"]
    assert stored["price"] == item["price"]
    assert body["total"] == round(item["price"] * 2, 2)

    viewed = client.get("/cart/view/")
    assert viewed.status_code == 200
    assert viewed.json()["customer_id"] == registered.json()["id"]
    assert viewed.json()["total"] == body["total"]



def test_real_customer_menu_cart_flow_without_mocks(client, tmp_path):
    # Multi-subsystem test, no mocks: real account + real menu data + real cart repository.
    (tmp_path / "shopping_cart.json").write_text("[]")
    client.post("/customers", json={"name": "Bob", "email": "bob@example.com", "password": "correct-password"})
    token = client.post(
        "/auth/login", json={"email": "bob@example.com", "password": "correct-password"}
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    price = client.get("/restaurant/1/menu-items/2").json()["price"]

    assert client.post("/cart/add/1/2/2", headers=headers).status_code == 201
    # A second restaurant's item is rejected (one restaurant per cart).
    assert client.post("/cart/add/2/3/1", headers=headers).status_code == 400

    cart = client.get("/cart/view/", headers=headers).json()
    assert [(i["item_id"], i["quantity"]) for i in cart["items"]] == [(2, 2)]
    assert client.get("/cart/total", headers=headers).json()["total_price"] == round(price * 2, 2)
