"""Add guest role

Revision ID: add_guest_role_001
Revises: 8c246282c4fd
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'add_guest_role_001'
down_revision = '8c246282c4fd'
branch_labels = None
depends_on = None

def upgrade():
    # Insert guest role if it doesn't exist
    connection = op.get_bind()
    
    # Check if guest role already exists
    result = connection.execute(sa.text("SELECT id FROM roles WHERE name = 'guest'"))
    if not result.fetchone():
        connection.execute(
            sa.text("INSERT INTO roles (name, created_at, updated_at) VALUES (:name, :created_at, :updated_at)"),
            {"name": "guest", "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()}
        )
        
def downgrade():
    # Remove guest role
    connection = op.get_bind()
    connection.execute(sa.text("DELETE FROM roles WHERE name = 'guest'"))
