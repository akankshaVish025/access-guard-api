from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DataAccess(Base):
    __tablename__ = "data_access"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("users.email", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    auth_token: Mapped[str | None] = mapped_column(String(128), nullable=True, unique=True, index=True)
    otp_code: Mapped[str | None] = mapped_column(String(6), nullable=True)
    otp_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    counter: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    last_access: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="access")

