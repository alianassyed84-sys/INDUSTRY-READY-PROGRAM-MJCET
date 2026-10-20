"""Create core entities: products, users, reviews, collection_jobs.

Revision ID: 0001
Revises: (initial migration)
Create Date: 2026-10-18
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: str | None = None
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    # --- products ----------------------------------------------------------
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.String(length=64), nullable=False),
        sa.Column("product_name", sa.String(length=1024), nullable=False),
        sa.Column("category", sa.String(length=512), nullable=True),
        sa.Column("discounted_price", sa.Float(), nullable=True),
        sa.Column("actual_price", sa.Float(), nullable=True),
        sa.Column("discount_percentage", sa.Float(), nullable=True),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("rating_count", sa.Integer(), nullable=True),
        sa.Column("about_product", sa.Text(), nullable=True),
        sa.Column("img_link", sa.String(length=2048), nullable=True),
        sa.Column("product_link", sa.String(length=2048), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id", name="uq_products_product_id"),
    )
    op.create_index("ix_products_product_id", "products", ["product_id"], unique=True)
    op.create_index("ix_products_product_name", "products", ["product_name"])
    op.create_index("ix_products_category", "products", ["category"])
    op.create_index("ix_products_rating", "products", ["rating"])

    # --- users -------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("user_name", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_users_user_id"),
    )
    op.create_index("ix_users_user_id", "users", ["user_id"], unique=True)

    # --- reviews -----------------------------------------------------------
    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("review_id", sa.String(length=128), nullable=False),
        sa.Column("product_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=True),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("review_title", sa.Text(), nullable=True),
        sa.Column("review_content", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.product_id"],
            ondelete="CASCADE",
            name="fk_reviews_product_id",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
            ondelete="SET NULL",
            name="fk_reviews_user_id",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("review_id", name="uq_reviews_review_id"),
    )
    op.create_index("ix_reviews_review_id", "reviews", ["review_id"], unique=True)
    op.create_index("ix_reviews_product_id", "reviews", ["product_id"])
    op.create_index("ix_reviews_user_id", "reviews", ["user_id"])

    # --- collection_jobs ---------------------------------------------------
    op.create_table(
        "collection_jobs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("products_seen", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "products_inserted", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("reviews_seen", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reviews_inserted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("warning_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_sample", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_collection_jobs_source", "collection_jobs", ["source"])


def downgrade() -> None:
    op.drop_table("collection_jobs")
    op.drop_table("reviews")
    op.drop_table("users")
    op.drop_table("products")
