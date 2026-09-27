"""add_phase3_finance_models

Revision ID: 28c7ae293451
Revises: 17b6fd186548
Create Date: 2026-09-27 23:07:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from app.models.base import Base

# revision identifiers, used by Alembic.
revision: str = '28c7ae293451'
down_revision: Union[str, Sequence[str], None] = '17b6fd186548'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - alters existing tables to include Phase 3 columns."""
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)

    # Use batch_alter_table for SQLite compatibility
    try:
        with op.batch_alter_table("expense_categories") as batch_op:
            batch_op.add_column(sa.Column("category_type", sa.String(20), server_default="EXPENSE", nullable=False))
            batch_op.add_column(sa.Column("is_system", sa.Boolean(), server_default=sa.text("0"), nullable=False))
    except Exception:
        pass

    try:
        with op.batch_alter_table("transactions") as batch_op:
            batch_op.add_column(sa.Column("transaction_type", sa.String(20), server_default="EXPENSE", nullable=False))
            batch_op.add_column(sa.Column("merchant", sa.String(150), nullable=True))
            batch_op.add_column(sa.Column("receipt_document_id", sa.String(36), nullable=True))
    except Exception:
        pass

    try:
        with op.batch_alter_table("budgets") as batch_op:
            batch_op.add_column(sa.Column("amount", sa.Numeric(12, 2), server_default="10000.00", nullable=False))
            batch_op.add_column(sa.Column("category_id", sa.String(36), nullable=True))
            batch_op.add_column(sa.Column("year", sa.Integer(), server_default="2026", nullable=False))
            batch_op.add_column(sa.Column("period", sa.String(7), server_default="2026-09", nullable=False))
    except Exception:
        pass

    try:
        with op.batch_alter_table("subscriptions") as batch_op:
            batch_op.add_column(sa.Column("category_id", sa.String(36), nullable=True))
            batch_op.add_column(sa.Column("payment_method", sa.String(30), server_default="UPI", nullable=False))
            batch_op.add_column(sa.Column("status", sa.String(20), server_default="ACTIVE", nullable=False))
            batch_op.add_column(sa.Column("notes", sa.Text(), nullable=True))
    except Exception:
        pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
