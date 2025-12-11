from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from app.db.models import WorkoutLog


def _is_full_completion(log: WorkoutLog) -> bool:
    reps_str = log.reps or ""
    reps_parts = [part.strip() for part in reps_str.split(",") if part.strip()]
    if not reps_parts:
        return log.completed
    return log.completed and all(part.isdigit() and int(part) > 0 for part in reps_parts)


def apply_progression_to_plan(
    plan_json: dict[str, Any], user_logs: Iterable[WorkoutLog]
) -> dict[str, Any]:
    """Adjust today's plan based on the last completed logs.

    Simple rule: if the last log for an exercise was marked completed and the reps
    string indicates all sets were done (e.g., "8,8,8"), bump target_weight by
    2.5kg. The function returns a mutated copy of the plan JSON.
    """

    plan_copy = {**plan_json}
    exercises = [dict(ex) for ex in plan_json.get("exercises", [])]
    plan_copy["exercises"] = exercises

    latest_log_by_exercise: dict[str, WorkoutLog] = {}
    for log in sorted(user_logs, key=lambda l: l.logged_at or datetime.min, reverse=True):
        if log.exercise_id not in latest_log_by_exercise and log.completed:
            latest_log_by_exercise[log.exercise_id] = log

    for exercise in exercises:
        exercise_id = exercise.get("id")
        if not exercise_id:
            continue

        last_log = latest_log_by_exercise.get(exercise_id)
        if not last_log or not _is_full_completion(last_log):
            continue

        target_weight = exercise.get("target_weight")
        if target_weight is None:
            target_weight = last_log.actual_weight or last_log.target_weight

        if target_weight is None:
            continue

        exercise["target_weight"] = round(float(target_weight) + 2.5, 1)

    return plan_copy
