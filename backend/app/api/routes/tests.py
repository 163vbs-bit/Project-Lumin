from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import current_user, require_teacher
from app.db.session import get_db
from app.models import User
from app.repositories.tests import TestRepository
from app.schemas.test import AttemptResult, AttemptSubmit, CategoryOut, TestCreate, TestListItem, TestOut
from app.services.test_service import TestService

router = APIRouter(prefix="/tests", tags=["tests"])


@router.get("/categories", response_model=list[CategoryOut])
def categories(db: Session = Depends(get_db)):
    return TestRepository(db).list_categories()


@router.get("", response_model=list[TestListItem])
def list_tests(
    category: str | None = None,
    search: str | None = None,
    limit: int = Query(24, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    rows = TestRepository(db).list_tests(category, search, limit, offset)
    return [
        TestListItem(
            id=test.id,
            title=test.title,
            description=test.description,
            difficulty=test.difficulty,
            mode=test.mode,
            time_limit_seconds=test.time_limit_seconds,
            category=test.category,
            question_count=len(test.questions),
            attempts_count=len(test.attempts),
        )
        for test in rows
    ]


@router.post("", response_model=TestOut, status_code=201)
def create_test(payload: TestCreate, user: User = Depends(require_teacher), db: Session = Depends(get_db)):
    return TestRepository(db).create(payload, user.id)


@router.get("/{test_id}", response_model=TestOut)
def get_test(test_id: int, db: Session = Depends(get_db)):
    test = TestRepository(db).get(test_id)
    if test is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Тест не найден")
    return test


@router.put("/{test_id}", response_model=TestOut)
def update_test(test_id: int, payload: TestCreate, user: User = Depends(require_teacher), db: Session = Depends(get_db)):
    repo = TestRepository(db)
    test = repo.get(test_id)
    if test is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Тест не найден")
    TestService(db).require_author_or_teacher(user, test)
    return repo.update(test, payload)


@router.delete("/{test_id}", status_code=204)
def delete_test(test_id: int, user: User = Depends(require_teacher), db: Session = Depends(get_db)):
    repo = TestRepository(db)
    test = repo.get(test_id)
    if test is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Тест не найден")
    TestService(db).require_author_or_teacher(user, test)
    repo.delete(test)


@router.post("/{test_id}/attempts", response_model=AttemptResult)
def submit_attempt(test_id: int, payload: AttemptSubmit, user: User = Depends(current_user), db: Session = Depends(get_db)):
    test = TestRepository(db).get(test_id)
    if test is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Тест не найден")
    attempt, xp_awarded = TestService(db).submit_attempt(user, test, payload)
    return AttemptResult(attempt_id=attempt.id, score=attempt.score, max_score=attempt.max_score, percent=attempt.percent, xp_awarded=xp_awarded, level=user.level)
