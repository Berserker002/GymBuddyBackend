# AI Gym Partner Backend (FastAPI + PostgreSQL)

FastAPI starter that matches the PRD:
- Program generation
- Daily workout retrieval & updates
- Workout logging & history
- Exercise guide with cache (text/vision ready stubs)

## Getting started

1. Create a Python environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment via `.env` (optional defaults shown):
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/gymbuddy
   OPENAI_API_KEY=sk-...
   SUPABASE_JWT_SECRET=...
   ```

3. Run migrations:
   ```bash
   alembic upgrade head
   ```

4. Start the API:
   ```bash
   uvicorn app.main:app --reload --app-dir backend
   ```

## Project layout
```
backend/
  app/
    api/          # Routers for program, workouts, exercise, history
    core/         # Settings, security
    db/           # SQLAlchemy models, schemas, session
    services/     # AI placeholders + progression logic
    main.py       # FastAPI application
alembic/          # Async migrations
```

## Notes
- JWT verification is a lightweight placeholder; wire to Supabase/custom auth before production.
- AI services return deterministic placeholders but match the expected JSON envelopes so they can be swapped with real OpenAI calls.
- The daily plan uses simple progression logic; extend `services/progression.py` with richer rules as needed.
