# ReviewPulse

## What This Is

ReviewPulse is an AI-powered product discovery and review intelligence application. It ingests consumer review datasets, performs deterministic computational linguistics (readability auditing, statistical language identification, aspect-based sentiment scoring, and TF-IDF keyphrase extraction), and provides price tracking and actionable intelligence for products.

## Core Value

Zero-dependency, high-speed review intelligence and product insights without relying on external commercial LLM APIs or brittle web scraping.

## Requirements

### Validated

- [x] **REQ-LANG-01**: Zero-dependency natural language identification supporting 12 ISO 639-1 languages with script fast-path and character n-gram profiling.
- [x] **REQ-READ-01**: Zero-dependency readability auditor computing classic formulas (Flesch, FKGL, Gunning Fog, Coleman-Liau, Dale-Chall) with consensus difficulty bands.
- [x] **REQ-SENT-01**: Deterministic sentiment analysis with modifier rules (negation, boosters, emphasis, contrast) and aspect-based sentiment analysis (ABSA).
- [x] **REQ-TOPIC-01**: TF-IDF keyphrase extraction returning unigrams and bigrams from a multi-document review corpus.
- [x] **REQ-HARV-01**: CSV dataset review harvester normalizing review records into PostgreSQL/SQLite via idempotent collection jobs.
- [x] **REQ-CAT-01**: Paginated product catalog and review search APIs.
- [x] **REQ-INSIGHT-01**: Aggregated product review intelligence endpoint combining sentiment, topics, ratings, and readability metrics.

### Active

- [ ] **REQ-PRICE-01**: Price tracking and historical observation monitoring with on-demand price checking, deduplication, and baseline statistics.

### Out of Scope

- **Live Amazon.in web scraping**: Strictly prohibited due to terms of service and legal constraints.
- **Heavyweight background queues without infrastructure**: Celery/Redis background task queues are deferred until dedicated broker infrastructure is provisioned.
- **Third-party LLM API dependencies for core analysis**: Natural language processing must remain self-contained, deterministic, and runnable locally in milliseconds.

## Context

- **Backend Stack**: Python 3.12+, FastAPI, SQLAlchemy 2.x async (`asyncpg`), Alembic migrations.
- **Testing**: 190 unit/integration tests running via `pytest` with in-memory SQLite support.
- **Linguistic Engines**: Zero external dependencies; written with pure Python standard library and calibrated product-review lexicons.
- **Platform**: Tested and optimized for Windows PowerShell and Linux deployment environments.

## Constraints

- **Performance**: Review analysis endpoints must execute deterministically in <5 ms per text passage.
- **Legal & Compliance**: No scraping of Amazon pages; PA-API 5.0 used only for metadata snapshots if credentials provided; review text sourced via curated datasets (`csv_amazon`).
- **Database Portability**: Code must support PostgreSQL via asyncpg in development/production and SQLite for lightweight local tests.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Scraping Prohibition (DEC-001) | Avoid violating Amazon Terms of Service; rely on authorized feeds or bundled review CSVs | ✓ Locked |
| Stateless Polling Policy (DEC-002) | Minimize operational overhead; defer Celery/ARQ until worker infrastructure is provisioned | ✓ Locked |
| Multi-Review CSV Comma Fallback (DEC-003) | Prevent parsing failures on commas in review text; assign full body to primary review | ✓ Locked |

---
*Last updated: 2026-10-21 after /gsd-ingest-docs*
