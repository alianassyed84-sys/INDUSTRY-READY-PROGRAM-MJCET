# Synthesized Constraints

## CON-01: Zero External AI / LLM Runtime Dependency
- **Source**: `docs/language_detector.md`, `docs/readability_auditor.md`, `docs/sentiment_analyzer.md`, `docs/topic_labeler.md`
- **Type**: `nfr`
- **Description**: All text and sentiment analysis engines operate locally, deterministically, and with zero external network or commercial LLM API dependencies. Latency per review must remain <5 ms.

## CON-02: Live Scraping Prohibition
- **Source**: `docs/authorized_providers.md`
- **Type**: `protocol`
- **Description**: Live web scraping of Amazon or third-party retail domains is strictly prohibited. External provider integrations must default to mock behavior unless explicitly configured with valid authorized credentials.

## CON-03: Database Portability
- **Source**: `docs/harvester.md`, `docs/development.md`
- **Type**: `schema`
- **Description**: The database abstraction must use SQLAlchemy 2.0 async with asyncpg for PostgreSQL in production and a compatible dialect (such as aiosqlite or in-memory SQLite) for lightweight automated test execution without external dependencies.

## CON-04: Stateless Polling Over Unmanaged Background Queues
- **Source**: `docs/price_monitoring.md`, `docs/harvester.md`
- **Type**: `api-contract`
- **Description**: In the absence of an operational Redis/broker infrastructure, long-running background workers (ARQ/Celery) must not be introduced arbitrarily. Endpoints remain synchronous or on-demand stateless polling until a background job milestone is explicitly scoped.
