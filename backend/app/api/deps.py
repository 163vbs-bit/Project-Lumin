from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models import User
from app.repositories.users import UserRepository

bearer = HTTPBearer()


def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)) -> User:
    try:
        user_id = int(decode_token(credentials.credentials, "access"))
    except ValueError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Недействительный access token") from exc
    user = UserRepository(db).get_by_id(user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Пользователь не найден")
    return user


def require_teacher(user: User = Depends(current_user)) -> User:
    if user.role.name != "teacher":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Требуется роль преподавателя")
    return user
