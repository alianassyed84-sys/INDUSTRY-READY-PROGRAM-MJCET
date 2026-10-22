"""Harden database monetary storage and composite index.

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-21
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    # 1. Update products monetary columns to Numeric(12, 2)
    with op.batch_alter_table("products") as batch_op:
        batch_op.alter_column(
            "discounted_price",
            existing_type=sa.Float(),
            type_=sa.Numeric(precision=12, scale=2),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "actual_price",
            existing_type=sa.Float(),
            type_=sa.Numeric(precision=12, scale=2),
            existing_nullable=True,
        )

    # 2. Update price_snapshots monetary columns to Numeric(12, 2)
    # and add composite index
    with op.batch_alter_table("price_snapshots") as batch_op:
        batch_op.alter_column(
            "price",
            existing_type=sa.Float(),
            type_=sa.Numeric(precision=12, scale=2),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "original_price",
            existing_type=sa.Float(),
            type_=sa.Numeric(precision=12, scale=2),
            existing_nullable=True,
        )
        batch_op.create_index(
            "ix_price_snapshots_product_id_observed_at",
            ["product_id", "observed_at"],
        )


def downgrade() -> None:
    # 1. Revert price_snapshots composite index and monetary columns
    with op.batch_alter_table("price_snapshots") as batch_op:
        batch_op.drop_index("ix_price_snapshots_product_id_observed_at")
        batch_op.alter_column(
            "original_price",
            existing_type=sa.Numeric(precision=12, scale=2),
            type_=sa.Float(),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "price",
            existing_type=sa.Numeric(precision=12, scale=2),
            type_=sa.Float(),
            existing_nullable=False,
        )

    # 2. Revert products monetary columns to Float
    with op.batch_alter_table("products") as batch_op:
        batch_op.alter_column(
            "actual_price",
            existing_type=sa.Numeric(precision=12, scale=2),
            type_=sa.Float(),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "discounted_price",
            existing_type=sa.Numeric(precision=12, scale=2),
            type_=sa.Float(),
            existing_nullable=True,
        )
