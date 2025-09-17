"""merge chakra_points and site_settings branches

Revision ID: d09b8fc44508
Revises: ac8ecc016359, add_site_settings_table
Create Date: 2025-09-15 13:34:29.302793

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd09b8fc44508'
down_revision: Union[str, Sequence[str], None] = ('ac8ecc016359', 'add_site_settings_table')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
