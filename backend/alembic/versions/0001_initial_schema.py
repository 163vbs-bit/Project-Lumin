"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("roles", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(32), unique=True, nullable=False))
    op.create_table("categories", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(80), unique=True, nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("color", sa.String(20), nullable=False))
    op.create_table("achievements", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("code", sa.String(80), unique=True, nullable=False), sa.Column("title", sa.String(120), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("xp_reward", sa.Integer(), default=0))
    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("email", sa.String(255), unique=True, nullable=False), sa.Column("username", sa.String(80), unique=True, nullable=False), sa.Column("hashed_password", sa.String(255), nullable=False), sa.Column("avatar_url", sa.String(500), nullable=True), sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id"), nullable=False), sa.Column("xp", sa.Integer(), default=0), sa.Column("level", sa.Integer(), default=1), sa.Column("streak", sa.Integer(), default=0), sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()))
    op.create_table("tests", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("title", sa.String(160), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("difficulty", sa.String(32), nullable=False), sa.Column("mode", sa.String(32), nullable=False), sa.Column("time_limit_seconds", sa.Integer(), nullable=True), sa.Column("is_published", sa.Boolean(), default=True), sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=False), sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()))
    op.create_table("questions", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("test_id", sa.Integer(), sa.ForeignKey("tests.id", ondelete="CASCADE"), nullable=False), sa.Column("body", sa.Text(), nullable=False), sa.Column("kind", sa.String(32), nullable=False), sa.Column("code_snippet", sa.Text(), nullable=True), sa.Column("time_limit_seconds", sa.Integer(), nullable=True), sa.Column("points", sa.Integer(), default=10), sa.Column("position", sa.Integer(), default=0))
    op.create_table("answers", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False), sa.Column("body", sa.Text(), nullable=False), sa.Column("is_correct", sa.Boolean(), default=False))
    op.create_table("attempts", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("test_id", sa.Integer(), sa.ForeignKey("tests.id"), nullable=False), sa.Column("score", sa.Integer(), default=0), sa.Column("max_score", sa.Integer(), default=0), sa.Column("percent", sa.Float(), default=0), sa.Column("mode", sa.String(32), nullable=False), sa.Column("duration_seconds", sa.Integer(), default=0), sa.Column("answers_payload", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()))
    op.create_table("statistics", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=True), sa.Column("tests_completed", sa.Integer(), default=0), sa.Column("average_percent", sa.Float(), default=0), sa.Column("best_percent", sa.Float(), default=0), sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()))
    op.create_table("user_progress", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=False), sa.Column("xp", sa.Integer(), default=0), sa.Column("mastery", sa.Float(), default=0), sa.Column("last_activity_at", sa.DateTime(), server_default=sa.func.now()))
    op.create_table("user_achievements", sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), primary_key=True), sa.Column("achievement_id", sa.Integer(), sa.ForeignKey("achievements.id"), primary_key=True))


def downgrade() -> None:
    for table in ["user_achievements", "user_progress", "statistics", "attempts", "answers", "questions", "tests", "users", "achievements", "categories", "roles"]:
        op.drop_table(table)
