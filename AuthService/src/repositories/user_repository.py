from typing import Optional

from sqlalchemy import select

from auth.models import Users
from auth.schemas import (
    UserCreateSchema,
    UserGetSchema,
    UserUpdatePasswordSchema,
    UserUpdateSchema,
)
from auth.utils import is_password_matching
from exceptions import (
    InvalidPasswordError,
    NotFoundError,
)
from repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[Users, UserGetSchema, UserCreateSchema, UserUpdateSchema]):
    def __init__(self, session):
        super().__init__(Users, UserGetSchema, UserCreateSchema, UserUpdateSchema, session)

    async def get_model_by_email(self, email: str) -> Optional[Users]:
        query = select(self.model).where(self.model.email == email)
        result = await self._session.execute(query)
        user = result.scalars().first()

        if not user:
            raise NotFoundError(f"User with email {email} not found")

        return user

    async def get_by_email(self, email: str) -> Optional[UserGetSchema]:
        user = await self.get_model_by_email(email)
        return self.get_schema.model_validate(user)

    async def reset_password(
        self, user_update: UserUpdatePasswordSchema
    ) -> Optional[UserGetSchema]:
        user = await self.get_model_by_email(user_update.email)

        if not is_password_matching(user_update.password, user.password):
            raise InvalidPasswordError()

        new_password_schema = UserUpdateSchema(password=user_update.new_password)
        user = await self.update_item(user, new_password_schema)

        return user
