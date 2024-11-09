from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.infrastructure.base.patched_filter import PatchedFilter
from src.infrastructure.database.models import User


class LoginUser(BaseModel):
    login: str
    password: str


class UserTokenResult(BaseModel):
    access_token: str
    refresh_token: str


class UpdateUser(BaseModel):
    first_name: str
    last_name: str
    login: str
    email: EmailStr
    age: int
    phone_number: str = Field(examples=["89986661488", "+79986661488"])

    @field_validator("age")
    def check_age(cls, value):
        if 1 <= value <= 100:
            return value
        raise ValueError("Age must be higher then 0 and less then 101")

    @field_validator("phone_number")
    def check_number(cls, value):
        if (value.isdigit() and len(value) == 11) or (
            value[1:].isdigit() and value.startswith("+") and len(value) == 12
        ):
            return value
        raise ValueError("Invalid phone number")


class CreateUser(UpdateUser):
    password: str


class UserReturnData(CreateUser, UpdateUser):
    uuid: UUID
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class UserFilter(PatchedFilter):
    uuid: Optional[UUID] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    login: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None
    phone_number: Optional[str] = None

    class Constants(PatchedFilter.Constants):
        model = User
