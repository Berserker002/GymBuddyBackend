import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    goal: Mapped[str | None]
    experience: Mapped[str | None]
    equipment: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    preferences: Mapped["UserPreference"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    programs: Mapped[list["Program"]] = relationship(back_populates="user")
    workouts: Mapped[list["Workout"]] = relationship(back_populates="user")
    logs: Mapped[list["WorkoutLog"]] = relationship(back_populates="user")
    profile: Mapped["UserProfile"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    strength_estimate: Mapped["StrengthEstimate"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )


class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True
    )
    avoid_exercises: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    preferred_equipment: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    custom_variations: Mapped[dict | None] = mapped_column(JSON)

    user: Mapped[User] = relationship(back_populates="preferences")


class Program(Base):
    __tablename__ = "programs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    split: Mapped[str] = mapped_column(String, nullable=False)
    program_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    user: Mapped[User] = relationship(back_populates="programs")


class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    day_name: Mapped[str] = mapped_column(String, nullable=False)
    plan_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship(back_populates="workouts")
    logs: Mapped[list["WorkoutLog"]] = relationship(back_populates="workout")


class WorkoutLog(Base):
    __tablename__ = "workout_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    workout_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workouts.id"), nullable=False
    )
    exercise_id: Mapped[str] = mapped_column(String, nullable=False)
    actual_weight: Mapped[float | None] = mapped_column(Float)
    target_weight: Mapped[float | None] = mapped_column(Float)
    sets: Mapped[int | None] = mapped_column(Integer)
    reps: Mapped[str | None] = mapped_column(String)
    completed: Mapped[bool] = mapped_column(Boolean, default=True)
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    user: Mapped[User] = relationship(back_populates="logs")
    workout: Mapped[Workout] = relationship(back_populates="logs")


class ExerciseGuideCache(Base):
    __tablename__ = "exercise_guides_cache"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    exercise_name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    guide_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True
    )
    gender: Mapped[str | None] = mapped_column(String)
    age: Mapped[int | None] = mapped_column(Integer)
    height_cm: Mapped[int | None] = mapped_column(Integer)
    weight_kg: Mapped[float | None] = mapped_column(Float)
    equipment: Mapped[str | None] = mapped_column(String)
    goal: Mapped[str | None] = mapped_column(String)
    training_days_per_week: Mapped[int | None] = mapped_column(Integer)

    user: Mapped[User] = relationship(back_populates="profile")


class StrengthEstimate(Base):
    __tablename__ = "strength_estimates"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True
    )
    bench_press_kg: Mapped[float | None] = mapped_column(Float)
    squat_kg: Mapped[float | None] = mapped_column(Float)
    deadlift_kg: Mapped[float | None] = mapped_column(Float)
    lat_pulldown_kg: Mapped[float | None] = mapped_column(Float)
    dumbbell_press_kg: Mapped[float | None] = mapped_column(Float)
    dumbbell_row_kg: Mapped[float | None] = mapped_column(Float)
    goblet_squat_kg: Mapped[float | None] = mapped_column(Float)
    max_pushups: Mapped[int | None] = mapped_column(Integer)
    max_pullups: Mapped[int | None] = mapped_column(Integer)
    plank_seconds: Mapped[int | None] = mapped_column(Integer)

    user: Mapped[User] = relationship(back_populates="strength_estimate")
