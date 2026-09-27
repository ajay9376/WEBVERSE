"""add_studentos_academic_models

Revision ID: 17b6fd186548
Revises: 8149cf1741a0
Create Date: 2026-09-27 21:29:58.277428

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from app.models.base import Base

# revision identifiers, used by Alembic.
revision: str = '17b6fd186548'
down_revision: Union[str, Sequence[str], None] = '8149cf1741a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - ensures all models including StudentOS are created."""
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    """Downgrade schema."""
    pass
