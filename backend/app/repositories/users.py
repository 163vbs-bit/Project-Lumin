from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import Role, User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.scalar(select(User).options(joinedload(User.role)).where(User.id == user_id))

    def get_by_login(self, login: str) -> User | None:
        return self.db.scalar(select(User).options(joinedload(User.role)).where(or_(User.username == login, User.email == login)))

    def get_role(self, name: str) -> Role | None:
        return self.db.scalar(select(Role).where(Role.name == name))

    def create(self, email: str, username: str, hashed_password: str, role: Role) -> User:
        user = User(email=email, username=username, hashed_password=hashed_password, role=role)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def leaderboard(self, limit: int = 20) -> list[User]:
        return list(self.db.scalars(select(User).order_by(User.xp.desc(), User.streak.desc()).limit(limit)))
