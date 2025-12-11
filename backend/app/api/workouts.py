import uuid
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
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
from app.services.progression import apply_progression_to_plan

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


async def _recent_logs(db: AsyncSession, user_id: uuid.UUID) -> list[WorkoutLog]:
    result = await db.execute(
        select(WorkoutLog).where(WorkoutLog.user_id == user_id).order_by(WorkoutLog.logged_at.desc())
    )
    return result.scalars().all()


@router.get("/today", response_model=WorkoutPlan)
async def get_today_workout(
    db: AsyncSession = Depends(get_db), token: str = Depends(verify_jwt)
):
    user = await ensure_user(db, token)
    program = await _latest_program(db, user.id)

    if program is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found. Initialize a program first.",
        )

    existing_today = await db.execute(
        select(Workout).where(Workout.user_id == user.id, Workout.date == date.today())
    )
    persisted_workout = existing_today.scalars().first()
    if persisted_workout:
        return WorkoutPlan(
            workout_id=persisted_workout.id,
            day=persisted_workout.day_name,
            exercises=persisted_workout.plan_json.get("exercises", []),
        )

    base_program = program.program_json

    pref_obj = await _user_preferences(db, user.id)
    preferences = pref_obj.custom_variations if pref_obj else None
    history_logs = await _recent_logs(db, user.id)

    daily_plan = await _build_daily_plan(base_program, preferences, history_logs, db, user.id)

    workout = Workout(
        user_id=user.id,
        day_name=daily_plan.get("day", "Day 1"),
        plan_json=daily_plan,
        date=date.today(),
    )
    db.add(workout)
    await db.commit()
    await db.refresh(workout)

    return WorkoutPlan(
        workout_id=workout.id,
        day=workout.day_name,
        exercises=daily_plan.get("exercises", []),
    )


async def _build_daily_plan(
    base_program: dict[str, dict],
    preferences: dict[str, str] | None,
    history_logs: list[WorkoutLog],
    db: AsyncSession,
    user_id: uuid.UUID,
) -> dict[str, dict]:
    if not base_program:
        return {"day": "Day 1", "exercises": []}

    days = base_program.get("days") or []
    if not days:
        return {"day": "Day 1", "exercises": []}

    workout_count = await db.execute(select(func.count()).where(Workout.user_id == user_id))
    index = workout_count.scalar_one() % len(days)
    day_plan = days[index]

    exercises = [dict(ex) for ex in day_plan.get("exercises", [])]
    for exercise in exercises:
        exercise_id = exercise.get("id")
        if preferences and exercise_id in preferences:
            exercise["id"] = preferences[exercise_id]

    progressed_plan = apply_progression_to_plan(
        {"day": day_plan.get("day", "Day 1"), "exercises": exercises}, history_logs
    )

    return progressed_plan


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

    workout = await db.get(Workout, payload.workout_id)
    if not workout or workout.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")

    if workout.started_at is None:
        workout.started_at = datetime.utcnow()

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
    await db.refresh(log)
    return {"status": "logged", "log_id": str(log.id)}


@router.post("/finish", response_model=WorkoutFinishResponse)
async def finish_workout(
    workout_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_jwt),
):
    user = await ensure_user(db, token)

    workout = await db.get(Workout, workout_id)
    if not workout or workout.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")

    if workout.finished_at is None:
        workout.finished_at = datetime.utcnow()

    current_logs = await db.execute(
        select(WorkoutLog).where(WorkoutLog.user_id == user.id, WorkoutLog.workout_id == workout_id)
    )
    logs = current_logs.scalars().all()

    progress: dict[str, str] = {}
    for log in logs:
        previous_log = await db.execute(
            select(WorkoutLog)
            .where(
                WorkoutLog.user_id == user.id,
                WorkoutLog.exercise_id == log.exercise_id,
                WorkoutLog.workout_id != workout_id,
            )
            .order_by(WorkoutLog.logged_at.desc())
            .limit(1)
        )
        last_entry = previous_log.scalars().first()
        last_weight = None
        if last_entry:
            last_weight = last_entry.actual_weight or last_entry.target_weight

        current_weight = log.actual_weight or log.target_weight
        if last_weight is not None and current_weight is not None:
            delta = current_weight - last_weight
            progress[log.exercise_id] = f"{delta:+.1f}kg"

    await db.commit()

    return WorkoutFinishResponse(
        message="Great work!",
        progress=progress or None,
    )
