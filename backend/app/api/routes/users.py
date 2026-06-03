from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models import Attempt, User
from app.repositories.users import UserRepository
from app.schemas.user import LeaderboardUser, UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def profile(user: User = Depends(current_user)):
    return user


@router.get("/me/history")
def history(user: User = Depends(current_user), db: Session = Depends(get_db)):
    attempts = db.query(Attempt).filter_by(user_id=user.id).order_by(Attempt.created_at.desc()).limit(20).all()
    return [
        {
            "id": attempt.id,
            "test_id": attempt.test_id,
            "title": attempt.test.title,
            "category": attempt.test.category.name,
            "percent": attempt.percent,
            "score": attempt.score,
            "max_score": attempt.max_score,
            "created_at": attempt.created_at,
        }
        for attempt in attempts
    ]


@router.get("/leaderboard", response_model=list[LeaderboardUser])
def leaderboard(db: Session = Depends(get_db)):
    return UserRepository(db).leaderboard()
