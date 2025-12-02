from __future__ import annotations

from typing import Any

from app.db.models import ExerciseGuideCache


async def get_exercise_guide(
    exercise_name: str | None,
    image_url: str | None,
    existing_cache: ExerciseGuideCache | None = None,
) -> dict[str, Any]:
    """Return a cached guide or a placeholder response.

    Future implementations will integrate with OpenAI text + vision models and
    persist results back into the exercise_guides_cache table.
    """

    if existing_cache:
        return existing_cache.guide_json

    resolved_name = exercise_name or "unknown_machine"
    return {
        "muscles": ["chest", "triceps"] if resolved_name == "bench_press" else ["unknown"],
        "steps": ["Set up", "Perform controlled reps", "Rack the weight"],
        "mistakes": ["Bouncing reps", "Flared elbows"],
        "metadata": {"source": "placeholder", "image_url": image_url},
    }
