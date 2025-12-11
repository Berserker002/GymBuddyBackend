# GymBuddy Backend API Notes

This document summarizes the current backend endpoints, expected payloads/responses, notable behavioral changes, and edge cases so the frontend can integrate safely.

## Recent changes
- User onboarding data (profile + strength estimates) is upserted during program initialization, aligning stored preferences with the submitted plan request.
- Workouts track `started_at` and `finished_at`; finishing a workout now returns per-exercise deltas against the prior log.
- Daily workout generation reuses the same-day plan if it already exists, applies saved swap preferences, and bumps target weights via simple progression (last fully completed set → +2.5kg).
- History weights fall back to logged targets when no actual weight exists, keeping charts populated.

## Authentication
All endpoints require a Bearer token in the `Authorization` header. A deterministic user ID is derived from the token by the existing `verify_jwt` dependency.

## Endpoints

### `POST /api/program/init`
- **Request body**: `ProgramCreate` with fields like `goal`, `experience`, `equipment` (array), optional `lifts` map, and onboarding fields (`gender`, `age`, `height_cm`, `weight_kg`, `training_days_per_week`).
- **Behavior**: Upserts `user_profiles` and `strength_estimates`, generates a program based on training days and lift estimates, and saves it in `programs`.
- **Response**: `{ id, split, program_json, created_at }`.
- **Edge cases**: Missing `lifts` are allowed; empty `equipment` defaults the stored equipment to `None`.

### `GET /api/workout/today`
- **Behavior**: Retrieves the latest program, raises 404 if none exists, reuses the persisted workout for today if present, or builds a new plan from the program rotation. Applies saved swap preferences and progression to adjust `target_weight` (+2.5kg after last fully completed sets).
- **Response**: `{ workout_id, day, exercises }` where `exercises` comes from the stored or newly built plan.
- **Edge cases**: Returns 404 if the user has no program; if the program has no days, returns an empty exercise list; day selection cycles by total completed/created workouts modulo program length.

### `PATCH /api/workout/update`
- **Request body**: `{ "day": <str>, "changes": [ { "exercise_id", "action": "swap", "new_exercise" } ] }`.
- **Behavior**: Persists swap preferences in `user_preferences.custom_variations` and tracks avoided exercises; future daily plans reflect these swaps.
- **Response**: `{ status: "updated", changes, preferences }`.
- **Edge cases**: Only the `swap` action is currently handled; other actions are ignored.

### `POST /api/workout/log`
- **Request body**: `WorkoutLogRequest` with `workout_id`, `exercise_id`, optional `actual_weight`/`target_weight`, `sets`, `reps`, and `completed`.
- **Behavior**: Validates workout ownership, sets `started_at` on first log, inserts a `workout_logs` row.
- **Response**: `{ status: "logged", log_id }`.
- **Edge cases**: 404 if the workout does not belong to the user; `completed` plus `reps` drive progression later, so empty reps will still count completion if `completed=true`.

### `POST /api/workout/finish`
- **Query param**: `workout_id`.
- **Behavior**: Sets `finished_at` (if missing), collects current logs, compares each exercise against the most recent prior log, and returns deltas.
- **Response**: `{ message: "Great work!", progress: { <exercise_id>: "+2.5kg" } | null }`.
- **Edge cases**: 404 if the workout is not found for the user; progress map omits exercises without a prior weight.

### `GET /api/history`
- **Query param**: `exercise_id`.
- **Behavior**: Returns chronological weight entries for the exercise, using `actual_weight` or falling back to `target_weight`, defaulting to `0` if both are missing.
- **Response**: `{ exercise: <exercise_id>, data: [ { date, weight } ] }`.

### `POST /api/exercise/guide`
- **Request body**: `{ exercise_name, image_url }` (image URL accepted but currently ignored).
- **Behavior**: Looks up a cached guide by lowercased `exercise_name`; otherwise generates a deterministic guide and stores it in `exercise_guides_cache`.
- **Response**: `{ muscles, steps, mistakes, metadata }`.
- **Edge cases**: Cache is skipped when `exercise_name` is not provided; metadata freshness is based on insert/update timestamps.

## Progression logic summary
- Uses the latest completed log per exercise; a log counts as fully completed when `completed=true` and the `reps` string contains positive integers for all sets.
- When fully completed, the next plan’s `target_weight` for that exercise increases by 2.5kg (rounded to one decimal). If today’s plan lacks a `target_weight`, the last log’s actual or target weight seeds the progression.

## Workout scheduling notes
- Daily plan selection rotates through program days using `total_workouts_created % len(days)`.
- If the user already has a workout persisted for today, the backend returns that plan unchanged instead of regenerating it.
