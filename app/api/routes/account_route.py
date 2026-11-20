"""Customer self-service and session endpoints."""
from fastapi import APIRouter, Depends, Response
from app.api.auth import current_account, customer, session_token
from app.schemas.account import AccountRead, Registration, Login, ProfileUpdate, AddressUpdate
from app.schemas.account import LoginRead, SessionRead
from app.services import account_service as service
from app.services.session_service import sessions, SESSION_SECONDS

router = APIRouter(tags=["Accounts"], responses={
    401: {"description": "Missing, invalid, or expired session"},
    403: {"description": "Inactive account or wrong role"},
    422: {"description": "Invalid request fields; input values are not echoed"},
})


@router.post("/customers", response_model=AccountRead, status_code=201,
             responses={409: {"description": "Email is already registered"}},
             summary="Register a customer; role is always customer")
def register(body: Registration) -> AccountRead:
    return service.register(body)


@router.post("/auth/login", response_model=LoginRead, summary="Sign in and receive an opaque bearer session token")
def login(body: Login, response: Response) -> dict:
    account = service.authenticate(body.email, body.password)
    token, session = sessions.create(account.id)
    response.headers["Cache-Control"] = "no-store"
    return {"account": account.model_dump(), "access_token": token,
            "token_type": "bearer", "expires_in": SESSION_SECONDS}


@router.get("/auth/session", response_model=SessionRead, summary="Retrieve the signed-in account")
def session_info(response: Response,
                 account: AccountRead = Depends(current_account)) -> dict:
    response.headers["Cache-Control"] = "no-store"
    return {"account": account.model_dump()}


@router.post("/auth/logout", status_code=204, summary="Revoke the current session")
def logout(token: str = Depends(session_token),
           account: AccountRead = Depends(current_account)) -> None:
    sessions.remove(token)


@router.get("/customers/me", response_model=AccountRead, summary="View your customer profile")
def profile(account: AccountRead = Depends(customer)) -> AccountRead:
    return account


@router.patch("/customers/me", response_model=AccountRead, summary="Update your name")
def update_profile(body: ProfileUpdate, account: AccountRead = Depends(customer)) -> AccountRead:
    return service.update_customer(account.id, body.model_dump())


@router.put("/customers/me/address", response_model=AccountRead, summary="Update your delivery address")
def update_address(body: AddressUpdate, account: AccountRead = Depends(customer)) -> AccountRead:
    return service.update_customer(account.id, body.model_dump())


@router.delete("/customers/me", status_code=204, summary="Deactivate without deleting historical identity")
def deactivate(token: str = Depends(session_token),
               account: AccountRead = Depends(customer)) -> None:
    service.update_customer(account.id, {"is_active": False})
    sessions.remove(token)



