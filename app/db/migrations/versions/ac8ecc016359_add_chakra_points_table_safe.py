"""add_chakra_points_table_safe

Revision ID: ac8ecc016359
Revises: 282d87587006
Create Date: 2025-09-10 19:40:47.693058

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac8ecc016359'
down_revision: Union[str, Sequence[str], None] = '282d87587006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Check if table exists before creating it
    connection = op.get_bind()
    
    # Check if chakra_points table exists
    result = connection.execute(sa.text("""
        SELECT COUNT(*) 
        FROM information_schema.tables 
        WHERE table_schema = DATABASE() 
        AND table_name = 'chakra_points'
    """))
    
    table_exists = result.fetchone()[0] > 0
    
    if not table_exists:
        # Create the table only if it doesn't exist
        op.create_table('chakra_points',
            sa.Column('id', sa.String(length=50), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('direction', sa.String(length=20), nullable=False),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('remedies', sa.Text(), nullable=False),
            sa.Column('is_auspicious', sa.Boolean(), nullable=True),
            sa.Column('should_avoid', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_chakra_points_id'), 'chakra_points', ['id'], unique=False)
        print("Created chakra_points table")
    else:
        print("chakra_points table already exists, skipping creation")


def downgrade() -> None:
    """Downgrade schema."""
    # Check if table exists before dropping it
    connection = op.get_bind()
    
    # Check if chakra_points table exists
    result = connection.execute(sa.text("""
        SELECT COUNT(*) 
        FROM information_schema.tables 
        WHERE table_schema = DATABASE() 
        AND table_name = 'chakra_points'
    """))
    
    table_exists = result.fetchone()[0] > 0
    
    if table_exists:
        op.drop_index(op.f('ix_chakra_points_id'), table_name='chakra_points')
        op.drop_table('chakra_points')
        print("Dropped chakra_points table")
    else:
        print("chakra_points table does not exist, skipping drop")
