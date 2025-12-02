import uuid
from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_jwt
from app.db.models import Program, UserPreference, Workout, WorkoutLog
from app.db.schemas import (
    WorkoutFinishResponse,
    WorkoutLogRequest,
    WorkoutPlan,
    WorkoutUpdateRequest,
)
from app.db.session import get_db
from app.db.utils import ensure_user
from app.services.ai_daily import generate_daily_plan

router = APIRouter(prefix="/api/workout", tags=["workouts"])


async def _latest_program(db: AsyncSession, user_id: uuid.UUID) -> Program | None:
    result = await db.execute(
        select(Program).where(Program.user_id == user_id).order_by(Program.created_at.desc())
    )
    return result.scalars().first()


async def _user_preferences(db: AsyncSession, user_id: uuid.UUID) -> UserPreference | None:
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == user_id)
    )
    return result.scalars().first()


async def _log_history(db: AsyncSession, user_id: uuid.UUID) -> dict[str, list[dict]]:
    result = await db.execute(
        select(WorkoutLog).where(WorkoutLog.user_id == user_id).order_by(WorkoutLog.logged_at)
    )
    history: dict[str, list[dict]] = {}
    for log in result.scalars().all():
        history.setdefault(log.exercise_id, []).append(
            {"completed": log.completed, "target_weight": log.target_weight, "actual_weight": log.actual_weight}
        )
    return history


@router.get("/today", response_model=WorkoutPlan)
async def get_today_workout(
    db: AsyncSession = Depends(get_db), token: str = Depends(verify_jwt)
):
    user = await ensure_user(db, token)
    program = await _latest_program(db, user.id)
    base_program = program.program_json if program else {}

    pref_obj = await _user_preferences(db, user.id)
    preferences = pref_obj.custom_variations if pref_obj else None
    history = await _log_history(db, user.id)
    daily_plan = await generate_daily_plan(base_program, preferences, history)

    workout = Workout(
        user_id=user.id,
        day_name=daily_plan.get("day", "Day 1"),
        plan_json=daily_plan,
        date=date.today(),
    )
    db.add(workout)
    await db.commit()
    await db.refresh(workout)

    return WorkoutPlan(day=workout.day_name, exercises=daily_plan.get("exercises", []))


@router.patch("/update")
async def update_workout(
    payload: WorkoutUpdateRequest, db: AsyncSession = Depends(get_db), token: str = Depends(verify_jwt)
):
    user = await ensure_user(db, token)

    pref = await _user_preferences(db, user.id)
    if not pref:
        pref = UserPreference(user_id=user.id, avoid_exercises=[], preferred_equipment=[], custom_variations={})
        db.add(pref)

    custom_variations = pref.custom_variations or {}
    avoid_exercises = set(pref.avoid_exercises or [])

    for change in payload.changes:
        if change.action == "swap" and change.new_exercise and change.exercise_id:
            custom_variations[change.exercise_id] = change.new_exercise
            avoid_exercises.add(change.exercise_id)

    pref.custom_variations = custom_variations
    pref.avoid_exercises = sorted(avoid_exercises)
    await db.commit()

    return {"status": "updated", "changes": payload.changes, "preferences": pref.custom_variations}


@router.post("/log")
async def log_workout(
    payload: WorkoutLogRequest, db: AsyncSession = Depends(get_db), token: str = Depends(verify_jwt)
):
    user = await ensure_user(db, token)

    log = WorkoutLog(
        user_id=user.id,
        workout_id=payload.workout_id,
        exercise_id=payload.exercise_id,
        actual_weight=payload.actual_weight,
        target_weight=payload.target_weight,
        sets=payload.sets,
        reps=payload.reps,
        completed=payload.completed,
        logged_at=datetime.utcnow(),
    )
    db.add(log)
    await db.commit()
    return {"status": "logged", "log_id": str(log.id)}


@router.post("/finish", response_model=WorkoutFinishResponse)
async def finish_workout(
    workout_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_jwt),
):
    user = await ensure_user(db, token)

    current_logs = await db.execute(
        select(WorkoutLog).where(WorkoutLog.user_id == user.id, WorkoutLog.workout_id == workout_id)
    )
    logs = current_logs.scalars().all()

    progress: dict[str, str] = {}
    for log in logs:
        previous_weight = await db.execute(
            select(WorkoutLog.actual_weight)
            .where(
                WorkoutLog.user_id == user.id,
                WorkoutLog.exercise_id == log.exercise_id,
                WorkoutLog.workout_id != workout_id,
            )
            .order_by(WorkoutLog.logged_at.desc())
        )
        last_weight = previous_weight.scalars().first()
        if last_weight is not None and log.actual_weight is not None:
            delta = log.actual_weight - last_weight
            progress[log.exercise_id] = f"{delta:+.1f}kg"

    return WorkoutFinishResponse(
        message="Great work!",
        progress=progress or None,
    )
