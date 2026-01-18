"""make interviewer company optional

Revision ID: d84fa060098e
Revises: 004
Create Date: 2026-01-18 18:02:21.044482

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd84fa060098e'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('interviewers', 'company',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)


def downgrade() -> None:
    op.alter_column('interviewers', 'company',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
