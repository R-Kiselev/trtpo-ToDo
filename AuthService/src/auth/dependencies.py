from typing import Annotated, AsyncGenerator

from fastapi import Depends
from fastapi.security import HTTPBearer, OAuth2PasswordBearer

from auth.enums import RoleEnum
from auth.schemas import TokenSchema, UserPayloadSchema
from auth.service import UserService
from dependencies import SessionDep, SettingsDep
from exceptions import (
    InvalidOrExpiredTokenError,
    InvalidOrExpiredTokenHTTPError,
    NotFoundError,
    PermissionDeniedHTTPError,
    UserNotFoundHTTPError,
)
from repositories.auow import AuthorizedUnitOfWork

bearer_scheme = HTTPBearer()
AuthCredentialsDep = Annotated[OAuth2PasswordBearer, Depends(bearer_scheme)]


async def get_user_service() -> UserService:
    return UserService()


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


async def get_authorized_uow(
    session: SessionDep,
    credentials: AuthCredentialsDep,
    settings: SettingsDep,
) -> AsyncGenerator[AuthorizedUnitOfWork, None]:
    try:
        token = TokenSchema(token=credentials.credentials)
        token_payload = UserService.verify_token(token, settings)
        user_payload = UserPayloadSchema.model_validate(token_payload)

        async with AuthorizedUnitOfWork(session, user_payload) as auow:
            yield auow
    except NotFoundError:
        raise UserNotFoundHTTPError("User not found")
    except InvalidOrExpiredTokenError:
        raise InvalidOrExpiredTokenHTTPError("Invalid or expired token")


AuthorizedUOWDep = Annotated[AuthorizedUnitOfWork, Depends(get_authorized_uow)]


async def get_admin_uow(
    auow: AuthorizedUOWDep,
) -> AsyncGenerator[AuthorizedUnitOfWork, None]:
    user = auow.user
    if user.role != RoleEnum.admin:
        raise PermissionDeniedHTTPError("Not enough permissions")
    yield auow


AdminUOWDep = Annotated[AuthorizedUnitOfWork, Depends(get_admin_uow)]
