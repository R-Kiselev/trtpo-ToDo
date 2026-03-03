from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Enum as sqlalchemyEnum
from sqlalchemy import String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import expression, func

from auth.enums import RoleEnum
from auth.utils import hash_password
from models import BaseModel


class Users(BaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(
        unique=True,
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        unique=True,
        nullable=False,
        index=True,
    )
    _password: Mapped[str] = mapped_column(
        String(255),
        name="password",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        server_default=expression.true(),
    )
    role: Mapped[RoleEnum] = mapped_column(
        sqlalchemyEnum(RoleEnum, name="roleenum"),
        server_default=RoleEnum.user,
    )

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, password: str):
        hashed_password = hash_password(password)
        self._password = hashed_password
