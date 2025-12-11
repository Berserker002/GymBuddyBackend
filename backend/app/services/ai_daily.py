from __future__ import annotations

from typing import Any

from app.db.models import WorkoutLog
from app.services.progression import apply_progression_to_plan


async def generate_daily_plan(
    base_program: dict[str, Any],
    preferences: dict[str, Any] | None,
    history: list[WorkoutLog],
) -> dict[str, Any]:
    """Create a simple daily plan that respects the PRD shape.

    A future version will call GPT using the prompt provided in the PRD, but this
    keeps the contract intact for now.
    """

    day_plan = base_program.get("days", [])[0] if base_program else {}
    exercises = [dict(ex) for ex in day_plan.get("exercises", [])]

    for exercise in exercises:
        exercise_id = exercise.get("id")
        if preferences and exercise_id in preferences:
            exercise["id"] = preferences[exercise_id]

    progressed_plan = apply_progression_to_plan(
        {"day": day_plan.get("day", "Day 1"), "exercises": exercises}, history
    )

    return progressed_plan
