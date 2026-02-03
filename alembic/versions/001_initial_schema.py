"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2026-02-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('preferences', sa.JSON(), nullable=False),
        sa.Column('timezone', sa.String(length=50), nullable=False),
        sa.Column('briefing_time', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('email')
    )
    
    # Create articles table
    op.create_table(
        'articles',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('url_hash', sa.String(length=64), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('url_hash')
    )
    op.create_index('ix_articles_url_hash', 'articles', ['url_hash'], unique=True)
    
    # Create user_articles junction table
    op.create_table(
        'user_articles',
        sa.Column('user_email', sa.String(length=255), nullable=False),
        sa.Column('article_id', sa.String(length=64), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ),
        sa.ForeignKeyConstraint(['user_email'], ['users.email'], ),
        sa.PrimaryKeyConstraint('user_email', 'article_id')
    )


def downgrade() -> None:
    op.drop_table('user_articles')
    op.drop_index('ix_articles_url_hash', table_name='articles')
    op.drop_table('articles')
    op.drop_table('users')
