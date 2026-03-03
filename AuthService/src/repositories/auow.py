from sqlalchemy.ext.asyncio import AsyncSession

from auth.schemas import UserGetSchema, UserPayloadSchema
from repositories.uow import UnitOfWork


class AuthorizedUnitOfWork(UnitOfWork):
    user: UserGetSchema

    def __init__(self, session: AsyncSession, user_payload: UserPayloadSchema):
        super().__init__(session)
        self.user_payload = user_payload

    async def __aenter__(self):
        await super().__aenter__()
        self.user = await self.user_repository.get_by_id(self.user_payload.id)

        return self
