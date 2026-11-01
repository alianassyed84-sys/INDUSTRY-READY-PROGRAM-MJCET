"""Add image_source, image_status, and unique index on products.img_link.

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-01
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    existing_cols = {c["name"] for c in insp.get_columns("products")}

    # 1. Add new columns if missing
    cols_to_add = []
    if "image_source" not in existing_cols:
        cols_to_add.append(sa.Column("image_source", sa.String(32), nullable=True))
    if "image_status" not in existing_cols:
        cols_to_add.append(
            sa.Column(
                "image_status",
                sa.String(32),
                nullable=False,
                server_default="none",
            )
        )

    if cols_to_add:
        with op.batch_alter_table("products") as batch_op:
            for col in cols_to_add:
                batch_op.add_column(col)

    # 2. Mark/clear Unsplash stock photos per requirement 5
    op.execute(
        sa.text(
            "UPDATE products SET img_link = NULL, image_status = 'none', image_source = NULL "
            "WHERE img_link LIKE '%unsplash%'"
        )
    )

    # 3. Deduplicate any duplicate non-null img_links per requirement 2
    op.execute(
        sa.text(
            """
            UPDATE products
            SET img_link = NULL, image_status = 'conflict'
            WHERE product_id IN (
                SELECT p2.product_id
                FROM products p1
                JOIN products p2 ON p1.img_link = p2.img_link AND p1.product_id < p2.product_id
                WHERE p1.img_link IS NOT NULL
            )
            """
        )
    )

    # 4. Create unique partial index on img_link if missing
    existing_indexes = {ix["name"] for ix in insp.get_indexes("products")}
    if "ix_products_img_link_unique" not in existing_indexes:
        with op.batch_alter_table("products") as batch_op:
            batch_op.create_index(
                "ix_products_img_link_unique",
                ["img_link"],
                unique=True,
                sqlite_where=sa.text("img_link IS NOT NULL"),
                postgresql_where=sa.text("img_link IS NOT NULL"),
            )


def downgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    existing_indexes = {ix["name"] for ix in insp.get_indexes("products")}
    existing_cols = {c["name"] for c in insp.get_columns("products")}

    with op.batch_alter_table("products") as batch_op:
        if "ix_products_img_link_unique" in existing_indexes:
            batch_op.drop_index("ix_products_img_link_unique")
        if "image_status" in existing_cols:
            batch_op.drop_column("image_status")
        if "image_source" in existing_cols:
            batch_op.drop_column("image_source")
