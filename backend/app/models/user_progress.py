from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserProgress(Base):
    __tablename__ = "user_progress"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), index=True)
    xp: Mapped[int] = mapped_column(default=0)
    mastery: Mapped[float] = mapped_column(Float, default=0)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
