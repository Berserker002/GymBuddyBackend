import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_jwt
from app.db.models import Program
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
    program_json = await generate_program(payload)
    program = Program(user_id=user.id, split=program_json["split"], program_json=program_json)
    db.add(program)
    await db.commit()
    await db.refresh(program)
    return program
