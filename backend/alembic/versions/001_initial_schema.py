"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("gender", sa.Enum("male", "female", "other", name="genderenum"), nullable=True),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("height", sa.Float(), nullable=True),
        sa.Column("goal", sa.Enum("lose", "maintain", "gain", name="goalenum"), nullable=True),
        sa.Column(
            "activity_level",
            sa.Enum("sedentary", "light", "moderate", "active", "athlete", name="activityenum"),
            nullable=True,
        ),
        sa.Column("maintenance_calories", sa.Float(), nullable=True),
        sa.Column("target_calories", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=False)

    op.create_table(
        "meals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("food_name", sa.String(length=200), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=False),
        sa.Column("calories", sa.Float(), nullable=False),
        sa.Column("protein", sa.Float(), nullable=True),
        sa.Column("carbs", sa.Float(), nullable=True),
        sa.Column("fats", sa.Float(), nullable=True),
        sa.Column(
            "meal_type",
            sa.Enum("breakfast", "lunch", "dinner", "snacks", name="mealtypeenum"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_meals_id"), "meals", ["id"], unique=False)
    op.create_index(op.f("ix_meals_user_id"), "meals", ["user_id"], unique=False)

    op.create_table(
        "daily_summaries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("total_calories", sa.Float(), nullable=False),
        sa.Column("total_protein", sa.Float(), nullable=False),
        sa.Column("total_carbs", sa.Float(), nullable=False),
        sa.Column("total_fat", sa.Float(), nullable=False),
        sa.Column("remaining_calories", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "date", name="uq_daily_summary_user_date"),
    )
    op.create_index(op.f("ix_daily_summaries_id"), "daily_summaries", ["id"], unique=False)
    op.create_index(op.f("ix_daily_summaries_user_id"), "daily_summaries", ["user_id"], unique=False)
    op.create_index(op.f("ix_daily_summaries_date"), "daily_summaries", ["date"], unique=False)

    op.create_table(
        "notification_preferences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("breakfast_enabled", sa.Boolean(), nullable=False),
        sa.Column("lunch_enabled", sa.Boolean(), nullable=False),
        sa.Column("dinner_enabled", sa.Boolean(), nullable=False),
        sa.Column("summary_enabled", sa.Boolean(), nullable=False),
        sa.Column("breakfast_time", sa.String(length=8), nullable=False),
        sa.Column("lunch_time", sa.String(length=8), nullable=False),
        sa.Column("dinner_time", sa.String(length=8), nullable=False),
        sa.Column("summary_time", sa.String(length=8), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_notification_preferences_id"), "notification_preferences", ["id"], unique=False)
    op.create_index(op.f("ix_notification_preferences_user_id"), "notification_preferences", ["user_id"], unique=True)

    op.create_table(
        "ai_insights",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("insight_type", sa.String(length=50), nullable=False),
        sa.Column("insight_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_insights_id"), "ai_insights", ["id"], unique=False)
    op.create_index(op.f("ix_ai_insights_user_id"), "ai_insights", ["user_id"], unique=False)
    op.create_index(op.f("ix_ai_insights_insight_type"), "ai_insights", ["insight_type"], unique=False)
    op.create_index(op.f("ix_ai_insights_created_at"), "ai_insights", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_table("ai_insights")
    op.drop_table("notification_preferences")
    op.drop_table("daily_summaries")
    op.drop_table("meals")
    op.drop_table("users")
