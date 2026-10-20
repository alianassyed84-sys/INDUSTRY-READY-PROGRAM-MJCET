"""User ORM model — reviewer / submitter identity."""

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    """A reviewer identified by the source system's user_id."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(128), unique=True, nullable=False, index=True
    )
    user_name: Mapped[str] = mapped_column(
        String(255), nullable=False, default="Anonymous"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    reviews: Mapped[list["Review"]] = relationship(  # noqa: F821
        "Review",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
