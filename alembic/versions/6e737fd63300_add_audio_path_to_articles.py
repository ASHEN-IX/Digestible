"""add audio_path to articles

Revision ID: 6e737fd63300
Revises: 8e1ee4b1a515
Create Date: 2026-01-14 23:06:10.352049

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e737fd63300'
down_revision: str = '8e1ee4b1a515'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add audio_path column to articles table
    op.add_column('articles', sa.Column('audio_path', sa.String(), nullable=True))

def downgrade() -> None:
    # Remove audio_path column from articles table
    op.drop_column('articles', 'audio_path')