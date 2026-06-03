from sqlalchemy import Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id", ondelete="CASCADE"), index=True)
    body: Mapped[str] = mapped_column(Text)
    kind: Mapped[str] = mapped_column(default="single_choice")
    code_snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    time_limit_seconds: Mapped[int | None] = mapped_column(nullable=True)
    points: Mapped[int] = mapped_column(default=10)
    position: Mapped[int] = mapped_column(default=0)

    test = relationship("Test", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan", order_by="Answer.id")


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), index=True)
    body: Mapped[str] = mapped_column(Text)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)

    question = relationship("Question", back_populates="answers")
