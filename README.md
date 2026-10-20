# ReviewPulse

ReviewPulse is an AI-powered product discovery and review intelligence application. This repository currently contains **Milestone 2**: a FastAPI backend with PostgreSQL / SQLAlchemy 2.x async integration, Alembic migrations, and automated linguistic analysis services. Product features, authentication, and the Next.js frontend are in upcoming milestones.

## Current backend

The API lives in [`backend/`](backend/). It exposes:

- `GET /api/v1/health` — process liveness
- `GET /api/v1/ready` — dependency readiness (does not claim PostgreSQL is healthy until a real check exists)
- `POST /api/v1/analysis/readability` — linguistic complexity and readability auditor (see [docs/readability_auditor.md](docs/readability_auditor.md))
- `POST /api/v1/analysis/language` — statistical language identification (see [docs/language_detector.md](docs/language_detector.md))
- `POST /api/v1/analysis/topics` — TF-IDF keyphrase extraction from a review corpus (see [docs/topic_labeler.md](docs/topic_labeler.md))
- `POST /api/v1/analysis/sentiment` — review polarity scoring and aspect-based sentiment (see [docs/sentiment_analyzer.md](docs/sentiment_analyzer.md))
- `POST /api/v1/harvester/jobs` — start review import job (see [docs/harvester.md](docs/harvester.md))
- `GET /api/v1/harvester/jobs/{id}` — check collection job status
- `GET /api/v1/harvester/products` — paginated product catalog
- `GET /api/v1/harvester/products/{id}` — detailed product view
- `GET /api/v1/harvester/products/{id}/insights` — aggregated review intelligence, sentiment, topics, ratings, and readability
- `GET /api/v1/harvester/reviews` — paginated review search and retrieval

Interactive docs (after the server is running): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Quick start (Windows PowerShell)

These commands assume Python 3.12+ is available (tested and verified on Python 3.12.15 and 3.14.3).

```powershell
python --version
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

If script activation is blocked, see [docs/development.md](docs/development.md) for process-scoped execution policy and no-activate alternatives. Do not set the machine execution policy to `Unrestricted`.

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in a browser.

Tests and lint (from `backend/` with the venv active):

```powershell
python -m pytest
python -m ruff check .
python -m ruff format --check .
deactivate
```

## PostgreSQL & Migrations

PostgreSQL is supported via SQLAlchemy 2.x async engine (`asyncpg`) and Alembic migrations. If `DATABASE_URL` is omitted, the API runs in memory-only mode for analysis endpoints; `GET /api/v1/ready` reports the database as `unconfigured`. When configured, `/api/v1/ready` performs a live `SELECT 1` ping.

Run migrations:

```powershell
cd backend
.\.venv\Scripts\alembic.exe upgrade head
```

## Next milestone

Data models, authentication, and product review storage entities.
