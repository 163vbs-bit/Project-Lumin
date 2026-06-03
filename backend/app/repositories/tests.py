from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import Answer, Attempt, Category, Question, Test


class TestRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_categories(self) -> list[Category]:
        return list(self.db.scalars(select(Category).order_by(Category.name)))

    def list_tests(self, category: str | None = None, search: str | None = None, limit: int = 24, offset: int = 0) -> list[Test]:
        stmt = select(Test).options(joinedload(Test.category), joinedload(Test.questions), joinedload(Test.attempts)).where(Test.is_published.is_(True))
        if category:
            stmt = stmt.join(Test.category).where(Category.name == category)
        if search:
            stmt = stmt.where(Test.title.ilike(f"%{search}%"))
        return list(self.db.scalars(stmt.order_by(Test.created_at.desc()).limit(limit).offset(offset)).unique())

    def get(self, test_id: int) -> Test | None:
        return self.db.scalar(
            select(Test)
            .options(joinedload(Test.category), joinedload(Test.questions).joinedload(Question.answers), joinedload(Test.attempts))
            .where(Test.id == test_id)
        )

    def create(self, payload, author_id: int) -> Test:
        test = Test(
            title=payload.title,
            description=payload.description,
            category_id=payload.category_id,
            difficulty=payload.difficulty,
            mode=payload.mode,
            time_limit_seconds=payload.time_limit_seconds,
            author_id=author_id,
        )
        for index, item in enumerate(payload.questions):
            question = Question(
                body=item.body,
                kind=item.kind,
                code_snippet=item.code_snippet,
                time_limit_seconds=item.time_limit_seconds,
                points=item.points,
                position=index,
            )
            question.answers = [Answer(body=answer.body, is_correct=answer.is_correct) for answer in item.answers]
            test.questions.append(question)
        self.db.add(test)
        self.db.commit()
        self.db.refresh(test)
        return test

    def update(self, test: Test, payload) -> Test:
        test.title = payload.title
        test.description = payload.description
        test.category_id = payload.category_id
        test.difficulty = payload.difficulty
        test.mode = payload.mode
        test.time_limit_seconds = payload.time_limit_seconds
        test.questions.clear()
        self.db.flush()
        for index, item in enumerate(payload.questions):
            question = Question(
                body=item.body,
                kind=item.kind,
                code_snippet=item.code_snippet,
                time_limit_seconds=item.time_limit_seconds,
                points=item.points,
                position=index,
            )
            question.answers = [Answer(body=answer.body, is_correct=answer.is_correct) for answer in item.answers]
            test.questions.append(question)
        self.db.commit()
        self.db.refresh(test)
        return test

    def delete(self, test: Test) -> None:
        self.db.delete(test)
        self.db.commit()

    def popular(self, limit: int = 8):
        return self.db.execute(
            select(Test, func.count(Attempt.id), func.coalesce(func.avg(Attempt.percent), 0))
            .join(Test.category)
            .outerjoin(Attempt)
            .group_by(Test.id)
            .order_by(func.count(Attempt.id).desc())
            .limit(limit)
        ).all()
