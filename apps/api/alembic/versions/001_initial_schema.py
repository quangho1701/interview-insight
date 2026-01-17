"""Initial schema - create all tables.

Revision ID: 001
Revises:
Create Date: 2026-01-17

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("provider", sa.VARCHAR(length=20), nullable=False),
        sa.Column("email", sa.VARCHAR(length=255), nullable=False),
        sa.Column("credits", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_provider", "users", ["provider"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # Create interviewers table
    op.create_table(
        "interviewers",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.VARCHAR(length=255), nullable=False),
        sa.Column("company", sa.VARCHAR(length=255), nullable=False),
        sa.Column(
            "profile_status",
            sa.VARCHAR(length=20),
            nullable=False,
            server_default="hidden",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_interviewers_name", "interviewers", ["name"])
    op.create_index("ix_interviewers_company", "interviewers", ["company"])

    # Create interview_analyses table
    op.create_table(
        "interview_analyses",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("interviewer_id", sa.UUID(), nullable=False),
        sa.Column("sentiment_score", sa.Float(), nullable=False),
        sa.Column("metrics_json", postgresql.JSONB(), nullable=True),
        sa.Column("transcript_redacted", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["interviewer_id"], ["interviewers.id"], ondelete="CASCADE"
        ),
    )
    op.create_index("ix_interview_analyses_user_id", "interview_analyses", ["user_id"])
    op.create_index(
        "ix_interview_analyses_interviewer_id", "interview_analyses", ["interviewer_id"]
    )

    # Create processing_jobs table
    op.create_table(
        "processing_jobs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("analysis_id", sa.UUID(), nullable=True),
        sa.Column("s3_audio_key", sa.VARCHAR(length=512), nullable=False),
        sa.Column(
            "status",
            sa.VARCHAR(length=20),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["analysis_id"], ["interview_analyses.id"], ondelete="SET NULL"
        ),
    )
    op.create_index("ix_processing_jobs_user_id", "processing_jobs", ["user_id"])
    op.create_index("ix_processing_jobs_status", "processing_jobs", ["status"])


def downgrade() -> None:
    op.drop_table("processing_jobs")
    op.drop_table("interview_analyses")
    op.drop_table("interviewers")
    op.drop_table("users")
