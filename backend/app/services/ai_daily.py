from __future__ import annotations

from typing import Any

from app.services.progression import apply_progression


async def generate_daily_plan(
    base_program: dict[str, Any], preferences: dict[str, Any] | None, history: list[dict[str, Any]]
) -> dict[str, Any]:
    """Create a simple daily plan that respects the PRD shape.

    A future version will call GPT using the prompt provided in the PRD, but this
    keeps the contract intact for now.
    """

    day_plan = base_program.get("days", [])[0] if base_program else {}
    exercises = day_plan.get("exercises", [])
    progressed = [apply_progression(ex, history) for ex in exercises]
    return {"day": day_plan.get("day", "Day 1"), "exercises": progressed}
