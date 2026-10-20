"""CollectionJob ORM model — tracks review import/harvest job state."""

import json
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CollectionJob(Base):
    """A single review-collection run from a given source."""

    __tablename__ = "collection_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="Source identifier, e.g. 'csv_amazon'",
    )
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="pending",
        comment="pending | running | done | failed",
    )
    products_seen: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    products_inserted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reviews_seen: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reviews_inserted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    warning_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_sample: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="JSON array of up to 10 error messages sampled during the run",
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def add_error(self, message: str, max_sample: int = 10) -> None:
        """Append *message* to the error_sample JSON array (capped at max_sample)."""
        self.error_count = (self.error_count or 0) + 1
        errors: list[Any] = json.loads(self.error_sample) if self.error_sample else []
        if len(errors) < max_sample:
            errors.append(message)
            self.error_sample = json.dumps(errors)

    def to_dict(self) -> dict[str, Any]:
        """Serializable snapshot for API responses."""
        p_seen = self.products_seen or 0
        p_ins = self.products_inserted or 0
        r_seen = self.reviews_seen or 0
        r_ins = self.reviews_inserted or 0
        return {
            "id": self.id,
            "source": self.source,
            "status": self.status,
            "products_seen": p_seen,
            "products_inserted": p_ins,
            "products_skipped": max(0, p_seen - p_ins),
            "reviews_seen": r_seen,
            "reviews_inserted": r_ins,
            "reviews_skipped": max(0, r_seen - r_ins),
            "warning_count": self.warning_count or 0,
            "error_count": self.error_count or 0,
            "error_sample": json.loads(self.error_sample) if self.error_sample else [],
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
