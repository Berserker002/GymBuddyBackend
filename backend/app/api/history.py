from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_jwt
from app.db.models import WorkoutLog
from app.db.schemas import HistoryEntry, HistoryResponse
from app.db.session import get_db
from app.db.utils import ensure_user

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=HistoryResponse)
async def get_history(
    exercise_id: str, db: AsyncSession = Depends(get_db), token: str = Depends(verify_jwt)
):
    user = await ensure_user(db, token)
    result = await db.execute(
        select(WorkoutLog.logged_at, WorkoutLog.actual_weight, WorkoutLog.target_weight)
        .where(WorkoutLog.user_id == user.id, WorkoutLog.exercise_id == exercise_id)
        .order_by(WorkoutLog.logged_at)
    )
    entries = [HistoryEntry(date=row[0].date(), weight=row[1] or row[2] or 0) for row in result.all()]
    return HistoryResponse(exercise=exercise_id, data=entries)
