"""initial schema"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("goal", sa.String(), nullable=True),
        sa.Column("experience", sa.String(), nullable=True),
        sa.Column("equipment", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "user_preferences",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("avoid_exercises", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("preferred_equipment", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("custom_variations", sa.JSON(), nullable=True),
    )

    op.create_table(
        "programs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("split", sa.String(), nullable=False),
        sa.Column("program_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "workouts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("day_name", sa.String(), nullable=False),
        sa.Column("plan_json", sa.JSON(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
    )

    op.create_table(
        "workout_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("workout_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workouts.id"), nullable=False),
        sa.Column("exercise_id", sa.String(), nullable=False),
        sa.Column("actual_weight", sa.Float(), nullable=True),
        sa.Column("target_weight", sa.Float(), nullable=True),
        sa.Column("sets", sa.Integer(), nullable=True),
        sa.Column("reps", sa.String(), nullable=True),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("logged_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "exercise_guides_cache",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("exercise_name", sa.String(), nullable=False, unique=True),
        sa.Column("guide_json", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("exercise_guides_cache")
    op.drop_table("workout_logs")
    op.drop_table("workouts")
    op.drop_table("programs")
    op.drop_table("user_preferences")
    op.drop_table("users")
