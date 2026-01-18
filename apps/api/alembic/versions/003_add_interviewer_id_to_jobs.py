"""Add interviewer_id to processing_jobs table.

Revision ID: 003
Revises: 002
Create Date: 2026-01-17

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "processing_jobs",
        sa.Column("interviewer_id", sa.UUID(), nullable=True),
    )
    op.create_index(
        "ix_processing_jobs_interviewer_id",
        "processing_jobs",
        ["interviewer_id"],
    )
    op.create_foreign_key(
        "fk_processing_jobs_interviewer_id",
        "processing_jobs",
        "interviewers",
        ["interviewer_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_processing_jobs_interviewer_id",
        "processing_jobs",
        type_="foreignkey",
    )
    op.drop_index("ix_processing_jobs_interviewer_id", table_name="processing_jobs")
    op.drop_column("processing_jobs", "interviewer_id")
