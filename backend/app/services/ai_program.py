from __future__ import annotations

from datetime import datetime
from typing import Any

from app.db.schemas import ProgramCreate


async def generate_program(payload: ProgramCreate) -> dict[str, Any]:
    """Placeholder program generation using prompt spec.

    Replace with a call to OpenAI once keys are configured. Keeping the
    shape consistent with the PRD to enable frontend integration.
    """

    split = "upper_lower"
    days = [
        {
            "day": "Upper",
            "exercises": [
                {"id": "bench_press", "sets": 3, "reps": "8-10", "target_weight": 60},
                {"id": "barbell_row", "sets": 3, "reps": "8-10", "target_weight": 50},
            ],
        },
        {
            "day": "Lower",
            "exercises": [
                {"id": "back_squat", "sets": 3, "reps": "8-10", "target_weight": 80},
                {"id": "romanian_deadlift", "sets": 3, "reps": "10-12", "target_weight": 70},
            ],
        },
    ]

    return {
        "split": split,
        "days": days,
        "generated_at": datetime.utcnow().isoformat(),
    }
