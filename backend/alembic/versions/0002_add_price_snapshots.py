"""Add price_snapshots table for tracking observed prices.

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-20
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    op.create_table(
        "price_snapshots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.String(length=64), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("original_price", sa.Float(), nullable=True),
        sa.Column(
            "currency", sa.String(length=8), nullable=False, server_default="INR"
        ),
        sa.Column(
            "source", sa.String(length=64), nullable=False, server_default="unknown"
        ),
        sa.Column(
            "observed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.product_id"],
            ondelete="CASCADE",
            name="fk_price_snapshots_product_id",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_price_snapshots_product_id", "price_snapshots", ["product_id"])
    op.create_index(
        "ix_price_snapshots_observed_at", "price_snapshots", ["observed_at"]
    )


def downgrade() -> None:
    op.drop_table("price_snapshots")
