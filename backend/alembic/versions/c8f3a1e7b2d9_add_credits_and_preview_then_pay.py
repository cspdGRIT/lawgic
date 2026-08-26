"""add_credits_and_preview_then_pay

Revision ID: c8f3a1e7b2d9
Revises: b7e2f1c9d3a4
Create Date: 2026-08-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c8f3a1e7b2d9'
down_revision: Union[str, Sequence[str], None] = 'b7e2f1c9d3a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('credit_balance', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('monthly_usage', sa.Column('lawyer_matches', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('cases', sa.Column('analysis_unlocked', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('documents', sa.Column('unlocked', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('access_requests', sa.Column('credits', sa.Integer(), nullable=False, server_default='1'))

    op.create_table(
        'credit_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('delta', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(length=30), nullable=False),
        sa.Column('feature', sa.String(length=30), nullable=True),
        sa.Column('balance_after', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_credit_transactions_id'), 'credit_transactions', ['id'], unique=False)
    op.create_index(op.f('ix_credit_transactions_user_id'), 'credit_transactions', ['user_id'], unique=False)

    # Pre-existing cases/documents predate the unlock flag entirely — they were created
    # back when their respective actions were either fully free or gated at a coarser
    # level, so grandfather them unlocked rather than retroactively hiding content
    # people already had.
    op.execute("UPDATE cases SET analysis_unlocked = true WHERE ai_analysis IS NOT NULL")
    op.execute("UPDATE documents SET unlocked = true")


def downgrade() -> None:
    op.drop_index(op.f('ix_credit_transactions_user_id'), table_name='credit_transactions')
    op.drop_index(op.f('ix_credit_transactions_id'), table_name='credit_transactions')
    op.drop_table('credit_transactions')
    op.drop_column('access_requests', 'credits')
    op.drop_column('documents', 'unlocked')
    op.drop_column('cases', 'analysis_unlocked')
    op.drop_column('monthly_usage', 'lawyer_matches')
    op.drop_column('users', 'credit_balance')
