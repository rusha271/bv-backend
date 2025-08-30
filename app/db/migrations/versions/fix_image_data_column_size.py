"""Fix image_data column size

Revision ID: fix_image_data_column_size
Revises: 5230a667d509
Create Date: 2025-08-30 13:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'fix_image_data_column_size'
down_revision: Union[str, Sequence[str], None] = '5230a667d509'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Change image_data column from BLOB to LONGBLOB to handle larger images
    op.alter_column('floorplan_analyses', 'image_data',
               existing_type=sa.LargeBinary(),
               type_=mysql.LONGBLOB(),
               existing_nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Revert back to BLOB
    op.alter_column('floorplan_analyses', 'image_data',
               existing_type=mysql.LONGBLOB(),
               type_=sa.LargeBinary(),
               existing_nullable=False)
