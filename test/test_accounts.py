import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.account import Registration
from app.repositories.account_repository import AccountRepository
from app.services import account_service as service
from app.services.session_service import sessions


@pytest.fixture
def visitor():
    sessions.sessions.clear()
    with TestClient(app) as client:
        yield client
    sessions.sessions.clear()


def register(client, email="alice@example.com"):
    return client.post("/customers", json={
        "name": "Alice", "email": email, "password": "correct-password", "role": "customer"})


def sign_in(client, email="alice@example.com"):
    response = client.post("/auth/login", json={
        "email": email, "password": "correct-password"})
    assert response.status_code == 200
    client.headers["Authorization"] = "Bearer " + response.json()["access_token"]
    return response


def test_registration_normalizes_persists_and_never_returns_credentials(visitor):
    result = register(visitor, " Alice@Example.COM ")
    assert result.status_code == 201
    data = result.json()
    assert data["email"] == "alice@example.com"
    assert data["role"] == "customer"
    assert "password" not in result.text
    stored = AccountRepository().get(data["id"])
    assert stored["password_hash"] != "correct-password"
    assert AccountRepository().get(data["id"]) == stored
    assert register(visitor).status_code == 409
    assert len(AccountRepository().list_accounts()) == 1


def test_profile_address_deactivation_and_old_session(visitor):
    account_id = register(visitor).json()["id"]
    login = sign_in(visitor)
    old_token = login.json()["access_token"]
    assert visitor.patch("/customers/me", json={"name": "New Name"}).status_code == 200
    assert visitor.put("/customers/me/address", json={"delivery_address": "123 Main St"}).status_code == 200
    profile = visitor.get("/customers/me").json()
    assert profile["name"] == "New Name"
    assert profile["delivery_address"] == "123 Main St"
    assert visitor.patch("/customers/me", json={"role": "admin"}).status_code == 422
    assert visitor.put("/customers/me/address", json={"delivery_address": "  "}).status_code == 422
    assert service.get_account(account_id).delivery_address == "123 Main St"
    assert visitor.delete("/customers/me").status_code == 204
    assert not AccountRepository().get(account_id)["is_active"]
    visitor.headers["Authorization"] = "Bearer " + old_token
    assert visitor.get("/customers/me").status_code in (401, 403)
    assert visitor.post("/auth/login", json={
        "email": "alice@example.com", "password": "correct-password"}).status_code == 403
    with pytest.raises(service.Forbidden):
        service.require_active_customer(account_id)


def test_login_failure_expiry_logout_and_required_token(visitor):
    register(visitor)
    assert visitor.get("/customers/me").status_code == 401
    assert visitor.post("/auth/login", json={
        "email": "alice@example.com", "password": "wrong"}).status_code == 401
    sign_in(visitor)
    token = visitor.headers.pop("Authorization")
    assert visitor.patch("/customers/me", json={"name": "Intruder"}).status_code == 401
    assert service.get_account(1).name == "Alice"
    visitor.headers["Authorization"] = token
    assert visitor.post("/auth/logout").status_code == 204
    assert visitor.get("/customers/me").status_code == 401


def test_other_customer_identity_cannot_be_supplied(visitor):
    register(visitor)
    other = register(visitor, "other@example.com").json()
    sign_in(visitor)
    assert visitor.patch("/customers/me", json={"id": other["id"], "name": "Stolen"}).status_code == 422
    assert service.get_account(other["id"]).name == "Alice"
    with pytest.raises(service.Forbidden):
        service.require_owner(service.get_account(1), other["id"])


def test_customer_sign_in_and_browse_restaurant_menu(visitor):
    register(visitor)
    sign_in(visitor)
    assert visitor.get("/customers/me").json()["role"] == "customer"
    restaurants = visitor.get("/restaurants")
    assert restaurants.status_code == 200
    restaurant_id = restaurants.json()[0]["id"]
    assert visitor.get(f"/restaurants/{restaurant_id}").status_code == 200
    assert visitor.get(f"/restaurant/{restaurant_id}/menu-items").status_code == 200



def test_deactivation_revokes_all_sessions_and_preserves_identity(visitor):
    register(visitor)
    sign_in(visitor)
    with TestClient(app) as other:
        sign_in(other)
        assert visitor.delete("/customers/me").status_code == 204
        assert other.get("/customers/me").status_code == 403
    new = register(visitor, "next@example.com").json()
    assert new["id"] == 2
    assert AccountRepository().get(1) is not None


