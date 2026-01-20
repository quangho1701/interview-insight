"""Add clerk_id field to users table for Clerk authentication.

Revision ID: 005
Revises: d84fa060098e
Create Date: 2026-01-19

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: Union[str, None] = "d84fa060098e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add clerk_id column for Clerk authentication
    op.add_column(
        "users",
        sa.Column("clerk_id", sa.VARCHAR(length=255), nullable=True),
    )
    # Create unique index on clerk_id
    op.create_index("ix_users_clerk_id", "users", ["clerk_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_clerk_id", table_name="users")
    op.drop_column("users", "clerk_id")
