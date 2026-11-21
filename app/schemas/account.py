"""Public account contracts; credentials never appear in AccountRead."""
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Address = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
Role = Literal["customer", "restaurant", "admin"]
MIN_PASSWORD_LENGTH = 8
UserId = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=254),
    Field(title="User ID", description="Account sign-in identifier as a plain string."),
]


class AccountInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Registration(AccountInput):
    role: Literal["customer"] = "customer"
    name: Name
    email: UserId
    password: str = Field(min_length=MIN_PASSWORD_LENGTH, max_length=128)
    delivery_address: Address | None = None

    @field_validator("email", mode="before")
    @classmethod
    def normalize_user_id(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value


class Login(AccountInput):
    email: UserId
    password: str = Field(min_length=1, max_length=128)


class ProfileUpdate(AccountInput):
    name: Name


class AddressUpdate(AccountInput):
    delivery_address: Address


class AccountRead(BaseModel):
    id: int
    name: str
    email: str = Field(title="User ID", description="Account sign-in identifier.")
    role: Role
    is_active: bool
    delivery_address: str | None = None
    restaurant_ids: list[int] = Field(default_factory=list)


class SessionRead(BaseModel):
    account: AccountRead


class LoginRead(SessionRead):
    access_token: str
    token_type: Literal["bearer"]
    expires_in: int

