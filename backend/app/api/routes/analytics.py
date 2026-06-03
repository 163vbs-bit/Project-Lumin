from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import current_user, require_teacher
from app.db.session import get_db
from app.models import Attempt, Category, Statistic, Test, User, UserProgress
from app.schemas.analytics import AnalyticsOut, CategoryPerformance, DashboardStats, PopularTest

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=AnalyticsOut)
def dashboard(user: User = Depends(current_user), db: Session = Depends(get_db)):
    total_tests = db.query(Test).count()
    attempts = db.query(Attempt).filter_by(user_id=user.id).all()
    average = round(sum(item.percent for item in attempts) / len(attempts), 2) if attempts else 0
    progress = (
        db.query(UserProgress, Category)
        .join(Category, Category.id == UserProgress.category_id)
        .filter(UserProgress.user_id == user.id)
        .all()
    )
    popular_rows = (
        db.query(Test, Category.name, func.count(Attempt.id), func.coalesce(func.avg(Attempt.percent), 0))
        .join(Category, Category.id == Test.category_id)
        .outerjoin(Attempt, Attempt.test_id == Test.id)
        .group_by(Test.id, Category.name)
        .order_by(func.count(Attempt.id).desc())
        .limit(6)
        .all()
    )
    return AnalyticsOut(
        stats=DashboardStats(tests_completed=len(attempts), average_percent=average, xp=user.xp, level=user.level, streak=user.streak, total_tests=total_tests),
        category_performance=[CategoryPerformance(category=category.name, mastery=round(row.mastery, 2), attempts=max(1, row.xp // 60)) for row, category in progress],
        popular_tests=[PopularTest(id=test.id, title=test.title, category=category, attempts=count, average_percent=round(avg, 2)) for test, category, count, avg in popular_rows],
    )


@router.get("/teacher")
def teacher_analytics(user: User = Depends(require_teacher), db: Session = Depends(get_db)):
    authored = db.query(Test).filter_by(author_id=user.id).all()
    test_ids = [test.id for test in authored]
    attempts = db.query(Attempt).filter(Attempt.test_id.in_(test_ids)).all() if test_ids else []
    return {
        "tests_created": len(authored),
        "student_attempts": len(attempts),
        "average_score": round(sum(a.percent for a in attempts) / len(attempts), 2) if attempts else 0,
        "popular_categories": db.query(Category.name, func.count(Test.id)).join(Test).filter(Test.author_id == user.id).group_by(Category.name).all(),
    }
