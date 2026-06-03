from sqlalchemy import ForeignKey, String, Table, Text, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

user_achievements = Table(
    "user_achievements",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("achievement_id", ForeignKey("achievements.id"), primary_key=True),
)


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(80), unique=True)
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    xp_reward: Mapped[int] = mapped_column(default=0)

    users = relationship("User", secondary=user_achievements, back_populates="achievements")
