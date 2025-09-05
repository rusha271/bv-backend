"""merge floorplan and videos heads

Revision ID: 7b029d1d8418
Revises: add_cascade_delete_to_floorplan, add_url_column_to_videos
Create Date: 2025-09-06 02:09:51.507421

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b029d1d8418'
down_revision: Union[str, Sequence[str], None] = ('add_cascade_delete_to_floorplan', 'add_url_column_to_videos')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
