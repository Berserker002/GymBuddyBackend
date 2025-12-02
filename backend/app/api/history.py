import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_jwt
from app.db.models import WorkoutLog
from app.db.schemas import HistoryEntry
from app.db.session import get_db

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("")
async def get_history(
    exercise_id: str, db: AsyncSession = Depends(get_db), token: str = Depends(verify_jwt)
):
    user_id = uuid.uuid5(uuid.NAMESPACE_DNS, token)
    result = await db.execute(
        select(WorkoutLog.logged_at, WorkoutLog.actual_weight)
        .where(WorkoutLog.user_id == user_id, WorkoutLog.exercise_id == exercise_id)
        .order_by(WorkoutLog.logged_at)
    )
    entries = [HistoryEntry(date=row[0].date(), weight=row[1] or 0) for row in result.all()]
    return {exercise_id: entries}
