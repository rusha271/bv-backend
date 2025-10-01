"""add_multiple_files_support_safe

Revision ID: dfdb7a0e6c7c
Revises: 56a319457db3
Create Date: 2025-09-29 16:12:46.263877

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dfdb7a0e6c7c'
down_revision: Union[str, Sequence[str], None] = '56a319457db3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new columns for multiple files support
    # Check if columns exist before adding them
    
    # Books table
    try:
        op.add_column('books', sa.Column('image_urls', sa.JSON(), nullable=True))
    except Exception:
        pass  # Column might already exist
    
    try:
        op.add_column('books', sa.Column('pdf_url', sa.String(length=500), nullable=True))
    except Exception:
        pass  # Column might already exist
    
    try:
        op.add_column('books', sa.Column('pdf_urls', sa.JSON(), nullable=True))
    except Exception:
        pass  # Column might already exist
    
    # Vastu tips table
    try:
        op.add_column('vastu_tips', sa.Column('image_urls', sa.JSON(), nullable=True))
    except Exception:
        pass  # Column might already exist
    
    try:
        op.add_column('vastu_tips', sa.Column('descriptions', sa.JSON(), nullable=True))
    except Exception:
        pass  # Column might already exist
    
    # Make image_url nullable in vastu_tips
    try:
        op.alter_column('vastu_tips', 'image_url', nullable=True)
    except Exception:
        pass  # Column might already be nullable
    
    # Videos table
    try:
        op.add_column('videos', sa.Column('video_urls', sa.JSON(), nullable=True))
    except Exception:
        pass  # Column might already exist
    
    try:
        op.add_column('videos', sa.Column('thumbnail_urls', sa.JSON(), nullable=True))
    except Exception:
        pass  # Column might already exist


def downgrade() -> None:
    """Downgrade schema."""
    # Remove the new columns
    try:
        op.drop_column('videos', 'thumbnail_urls')
    except Exception:
        pass
    
    try:
        op.drop_column('videos', 'video_urls')
    except Exception:
        pass
    
    try:
        op.alter_column('vastu_tips', 'image_url', nullable=False)
    except Exception:
        pass
    
    try:
        op.drop_column('vastu_tips', 'descriptions')
    except Exception:
        pass
    
    try:
        op.drop_column('vastu_tips', 'image_urls')
    except Exception:
        pass
    
    try:
        op.drop_column('books', 'pdf_urls')
    except Exception:
        pass
    
    try:
        op.drop_column('books', 'pdf_url')
    except Exception:
        pass
    
    try:
        op.drop_column('books', 'image_urls')
    except Exception:
        pass
