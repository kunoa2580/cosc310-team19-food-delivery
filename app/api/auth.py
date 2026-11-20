"""HTTP adapters for shared account policies and opaque bearer sessions."""
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas.account import AccountRead
from app.services.account_service import (
    Forbidden, Unauthenticated, AccountNotFound, get_account, require_role,
)
from app.services.session_service import sessions

bearer = HTTPBearer(auto_error=False)


def session_token(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> str:
    if credentials is None:
        raise Unauthenticated("Sign in required")
    return credentials.credentials


def current_account(token: str = Depends(session_token)) -> AccountRead:
    session = sessions.get(token)
    try:
        account = get_account(session.account_id)
    except AccountNotFound as error:
        raise Unauthenticated("Sign in required") from error
    if not account.is_active:
        raise Forbidden("Account is inactive")
    return account


def customer(account: AccountRead = Depends(current_account)) -> AccountRead:
    require_role(account, "customer")
    return account


def administrator(account: AccountRead = Depends(current_account)) -> AccountRead:
    require_role(account, "admin")
    return account



