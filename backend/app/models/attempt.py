from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id"), index=True)
    score: Mapped[int] = mapped_column(default=0)
    max_score: Mapped[int] = mapped_column(default=0)
    percent: Mapped[float] = mapped_column(Float, default=0)
    mode: Mapped[str] = mapped_column(String(32), default="standard")
    duration_seconds: Mapped[int] = mapped_column(default=0)
    answers_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="attempts")
    test = relationship("Test", back_populates="attempts")
