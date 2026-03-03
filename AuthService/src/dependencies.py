from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from database import DatabaseHelper
from exceptions import (
    ServerHTTPError,
)
from repositories.uow import UnitOfWork
from settings import Settings


def get_settings() -> Settings:
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_db_helper(settings: Settings = Depends(get_settings)) -> DatabaseHelper:
    # Parameters are ignored if the instance already exists
    return DatabaseHelper.get_instance(
        url=str(settings.postgres.url),
        echo=settings.postgres.echo,
        echo_pool=settings.postgres.echo_pool,
        pool_size=settings.postgres.pool_size,
        max_overflow=settings.postgres.max_overflow,
    )


async def get_session(
    db_helper: DatabaseHelper = Depends(get_db_helper),
) -> AsyncGenerator[AsyncSession, None]:
    try:
        async with db_helper.session_maker() as session:
            yield session
    except SQLAlchemyError as e:
        raise ServerHTTPError(f"Failed to get session: {str(e)}")


SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_uow(
    session: SessionDep,
) -> AsyncGenerator[UnitOfWork, None]:
    async with UnitOfWork(session) as uow:
        yield uow


UOWDep = Annotated[UnitOfWork, Depends(get_uow)]
