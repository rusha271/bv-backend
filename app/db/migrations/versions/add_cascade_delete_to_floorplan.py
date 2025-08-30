"""Add cascade delete to floorplan_analyses

Revision ID: add_cascade_delete_to_floorplan
Revises: fix_image_data_column_size
Create Date: 2025-08-30 13:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_cascade_delete_to_floorplan'
down_revision: Union[str, Sequence[str], None] = 'fix_image_data_column_size'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop the existing foreign key constraint
    op.drop_constraint('floorplan_analyses_ibfk_2', 'floorplan_analyses', type_='foreignkey')
    
    # Add the foreign key constraint with CASCADE delete
    op.create_foreign_key(
        'floorplan_analyses_ibfk_2',
        'floorplan_analyses',
        'files',
        ['file_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the CASCADE foreign key constraint
    op.drop_constraint('floorplan_analyses_ibfk_2', 'floorplan_analyses', type_='foreignkey')
    
    # Add back the original foreign key constraint without CASCADE
    op.create_foreign_key(
        'floorplan_analyses_ibfk_2',
        'floorplan_analyses',
        'files',
        ['file_id'],
        ['id']
    )
