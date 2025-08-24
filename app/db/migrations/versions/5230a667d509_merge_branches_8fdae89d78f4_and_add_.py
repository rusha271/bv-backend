"""Merge branches 8fdae89d78f4 and add_guest_role_001

Revision ID: 5230a667d509
Revises: 8fdae89d78f4, add_guest_role_001
Create Date: 2025-08-24 17:06:25.219812

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5230a667d509'
down_revision: Union[str, Sequence[str], None] = ('8fdae89d78f4', 'add_guest_role_001')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
