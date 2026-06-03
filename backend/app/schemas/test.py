from datetime import datetime
from pydantic import BaseModel, Field


class AnswerCreate(BaseModel):
    body: str
    is_correct: bool = False


class QuestionCreate(BaseModel):
    body: str
    kind: str = Field(pattern="^(single_choice|multiple_choice|true_false|code|timed)$")
    code_snippet: str | None = None
    time_limit_seconds: int | None = None
    points: int = 10
    answers: list[AnswerCreate]


class TestCreate(BaseModel):
    title: str
    description: str
    category_id: int
    difficulty: str = "medium"
    mode: str = "standard"
    time_limit_seconds: int | None = None
    questions: list[QuestionCreate] = Field(min_length=1)


class AnswerOut(BaseModel):
    id: int
    body: str
    is_correct: bool = False

    model_config = {"from_attributes": True}


class QuestionOut(BaseModel):
    id: int
    body: str
    kind: str
    code_snippet: str | None = None
    time_limit_seconds: int | None = None
    points: int
    position: int
    answers: list[AnswerOut]

    model_config = {"from_attributes": True}


class CategoryOut(BaseModel):
    id: int
    name: str
    description: str
    color: str

    model_config = {"from_attributes": True}


class TestOut(BaseModel):
    id: int
    title: str
    description: str
    difficulty: str
    mode: str
    time_limit_seconds: int | None = None
    is_published: bool
    created_at: datetime
    category: CategoryOut
    questions: list[QuestionOut] = []

    model_config = {"from_attributes": True}


class TestListItem(BaseModel):
    id: int
    title: str
    description: str
    difficulty: str
    mode: str
    time_limit_seconds: int | None
    category: CategoryOut
    question_count: int
    attempts_count: int


class AttemptSubmit(BaseModel):
    answers: dict[str, list[int]]
    duration_seconds: int = 0
    mode: str = "standard"


class AttemptResult(BaseModel):
    attempt_id: int
    score: int
    max_score: int
    percent: float
    xp_awarded: int
    level: int
