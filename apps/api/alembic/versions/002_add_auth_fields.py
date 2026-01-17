"""Add authentication fields to users table.

Revision ID: 002
Revises: 001
Create Date: 2026-01-17

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add hashed_password column for local auth
    op.add_column(
        "users",
        sa.Column("hashed_password", sa.VARCHAR(length=255), nullable=True),
    )

    # Add oauth_id column for OAuth provider user IDs
    op.add_column(
        "users",
        sa.Column("oauth_id", sa.VARCHAR(length=255), nullable=True),
    )
    op.create_index("ix_users_oauth_id", "users", ["oauth_id"])


def downgrade() -> None:
    op.drop_index("ix_users_oauth_id", table_name="users")
    op.drop_column("users", "oauth_id")
    op.drop_column("users", "hashed_password")
