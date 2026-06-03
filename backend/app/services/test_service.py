from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Attempt, Statistic, Test, UserProgress
from app.repositories.tests import TestRepository
from app.schemas.test import AttemptSubmit


class TestService:
    def __init__(self, db: Session):
        self.db = db
        self.tests = TestRepository(db)

    def submit_attempt(self, user, test: Test, payload: AttemptSubmit):
        correct_by_question = {
            str(question.id): {answer.id for answer in question.answers if answer.is_correct}
            for question in test.questions
        }
        score = 0
        max_score = sum(question.points for question in test.questions)
        for question in test.questions:
            selected = set(payload.answers.get(str(question.id), []))
            if selected == correct_by_question[str(question.id)]:
                score += question.points
        percent = round((score / max_score) * 100, 2) if max_score else 0
        xp_awarded = int(score * (1.5 if payload.mode == "hardcore" else 1))

        attempt = Attempt(
            user_id=user.id,
            test_id=test.id,
            score=score,
            max_score=max_score,
            percent=percent,
            mode=payload.mode,
            duration_seconds=payload.duration_seconds,
            answers_payload=payload.answers,
        )
        user.xp += xp_awarded
        user.level = max(1, user.xp // 500 + 1)
        user.streak += 1 if percent >= 60 else 0
        self.db.add(attempt)
        self._update_stats(user.id, test.category_id, percent, xp_awarded)
        self.db.commit()
        self.db.refresh(attempt)
        return attempt, xp_awarded

    def require_author_or_teacher(self, user, test: Test) -> None:
        if user.role.name != "teacher" or test.author_id != user.id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Можно изменять только свои тесты")

    def _update_stats(self, user_id: int, category_id: int, percent: float, xp: int) -> None:
        stat = self.db.query(Statistic).filter_by(user_id=user_id, category_id=category_id).one_or_none()
        if stat is None:
            stat = Statistic(user_id=user_id, category_id=category_id, tests_completed=0, average_percent=0, best_percent=0)
            self.db.add(stat)
        stat.average_percent = ((stat.average_percent * stat.tests_completed) + percent) / (stat.tests_completed + 1)
        stat.tests_completed += 1
        stat.best_percent = max(stat.best_percent, percent)

        progress = self.db.query(UserProgress).filter_by(user_id=user_id, category_id=category_id).one_or_none()
        if progress is None:
            progress = UserProgress(user_id=user_id, category_id=category_id, xp=0, mastery=0)
            self.db.add(progress)
        progress.xp += xp
        progress.mastery = min(100, (progress.mastery * 0.75) + (percent * 0.25))
