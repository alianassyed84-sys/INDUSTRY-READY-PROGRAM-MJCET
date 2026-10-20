"""Review ORM model — a single product review from a reviewer."""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Review(Base):
    """A product review linked to a product and optionally to a user."""

    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    review_id: Mapped[str] = mapped_column(
        String(128), unique=True, nullable=False, index=True
    )
    product_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("products.product_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str | None] = mapped_column(
        String(128),
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    review_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    review_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    product: Mapped["Product"] = relationship(  # noqa: F821
        "Product", back_populates="reviews"
    )
    user: Mapped["User | None"] = relationship(  # noqa: F821
        "User", back_populates="reviews"
    )
