from fastapi import FastAPI

from app.api.exercise import router as exercise_router
from app.api.history import router as history_router
from app.api.program import router as program_router
from app.api.workouts import router as workouts_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(program_router)
app.include_router(workouts_router)
app.include_router(exercise_router)
app.include_router(history_router)
