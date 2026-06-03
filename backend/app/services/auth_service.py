from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_token, decode_token, hash_password, verify_password
from app.repositories.users import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenPair


class AuthService:
    def __init__(self, db: Session):
        self.users = UserRepository(db)

    def register(self, payload: RegisterRequest):
        if self.users.get_by_login(payload.username) or self.users.get_by_login(payload.email):
            raise HTTPException(status.HTTP_409_CONFLICT, "Логин или почта уже заняты. Используйте другие данные или войдите в существующий аккаунт.")
        role = self.users.get_role(payload.role)
        if role is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Неизвестная роль")
        return self.users.create(payload.email, payload.username, hash_password(payload.password), role)

    def login(self, payload: LoginRequest) -> TokenPair:
        user = self.users.get_by_login(payload.username)
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Неверный логин или пароль")
        return self.issue_tokens(user.id)

    def refresh(self, refresh_token: str) -> TokenPair:
        try:
            user_id = int(decode_token(refresh_token, "refresh"))
        except ValueError as exc:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Недействительный refresh token") from exc
        return self.issue_tokens(user_id)

    def issue_tokens(self, user_id: int) -> TokenPair:
        subject = str(user_id)
        return TokenPair(
            access_token=create_token(subject, "access", timedelta(minutes=settings.access_token_minutes)),
            refresh_token=create_token(subject, "refresh", timedelta(days=settings.refresh_token_days)),
        )
