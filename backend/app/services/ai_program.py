from __future__ import annotations

from datetime import datetime
from typing import Any

from app.db.schemas import ProgramCreate


async def generate_program(payload: ProgramCreate) -> dict[str, Any]:
    """Placeholder program generation using prompt spec.

    Replace with a call to OpenAI once keys are configured. Keeping the
    shape consistent with the PRD to enable frontend integration.
    """

    days_per_week = payload.training_days_per_week or 3
    if days_per_week >= 5:
        split = "push_pull_legs"
        days = [
            {
                "day": "Push",
                "exercises": [
                    {"id": "bench_press", "sets": 3, "reps": "8-10", "target_weight": payload.lifts.get("bench", 60) if payload.lifts else 60},
                    {"id": "overhead_press", "sets": 3, "reps": "8-10", "target_weight": 40},
                ],
            },
            {
                "day": "Pull",
                "exercises": [
                    {"id": "barbell_row", "sets": 3, "reps": "8-10", "target_weight": 50},
                    {"id": "lat_pulldown", "sets": 3, "reps": "10-12", "target_weight": 45},
                ],
            },
            {
                "day": "Legs",
                "exercises": [
                    {"id": "back_squat", "sets": 3, "reps": "8-10", "target_weight": payload.lifts.get("squat", 70) if payload.lifts else 70},
                    {"id": "romanian_deadlift", "sets": 3, "reps": "10-12", "target_weight": 60},
                ],
            },
        ]
    elif days_per_week == 4:
        split = "upper_lower"
        days = [
            {
                "day": "Upper",
                "exercises": [
                    {"id": "bench_press", "sets": 3, "reps": "8-10", "target_weight": payload.lifts.get("bench", 60) if payload.lifts else 60},
                    {"id": "barbell_row", "sets": 3, "reps": "8-10", "target_weight": 50},
                ],
            },
            {
                "day": "Lower",
                "exercises": [
                    {"id": "back_squat", "sets": 3, "reps": "8-10", "target_weight": payload.lifts.get("squat", 80) if payload.lifts else 80},
                    {"id": "romanian_deadlift", "sets": 3, "reps": "10-12", "target_weight": 70},
                ],
            },
        ]
    else:
        split = "full_body"
        days = [
            {
                "day": "Full Body",
                "exercises": [
                    {"id": "goblet_squat", "sets": 3, "reps": "12", "target_weight": payload.lifts.get("goblet_squat", 24) if payload.lifts else 24},
                    {"id": "dumbbell_press", "sets": 3, "reps": "10", "target_weight": payload.lifts.get("dumbbell_press", 20) if payload.lifts else 20},
                    {"id": "dumbbell_row", "sets": 3, "reps": "10", "target_weight": payload.lifts.get("dumbbell_row", 24) if payload.lifts else 24},
                ],
            }
        ]

    return {
        "split": split,
        "days": days,
        "generated_at": datetime.utcnow().isoformat(),
    }
