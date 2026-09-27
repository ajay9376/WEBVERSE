"""add_phase4_life_admin_models

Revision ID: 4c8d9e1f2a3b
Revises: 28c7ae293451
Create Date: 2026-09-28 00:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from app.models.base import Base

# revision identifiers, used by Alembic.
revision: str = '4c8d9e1f2a3b'
down_revision: Union[str, Sequence[str], None] = '28c7ae293451'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - creates new Phase 4 Life Admin tables and updates existing ones."""
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)

    # Use batch_alter_table for SQLite compatibility on existing documents table
    try:
        with op.batch_alter_table("documents") as batch_op:
            batch_op.add_column(sa.Column("category_id", sa.String(36), nullable=True))
            batch_op.add_column(sa.Column("title", sa.String(255), nullable=True))
            batch_op.add_column(sa.Column("description", sa.Text(), nullable=True))
            batch_op.add_column(sa.Column("document_date", sa.DateTime(), nullable=True))
            batch_op.add_column(sa.Column("expiry_date", sa.DateTime(), nullable=True))
            batch_op.add_column(sa.Column("issuer", sa.String(150), nullable=True))
            batch_op.add_column(sa.Column("reference_number", sa.String(100), nullable=True))
    except Exception:
        pass

    try:
        with op.batch_alter_table("reminders") as batch_op:
            batch_op.add_column(sa.Column("status", sa.String(20), server_default="PENDING", nullable=False))
    except Exception:
        pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
