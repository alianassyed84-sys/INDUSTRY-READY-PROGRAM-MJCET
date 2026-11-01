"""Product ORM model — an Amazon product entity."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Float, Index, Integer, Numeric, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Product(Base):
    """A product scraped or imported from a review source."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True
    )
    product_name: Mapped[str] = mapped_column(String(1024), nullable=False, index=True)
    identity_key: Mapped[str | None] = mapped_column(
        String(128), unique=True, nullable=True, index=True
    )
    kind: Mapped[str] = mapped_column(
        String(32), default="product", server_default="product", nullable=False, index=True
    )
    identification_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_synthetic: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="0", nullable=False
    )
    category: Mapped[str | None] = mapped_column(String(512), nullable=True, index=True)
    discounted_price: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    actual_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    discount_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    rating_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    about_product: Mapped[str | None] = mapped_column(Text, nullable=True)
    img_link: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    image_source: Mapped[str | None] = mapped_column(String(32), nullable=True)
    image_status: Mapped[str] = mapped_column(
        String(32), default="none", server_default="none", nullable=False
    )
    product_link: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index(
            "ix_products_img_link_unique",
            "img_link",
            unique=True,
            sqlite_where=text("img_link IS NOT NULL"),
        ),
    )

    reviews: Mapped[list["Review"]] = relationship(  # noqa: F821
        "Review",
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    price_snapshots: Mapped[list["PriceSnapshot"]] = relationship(  # noqa: F821
        "PriceSnapshot",
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
