"""add profile strength tables and workout timing

Revision ID: 0002_profile_strength
Revises: 0001_initial
Create Date: 2024-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_profile_strength"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("users", "email", existing_type=sa.String(), nullable=True)

    op.create_table(
        "user_profiles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("gender", sa.String(), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("height_cm", sa.Integer(), nullable=True),
        sa.Column("weight_kg", sa.Float(), nullable=True),
        sa.Column("equipment", sa.String(), nullable=True),
        sa.Column("goal", sa.String(), nullable=True),
        sa.Column("training_days_per_week", sa.Integer(), nullable=True),
    )

    op.create_table(
        "strength_estimates",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("bench_press_kg", sa.Float(), nullable=True),
        sa.Column("squat_kg", sa.Float(), nullable=True),
        sa.Column("deadlift_kg", sa.Float(), nullable=True),
        sa.Column("lat_pulldown_kg", sa.Float(), nullable=True),
        sa.Column("dumbbell_press_kg", sa.Float(), nullable=True),
        sa.Column("dumbbell_row_kg", sa.Float(), nullable=True),
        sa.Column("goblet_squat_kg", sa.Float(), nullable=True),
        sa.Column("max_pushups", sa.Integer(), nullable=True),
        sa.Column("max_pullups", sa.Integer(), nullable=True),
        sa.Column("plank_seconds", sa.Integer(), nullable=True),
    )

    op.add_column(
        "workouts",
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "workouts",
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("workouts", "finished_at")
    op.drop_column("workouts", "started_at")
    op.drop_table("strength_estimates")
    op.drop_table("user_profiles")
    op.alter_column("users", "email", existing_type=sa.String(), nullable=False)
