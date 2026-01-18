"""Add user_id and email to interviewers, summary to interview_analyses.

Revision ID: 004
Revises: 003
Create Date: 2026-01-18

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add user_id to interviewers (required for multi-tenancy)
    op.add_column(
        "interviewers",
        sa.Column("user_id", sa.UUID(), nullable=True),
    )
    op.create_index(
        "ix_interviewers_user_id",
        "interviewers",
        ["user_id"],
    )
    op.create_foreign_key(
        "fk_interviewers_user_id",
        "interviewers",
        "users",
        ["user_id"],
        ["id"],
    )

    # Add email to interviewers (optional contact info)
    op.add_column(
        "interviewers",
        sa.Column("email", sa.String(), nullable=True),
    )

    # Add summary to interview_analyses (for ML-generated summaries)
    op.add_column(
        "interview_analyses",
        sa.Column("summary", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("interview_analyses", "summary")
    op.drop_column("interviewers", "email")
    op.drop_constraint("fk_interviewers_user_id", "interviewers", type_="foreignkey")
    op.drop_index("ix_interviewers_user_id", table_name="interviewers")
    op.drop_column("interviewers", "user_id")
