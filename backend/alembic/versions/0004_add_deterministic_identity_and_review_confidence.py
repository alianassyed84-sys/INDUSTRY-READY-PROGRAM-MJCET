"""Add deterministic identity, kind, confidence, and source polarity.

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-01
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    # 1. Update products table
    with op.batch_alter_table("products") as batch_op:
        batch_op.add_column(
            sa.Column("identity_key", sa.String(128), nullable=True)
        )
        batch_op.add_column(
            sa.Column(
                "kind",
                sa.String(32),
                nullable=False,
                server_default="product",
            )
        )
        batch_op.add_column(
            sa.Column("identification_confidence", sa.Float(), nullable=True)
        )
        batch_op.add_column(
            sa.Column(
                "is_synthetic",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("0"),
            )
        )
        batch_op.create_index("ix_products_identity_key", ["identity_key"], unique=True)
        batch_op.create_index("ix_products_kind", ["kind"])

    # 2. Update reviews table
    with op.batch_alter_table("reviews") as batch_op:
        batch_op.add_column(
            sa.Column("source_polarity", sa.String(16), nullable=True)
        )
        batch_op.add_column(
            sa.Column("product_confidence", sa.Float(), nullable=True)
        )

    # 3. Update collection_jobs table
    with op.batch_alter_table("collection_jobs") as batch_op:
        batch_op.add_column(
            sa.Column("filter_report", sa.Text(), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table("collection_jobs") as batch_op:
        batch_op.drop_column("filter_report")

    with op.batch_alter_table("reviews") as batch_op:
        batch_op.drop_column("product_confidence")
        batch_op.drop_column("source_polarity")

    with op.batch_alter_table("products") as batch_op:
        batch_op.drop_index("ix_products_kind")
        batch_op.drop_index("ix_products_identity_key")
        batch_op.drop_column("is_synthetic")
        batch_op.drop_column("identification_confidence")
        batch_op.drop_column("kind")
        batch_op.drop_column("identity_key")
