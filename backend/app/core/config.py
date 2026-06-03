import json
import os

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str
    api_prefix: str
    database_url: str
    secret_key: str
    access_token_minutes: int
    refresh_token_days: int
    cors_origins: list[str]


def _cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS")
    if not raw:
        return ["http://localhost:5173", "http://127.0.0.1:5173"]
    try:
        value = json.loads(raw)
        return value if isinstance(value, list) else [str(value)]
    except json.JSONDecodeError:
        return [item.strip() for item in raw.split(",") if item.strip()]


settings = Settings(
    app_name=os.getenv("APP_NAME", "Lumin"),
    api_prefix=os.getenv("API_PREFIX", "/api"),
    database_url=os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@db:5432/lumin"),
    secret_key=os.getenv("SECRET_KEY", "change-me-in-production"),
    access_token_minutes=int(os.getenv("ACCESS_TOKEN_MINUTES", "30")),
    refresh_token_days=int(os.getenv("REFRESH_TOKEN_DAYS", "14")),
    cors_origins=_cors_origins(),
)
