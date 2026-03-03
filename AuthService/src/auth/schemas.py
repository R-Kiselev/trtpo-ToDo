from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, EmailStr

from auth.enums import RoleEnum


class Base(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserGetSchema(Base):
    id: UUID
    username: str
    email: EmailStr
    created_at: datetime
    is_active: bool
    role: str


class UserCreateSchema(Base):
    username: str
    email: EmailStr
    password: str


class UserUpdateSchema(Base):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[RoleEnum] = None
    is_active: Optional[bool] = None


class UserLoginSchema(Base):
    email: EmailStr
    password: str


class UserUpdatePasswordSchema(UserLoginSchema):
    new_password: str


class UserPayloadSchema(Base):
    id: UUID
    role: RoleEnum


class TokenSchema(Base):
    token: str


class JWTResponseSchema(Base):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


BaseModelType = TypeVar("BaseModelType", bound=Base)


class PageResponseSchema(Base, Generic[BaseModelType]):
    next_page: AnyHttpUrl
    prev_page: AnyHttpUrl
    total: int
    pages: int
    results: List[BaseModelType]
