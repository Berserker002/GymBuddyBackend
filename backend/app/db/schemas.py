import uuid
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    id: uuid.UUID
    email: str

    class Config:
        orm_mode = True


class ProgramCreate(BaseModel):
    goal: str
    experience: str
    equipment: list[str]
    lifts: dict[str, float] | None = None


class ProgramResponse(BaseModel):
    id: uuid.UUID
    split: str
    program_json: dict[str, Any]
    created_at: datetime

    class Config:
        orm_mode = True


class SwapRequest(BaseModel):
    exercise_id: str
    action: str
    new_exercise: str | None = None


class WorkoutUpdateRequest(BaseModel):
    day: str
    changes: list[SwapRequest]


class WorkoutPlan(BaseModel):
    workout_id: uuid.UUID | None = None
    day: str
    exercises: list[dict[str, Any]]


class WorkoutLogRequest(BaseModel):
    workout_id: uuid.UUID
    exercise_id: str
    actual_weight: float | None = None
    target_weight: float | None = None
    sets: int | None = None
    reps: str | None = None
    completed: bool = True


class WorkoutFinishResponse(BaseModel):
    message: str
    progress: dict[str, str] | None = None


class HistoryEntry(BaseModel):
    date: date
    weight: float


class HistoryResponse(BaseModel):
    exercise: str
    data: list[HistoryEntry]


class ExerciseGuideRequest(BaseModel):
    exercise_name: str | None = Field(default=None, description="Name of the exercise")
    image_url: str | None = Field(default=None, description="Optional image URL for vision mode")


class ExerciseGuideResponse(BaseModel):
    muscles: list[str]
    steps: list[str]
    mistakes: list[str]
    metadata: dict[str, Any] | None = None
