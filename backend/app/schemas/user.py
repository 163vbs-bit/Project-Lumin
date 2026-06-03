from datetime import datetime

from pydantic import BaseModel, EmailStr


class RoleOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    avatar_url: str | None = None
    xp: int
    level: int
    streak: int
    created_at: datetime
    role: RoleOut

    model_config = {"from_attributes": True}


class LeaderboardUser(BaseModel):
    id: int
    username: str
    avatar_url: str | None = None
    xp: int
    level: int
    streak: int
