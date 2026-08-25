"""add_access_requests_and_access_status

Revision ID: b7e2f1c9d3a4
Revises: a1b2c3d4e5f6
Create Date: 2026-08-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b7e2f1c9d3a4'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # server_default backfills every existing row as "approved" — the app's own default
    # of "pending" (set in the ORM model) takes over for every row inserted from here on.
    op.add_column(
        'users',
        sa.Column('access_status', sa.String(length=20), nullable=False, server_default='approved'),
    )

    op.create_table(
        'access_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('amount_rupees', sa.Integer(), nullable=False, server_default='72'),
        sa.Column('utr_reference', sa.String(length=64), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('reviewed_by_user_id', sa.Integer(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewed_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_access_requests_id'), 'access_requests', ['id'], unique=False)
    op.create_index(op.f('ix_access_requests_user_id'), 'access_requests', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_access_requests_user_id'), table_name='access_requests')
    op.drop_index(op.f('ix_access_requests_id'), table_name='access_requests')
    op.drop_table('access_requests')
    op.drop_column('users', 'access_status')
