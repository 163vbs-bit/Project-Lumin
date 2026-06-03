from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Test(Base):
    __tablename__ = "tests"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160), index=True)
    description: Mapped[str] = mapped_column(Text)
    difficulty: Mapped[str] = mapped_column(String(32))
    mode: Mapped[str] = mapped_column(String(32), default="standard")
    time_limit_seconds: Mapped[int | None] = mapped_column(nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    category = relationship("Category", back_populates="tests")
    author = relationship("User", back_populates="tests")
    questions = relationship("Question", back_populates="test", cascade="all, delete-orphan", order_by="Question.position")
    attempts = relationship("Attempt", back_populates="test")
