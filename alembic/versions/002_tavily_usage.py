"""Add tavily_usage table for API rate limiting

Revision ID: 002
Revises: 001
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'tavily_usage',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('used_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tavily_usage_used_at', 'tavily_usage', ['used_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_tavily_usage_used_at', table_name='tavily_usage')
    op.drop_table('tavily_usage')
