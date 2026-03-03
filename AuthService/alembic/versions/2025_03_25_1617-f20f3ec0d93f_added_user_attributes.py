"""added user attributes

Revision ID: f20f3ec0d93f
Revises: dd8d7e30f660
Create Date: 2025-03-25 16:17:46.127024

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "f20f3ec0d93f"
down_revision: Union[str, None] = "dd8d7e30f660"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE TYPE roleenum AS ENUM ('user', 'admin')")

    op.add_column("users", sa.Column("username", sa.String(), nullable=False))
    op.add_column("users", sa.Column("email", sa.String(), nullable=False))
    op.add_column("users", sa.Column("password", sa.String(length=255), nullable=False))
    op.add_column(
        "users",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.Enum("user", "admin", name="roleenum"),
            server_default="user",
            nullable=False,
        ),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_unique_constraint(op.f("uq_users_username"), "users", ["username"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f("uq_users_username"), "users", type_="unique")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_column("users", "role")
    op.drop_column("users", "is_active")
    op.drop_column("users", "created_at")
    op.drop_column("users", "password")
    op.drop_column("users", "email")
    op.drop_column("users", "username")

    op.execute("DROP TYPE roleenum")
