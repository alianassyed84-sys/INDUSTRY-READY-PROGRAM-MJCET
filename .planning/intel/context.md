# Synthesized Context

## Project Architecture & Tech Stack
- **Source**: `README.md`, `docs/development.md`
- **Application**: ReviewPulse
- **Backend Framework**: FastAPI with Python 3.12+ (tested with 3.12/3.14).
- **ORM & Migrations**: SQLAlchemy 2.x async (`asyncpg`) and Alembic migrations.
- **Linguistic Engines**: Pure Python stdlib implementations for Language Identification (n-grams/Cavnar-Trenkle), Readability Auditing (Flesch, Fog, Coleman-Liau, Dale-Chall), Sentiment Analysis (calibrated lexicon + modifier grammar), and Topic Labeling (TF-IDF).
- **Development Tooling**: Ruff for linting and formatting; pytest for unit and integration testing. Windows PowerShell execution guidelines with local `.venv` execution without modifying machine-wide execution policies.
- **Product Roadmap Horizon**: Milestone 1 (FastAPI Foundation) & Milestone 2 (Linguistic Intelligence & Harvester) are implemented in the backend. Upcoming milestones target user authentication, price history workers, and Next.js frontend interfaces.
