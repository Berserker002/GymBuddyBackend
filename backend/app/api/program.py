import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_jwt
from app.db.models import Program, StrengthEstimate, UserProfile
from app.db.schemas import ProgramCreate, ProgramResponse
from app.db.session import get_db
from app.db.utils import ensure_user
from app.services.ai_program import generate_program

router = APIRouter(prefix="/api/program", tags=["program"])


@router.post("/init", response_model=ProgramResponse)
async def init_program(
    payload: ProgramCreate,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_jwt),
):
    user = await ensure_user(db, token)
    await _upsert_profile(db, user.id, payload)
    await _upsert_strength_estimates(db, user.id, payload.lifts)

    program_json = await generate_program(payload)
    program = Program(user_id=user.id, split=program_json["split"], program_json=program_json)
    db.add(program)
    await db.commit()
    await db.refresh(program)
    return program


async def _upsert_profile(db: AsyncSession, user_id: uuid.UUID, payload: ProgramCreate) -> None:
    profile = await db.get(UserProfile, user_id)
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)

    profile.gender = payload.gender
    profile.age = payload.age
    profile.height_cm = payload.height_cm
    profile.weight_kg = payload.weight_kg
    profile.equipment = payload.equipment[0] if payload.equipment else None
    profile.goal = payload.goal
    profile.training_days_per_week = payload.training_days_per_week
    await db.commit()


async def _upsert_strength_estimates(
    db: AsyncSession, user_id: uuid.UUID, lifts: dict[str, float] | None
) -> None:
    if lifts is None:
        return

    estimates = await db.get(StrengthEstimate, user_id)
    if not estimates:
        estimates = StrengthEstimate(user_id=user_id)
        db.add(estimates)

    estimates.bench_press_kg = lifts.get("bench") or lifts.get("bench_press")
    estimates.squat_kg = lifts.get("squat") or lifts.get("back_squat")
    estimates.deadlift_kg = lifts.get("deadlift")
    estimates.lat_pulldown_kg = lifts.get("lat_pulldown")
    estimates.dumbbell_press_kg = lifts.get("dumbbell_press")
    estimates.dumbbell_row_kg = lifts.get("dumbbell_row")
    estimates.goblet_squat_kg = lifts.get("goblet_squat")
    estimates.max_pushups = int(lifts.get("max_pushups", 0)) if "max_pushups" in lifts else estimates.max_pushups
    estimates.max_pullups = int(lifts.get("max_pullups", 0)) if "max_pullups" in lifts else estimates.max_pullups
    estimates.plank_seconds = int(lifts.get("plank_seconds", 0)) if "plank_seconds" in lifts else estimates.plank_seconds
    await db.commit()
