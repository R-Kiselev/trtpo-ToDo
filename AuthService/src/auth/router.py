from typing import Literal, Optional
from uuid import UUID

from fastapi import APIRouter, Query, Request, status

from auth.dependencies import (
    AdminUOWDep,
    AuthCredentialsDep,
    AuthorizedUOWDep,
    UserServiceDep,
)
from auth.enums import RoleEnum
from auth.schemas import (
    JWTResponseSchema,
    PageResponseSchema,
    TokenSchema,
    UserCreateSchema,
    UserGetSchema,
    UserLoginSchema,
    UserUpdatePasswordSchema,
    UserUpdateSchema,
)
from exceptions import (
    AlreadyExistsError,
    AlreadyRegisteredHTTPError,
    InvalidOrExpiredTokenError,
    InvalidOrExpiredTokenHTTPError,
    NotFoundError,
    PermissionDeniedHTTPError,
    UserNotFoundHTTPError,
)
from src.dependencies import SettingsDep, UOWDep

api = APIRouter(prefix="/auth", tags=["auth"])


@api.post("/register", response_model=UserGetSchema, status_code=status.HTTP_201_CREATED)
async def user_register(
    user: UserCreateSchema,
    uow: UOWDep,
) -> UserGetSchema:
    try:
        created_user = await uow.user_repository.save(user)
    except AlreadyExistsError:
        raise AlreadyRegisteredHTTPError("User already exists")

    return created_user


@api.post("/login", status_code=status.HTTP_200_OK)
async def user_login(
    user_login_data: UserLoginSchema,
    uow: UOWDep,
    user_service: UserServiceDep,
    settings: SettingsDep,
) -> JWTResponseSchema:
    try:
        user_model = await uow.user_repository.get_model_by_email(user_login_data.email)
        return await user_service.login(user_login_data, user_model, settings)
    except NotFoundError:
        raise UserNotFoundHTTPError("User not found")
    except PermissionError as e:
        raise PermissionDeniedHTTPError(str(e))


@api.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_token(
    credentials: AuthCredentialsDep,
    user_service: UserServiceDep,
    settings: SettingsDep,
) -> JWTResponseSchema:
    token = TokenSchema(token=credentials.credentials)
    try:
        jwt_response = await user_service.refresh_token(token, settings)
        return jwt_response

    except InvalidOrExpiredTokenError:
        raise InvalidOrExpiredTokenHTTPError("Invalid or expired token")


@api.get("/users/me", response_model=UserGetSchema, status_code=status.HTTP_200_OK)
async def get_me(
    auow: AuthorizedUOWDep,
) -> UserGetSchema:
    return auow.user


@api.put("/users/password", status_code=status.HTTP_200_OK)
async def reset_password(
    user_data: UserUpdatePasswordSchema,
    auow: AuthorizedUOWDep,
) -> UserGetSchema:
    current_user = auow.user

    if current_user.role != RoleEnum.admin and current_user.email != user_data.email:
        raise PermissionDeniedHTTPError("Not enough permissions")

    return await auow.user_repository.reset_password(user_data)


@api.get("/users", response_model=PageResponseSchema, status_code=status.HTTP_200_OK)
async def get_all_users(
    request: Request,
    admin_uow: AdminUOWDep,
    page_number: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    role: RoleEnum = Query(None, alias="role"),
    sort_by: Optional[Literal["created_at", "username", "role"]] = Query(None),
    sort_order: Optional[Literal["asc", "desc"]] = Query(None),
) -> PageResponseSchema:
    user_page = await admin_uow.user_repository.get_all_with_filter_sort_pagination(
        request=request,
        page_number=page_number,
        page_size=page_size,
        role=role,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return user_page


@api.get("/users/{user_id}", response_model=UserGetSchema, status_code=status.HTTP_200_OK)
async def get_user_by_id(
    user_id: UUID,
    auow: AuthorizedUOWDep,
) -> UserGetSchema:
    current_user = auow.user

    if current_user.role != RoleEnum.admin and current_user.id != user_id:
        raise PermissionDeniedHTTPError("Not enough permissions")

    user = await auow.user_repository.get_by_id(user_id)

    return user


@api.put(
    "/users/{user_id}",
    response_model=UserGetSchema,
    status_code=status.HTTP_200_OK,
)
async def update_user(
    user_id: UUID,
    user: UserUpdateSchema,
    auow: AuthorizedUOWDep,
) -> UserGetSchema:
    current_user = auow.user

    if current_user.role != RoleEnum.admin:
        raise PermissionDeniedHTTPError("Not enough permissions")

    updated_user = await auow.user_repository.update_by_id(user_id, user)
    return updated_user


@api.delete("/users/{user_id}", response_model=UserGetSchema, status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: UUID,
    auow: AuthorizedUOWDep,
) -> UserGetSchema:
    current_user = auow.user

    if current_user.role != RoleEnum.admin and current_user.id != user_id:
        raise PermissionDeniedHTTPError("Not enough permissions")

    deleted_user = await auow.user_repository.delete_by_id(user_id)
    return deleted_user
