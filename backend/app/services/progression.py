from __future__ import annotations

from typing import Any


def apply_progression(exercise: dict[str, Any], history: list[dict[str, Any]]) -> dict[str, Any]:
    """Very small progression helper using the PRD logic.

    If last session hit 90%+ completion, bump target weight by 2.5kg.
    """

    if not exercise:
        return {}

    target_weight = exercise.get("target_weight")
    if target_weight is None:
        return exercise

    completed_sets = sum(log.get("completed", True) for log in history)
    total_sets = len(history) if history else 0
    completion_rate = completed_sets / total_sets if total_sets else 1

    if completion_rate >= 0.9:
        exercise["target_weight"] = round(target_weight + 2.5, 1)
    return exercise
