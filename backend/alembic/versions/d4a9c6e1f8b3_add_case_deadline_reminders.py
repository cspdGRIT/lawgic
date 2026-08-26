"""add_case_deadline_reminders

Revision ID: d4a9c6e1f8b3
Revises: c8f3a1e7b2d9
Create Date: 2026-08-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd4a9c6e1f8b3'
down_revision: Union[str, Sequence[str], None] = 'c8f3a1e7b2d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('cases', sa.Column('deadline_date', sa.Date(), nullable=True))
    op.add_column('cases', sa.Column('deadline_reminder_sent', sa.Boolean(), nullable=False, server_default=sa.text('false')))


def downgrade() -> None:
    op.drop_column('cases', 'deadline_reminder_sent')
    op.drop_column('cases', 'deadline_date')
