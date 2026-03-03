from sqlalchemy.ext.asyncio import AsyncSession

from repositories.user_repository import UserRepository


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def __aenter__(self) -> "UnitOfWork":
        self.user_repository = UserRepository(self._session)

        return self

    async def __aexit__(self, exc_type, exc_val, traceback):
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()
