"""Set a database default for shipment creation timestamps.

Revision ID: c3d4e5f6a7b8
Revises: 9cb2a910d796
Create Date: 2026-10-15
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "9cb2a910d796"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Preserve NULL values on legacy rows; the default applies to new inserts.
    op.alter_column(
        "shipments",
        "created_at",
        existing_type=sa.DateTime(),
        nullable=True,
        server_default=sa.text("CURRENT_TIMESTAMP"),
    )


def downgrade() -> None:
    op.alter_column(
        "shipments",
        "created_at",
        existing_type=sa.DateTime(),
        server_default=None,
    )
