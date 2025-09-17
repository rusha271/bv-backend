"""Add site_settings table

Revision ID: add_site_settings_table
Revises: 282d87587006
Create Date: 2025-01-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'add_site_settings_table'
down_revision = '282d87587006'
branch_labels = None
depends_on = None


def upgrade():
    # Create site_settings table
    op.create_table('site_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('meta_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_site_settings_id'), 'site_settings', ['id'], unique=False)
    op.create_index(op.f('ix_site_settings_category'), 'site_settings', ['category'], unique=False)


def downgrade():
    # Drop site_settings table
    op.drop_index(op.f('ix_site_settings_category'), table_name='site_settings')
    op.drop_index(op.f('ix_site_settings_id'), table_name='site_settings')
    op.drop_table('site_settings')
