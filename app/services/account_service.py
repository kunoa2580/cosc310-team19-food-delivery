"""Account rules, password verification, and shared authorization policies."""
import hashlib
import secrets
from app.repositories.account_repository import AccountRepository, account_lock
from app.schemas.account import AccountRead, Registration

repository = AccountRepository()


class AccountError(Exception):
    """Base domain error."""


class Unauthenticated(AccountError):
    pass


class Forbidden(AccountError):
    pass


class AccountConflict(AccountError):
    pass


class AccountNotFound(AccountError):
    pass


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt),
                            n=16384, r=8, p=1).hex()
    return f"scrypt:{salt}:{digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, salt, expected = stored.split(":")
        if algorithm != "scrypt":
            return False
        actual = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt),
                                n=16384, r=8, p=1).hex()
        return secrets.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def register(payload: Registration) -> AccountRead:
    return create_account(payload)


def create_account(payload: Registration, role: str = "customer",
                   restaurant_ids: list[int] | None = None) -> AccountRead:
    """Trusted provisioning only: public registration never accepts role/ownership."""
    account = {**payload.model_dump(exclude={"password"}),
               "password_hash": hash_password(payload.password), "role": role,
               "is_active": True, "restaurant_ids": restaurant_ids or []}
    with account_lock:
        accounts = repository.list_accounts()
        if any(a["email"] == payload.email for a in accounts):
            raise AccountConflict("Email is already registered")
        account["id"] = max((a["id"] for a in accounts), default=0) + 1
        public = AccountRead(**account)
        accounts.append(account)
        repository.save(accounts)
    return public


def get_account(account_id: int) -> AccountRead:
    account = repository.get(account_id)
    if account is None:
        raise AccountNotFound("Account not found")
    return AccountRead(**account)


def require_active_customer(customer_id: int) -> AccountRead:
    account = get_account(customer_id)
    require_role(account, "customer")
    return account


def require_role(account: AccountRead, role: str) -> None:
    # Reload state: a previously obtained identity must not bypass deactivation.
    current = get_account(account.id)
    if not current.is_active or current.role != role:
        raise Forbidden("Account is inactive or does not have the required role")


def require_owner(account: AccountRead, customer_id: int) -> None:
    require_role(account, "customer")
    if account.id != customer_id:
        raise Forbidden("This resource belongs to another customer")


def update_customer(customer_id: int, changes: dict) -> AccountRead:
    with account_lock:
        require_active_customer(customer_id)
        if not changes or set(changes) - {"name", "delivery_address", "is_active"}:
            raise Forbidden("Unsupported customer update")
        accounts = repository.list_accounts()
        account = next(a for a in accounts if a["id"] == customer_id)
        account.update(changes)
        repository.save(accounts)
        return AccountRead(**account)


def authenticate(email: str, password: str) -> AccountRead:
    account = next((a for a in repository.list_accounts()
                    if a["email"] == email.strip().lower()), None)
    if account is None or not verify_password(password, account["password_hash"]):
        raise Unauthenticated("Invalid email or password")
    if not account["is_active"]:
        raise Forbidden("Account is inactive")
    return AccountRead(**account)



