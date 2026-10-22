"""PriceSnapshot ORM model — records observed prices over time for a product."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PriceSnapshot(Base):
    """An observed price data point recorded for a product."""

    __tablename__ = "price_snapshots"
    __table_args__ = (
        Index("ix_price_snapshots_product_id_observed_at", "product_id", "observed_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("products.product_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    original_price: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    currency: Mapped[str] = mapped_column(String(8), default="INR", nullable=False)
    source: Mapped[str] = mapped_column(String(64), default="unknown", nullable=False)
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    product: Mapped["Product"] = relationship(  # noqa: F821
        "Product",
        back_populates="price_snapshots",
    )
