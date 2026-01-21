"""Add job_id column to interview_analyses for idempotency.

Revision ID: 006
Revises: 005
Create Date: 2026-01-21

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add job_id column for idempotency (links analysis back to processing job)
    op.add_column(
        "interview_analyses",
        sa.Column("job_id", sa.UUID(), nullable=True),
    )
    # Create unique index to enforce one analysis per job
    op.create_index(
        "ix_interview_analyses_job_id",
        "interview_analyses",
        ["job_id"],
        unique=True,
    )
    op.create_foreign_key(
        "fk_interview_analyses_job_id",
        "interview_analyses",
        "processing_jobs",
        ["job_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_interview_analyses_job_id", "interview_analyses", type_="foreignkey")
    op.drop_index("ix_interview_analyses_job_id", table_name="interview_analyses")
    op.drop_column("interview_analyses", "job_id")
