import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_jwt
from app.db.models import ExerciseGuideCache
from app.db.schemas import ExerciseGuideRequest, ExerciseGuideResponse
from app.db.session import get_db
from app.services.ai_guide import get_exercise_guide

router = APIRouter(prefix="/api/exercise", tags=["exercise"])


@router.post("/guide", response_model=ExerciseGuideResponse)
async def exercise_guide(
    payload: ExerciseGuideRequest,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_jwt),
):
    # Optional cache lookup
    cached: ExerciseGuideCache | None = None
    if payload.exercise_name:
        result = await db.execute(
            select(ExerciseGuideCache).where(
                ExerciseGuideCache.exercise_name == payload.exercise_name.lower()
            )
        )
        cached = result.scalars().first()

    guide = await get_exercise_guide(payload.exercise_name, payload.image_url, cached)

    if not cached and payload.exercise_name:
        cache_entry = ExerciseGuideCache(
            exercise_name=payload.exercise_name.lower(), guide_json=guide
        )
        db.add(cache_entry)
        await db.commit()

    return guide
