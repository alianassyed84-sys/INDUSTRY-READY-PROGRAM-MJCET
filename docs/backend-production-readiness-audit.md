# ReviewPulse — Backend Production-Readiness Audit

**Date:** 2026-10-21  
**Target Component:** ReviewPulse Backend (`backend/`)  
**Audit Scope:** Production readiness, reliability, security, scalability, architecture, and deployment (excluding all frontend concerns).  
**Status:** Audit Complete — No application code, dependencies, or tests modified.

---

## 1. Executive Summary & Verified Baseline

### 1.1 Executive Summary
ReviewPulse features a high-quality, zero-dependency computational linguistics engine (readability, language identification, sentiment polarity, and TF-IDF topic extraction) accompanied by an extensive 278-test automated suite. Core business logic, Pydantic schemas for NLP endpoints, and basic database models are well-architected and clean.

However, the backend currently operates as a **synchronous single-process development prototype** rather than a production-ready cloud service. The audit identified **3 Critical findings** and **7 High-severity findings** that must be addressed prior to exposing the API to public production traffic:
1. **Critical Security**: Complete absence of authentication and authorization on data-ingestion and administrative endpoints (`/jobs`, `/check-price`).
2. **Critical Security**: Arbitrary server file path read in `POST /api/v1/harvester/jobs` via unsanitized `csv_path` payload input.
3. **Critical Reliability**: Lack of asynchronous background job processing — CSV imports and provider polling execute synchronously inside HTTP request handlers, causing request timeouts, connection hogging, and orphaned jobs.
4. **High Architectural**: Absence of database connection pool sizing, missing composite indexes, floating-point monetary storage, and check-then-act race conditions on price observations.
5. **High Operations**: No rate limiting, no request correlation ID tracing, no Prometheus metrics, and no CI/CD or Docker containerization.

### 1.2 Verified Execution Baseline
The following commands were executed in the `backend/` directory using Python 3.12.15 in the project virtual environment (`backend/.venv`):

| Check | Command Executed | Result | Notes |
|---|---|---|---|
| **Test Suite** | `python -m pytest -W error --tb=short -q` | **278 passed in 9.74s** | Executed with warnings treated as errors. All tests pass with zero warnings. |
| **Linting** | `ruff check .` | **All checks passed!** | 0 lint violations across all modules and tests. |
| **Formatting** | `ruff format --check .` | **62 files already formatted** | 100% compliant with Ruff style guidelines. |
| **Live Database** | `check_database_connection` | **Unverified (Limitation)** | Automated tests execute against in-memory SQLite (`sqlite+aiosqlite:///:memory:`). No live PostgreSQL instance was connected during audit. |

---

## 2. Inventory of Existing Capabilities (Already Complete)

The following capabilities are fully implemented, verified, and production-grade in their algorithmic implementation:

1. **Computational Linguistics (Pure Python, Zero External API Dependencies)**:
   - **Language Identifier** (`app/services/language_detection.py`): 12 ISO 639-1 languages, script-based fast path for non-Latin scripts (Arabic, Cyrillic, CJK, Katakana/Hiragana), and Cavnar & Trenkle (1994) character n-gram rank-order profiling. Sub-millisecond execution.
   - **Readability Auditor** (`app/services/readability.py`): Flesch Reading Ease, Flesch-Kincaid Grade Level, Gunning Fog, Coleman-Liau, and Automated Readability Index (ARI) with structural statistics and reliability assessments.
   - **Sentiment Analysis Engine** (`app/services/sentiment.py`): Rule- and lexicon-based polarity analyzer calibrated for consumer reviews. Implements grammatical modifier rules (negation flipping, booster scaling, ALL-CAPS emphasis, exclamation amplification, and contrastive conjunction pivots). Supports Aspect-Based Sentiment Analysis (ABSA).
   - **Topic Labeler** (`app/services/topics.py`): Multi-document corpus TF-IDF keyphrase extraction producing ranked unigrams and bigrams with stop-word filtering.
2. **Amazon URL Validation & Security** (`app/services/harvester/amazon_url.py`):
   - Strict HTTPS enforcement, restriction to `ALLOWED_HOSTNAMES` (`amazon.in`, `www.amazon.in`, `m.amazon.in`), prohibition of embedded user-info/authority credentials, and regex extraction of 10-character alphanumeric ASINs. Zero network calls or SSRF risk.
3. **Price Snapshot Analytics Contract** (`app/services/harvester/price_history.py`):
   - Strict baseline peak logic (single observations are explicitly treated as baselines, never historical peaks).
   - Multi-currency mathematical guard (isolates price deltas and percentages strictly to the primary observation currency).
4. **Configuration & Production CORS Validation** (`app/core/config.py`):
   - Pydantic Settings with `@model_validator(mode="after")` enforcing that when `APP_ENV=production`, `CORS_ORIGINS` must be non-empty and cannot contain wildcard `*`.
5. **Basic Liveness and Database Readiness Probes** (`app/api/v1/health.py`):
   - `GET /api/v1/health`: Instant liveness probe.
   - `GET /api/v1/ready`: Dependency check executing `SELECT 1` with a 2-second timeout against configured `DATABASE_URL`.

---

## 3. Categorized Production-Readiness Findings

### 3.1 Severity Definitions
- **Critical**: Security vulnerabilities, data loss risks, or fundamental architectural blockers that prevent production launch.
- **High**: Major operational, performance, or reliability deficiencies that degrade service stability under real-world load.
- **Medium**: Maintainability, API design, telemetry, or edge-case gaps that should be addressed before general availability.
- **Low**: Code hygiene, documentation refinements, and developer ergonomics.

---

### Finding F-01: Arbitrary Server File Path Ingestion (Path Traversal / Local File Read)
- **Severity**: **Critical**
- **Category**: Security / Data Integrity
- **Classification**: **Confirmed Defect**
- **Evidence**:
  - `backend/app/schemas/harvester.py:27-33`: `JobStartRequest.csv_path` accepts an unvalidated arbitrary `str | None`.
  - `backend/app/api/v1/harvester.py:124-141`: `start_job` reads `csv_path = payload.csv_path or settings.amazon_csv_path` and immediately invokes `await run_csv_import(session=db, csv_path=csv_path, job=job)`.
  - `backend/app/services/harvester/csv_adapter.py:38`: `open(self.csv_path, "r", encoding="utf-8")` opens the client-supplied path directly.
- **Impact**: Any unauthenticated client can send arbitrary file paths (e.g. `/etc/passwd`, Windows system files, or sensitive configuration files). If readable, parse errors or sampled contents leak into `CollectionJob.error_sample` or logs.
- **Remediation**: Remove `csv_path` from the public API request body. In production, only permit ingestion from the server-configured `AMAZON_CSV_PATH` or an authenticated multipart file upload with strict content-type and extension validation stored in a sandboxed temporary directory.

---

### Finding F-02: Total Absence of Authentication and Authorization Controls
- **Severity**: **Critical**
- **Category**: Security
- **Classification**: **Missing Capability**
- **Evidence**:
  - `backend/app/api/v1/harvester.py:103-144`: `POST /api/v1/harvester/jobs` has no security dependencies or token checks.
  - `backend/app/api/v1/harvester.py:403-451`: `POST /api/v1/harvester/products/{id}/check-price` has no authentication.
  - `backend/app/api/v1/analysis.py`, `language_detection.py`, `sentiment.py`, `topics.py`: All computational endpoints are public without API keys or JWT guards.
- **Impact**: Any anonymous user on the public internet can trigger resource-intensive database import jobs, initiate external provider price checks, and run CPU-heavy TF-IDF algorithms at will.
- **Remediation**:
  - Implement an API Key or Bearer JWT authentication dependency (`HTTPBearer` / `Security`).
  - Differentiate between Administrative actions (starting harvest jobs, configuring providers) and Consumer actions (viewing product insights, checking prices).

---

### Finding F-03: Synchronous Long-Running Request Execution in HTTP Lifecycle
- **Severity**: **Critical**
- **Category**: Architecture / Reliability
- **Classification**: **Confirmed Defect**
- **Evidence**:
  - `backend/app/api/v1/harvester.py:109-141`: Route docstring explicitly notes: `starts an import job... and runs it synchronously (completes before responding)`.
  - `backend/app/services/harvester/importer.py:115-189`: `run_csv_import` executes a loop over 1,465 records with `await session.commit()` after every single row.
- **Impact**:
  - Running 1,465 sequential commits takes 2–5 seconds locally and 15–30+ seconds over a network connection to managed PostgreSQL (e.g. AWS RDS).
  - Reverse proxies (Cloudflare, Nginx, AWS ALB) will drop requests with HTTP 504 Gateway Timeout if imports exceed 30–60 seconds.
  - HTTP worker threads in Uvicorn are tied up, blocking other incoming user traffic.
  - If the server restarts or is terminated during an import, the job record remains stuck in `status="running"` indefinitely.
- **Remediation**:
  - Decouple job initiation from job execution. `POST /api/v1/harvester/jobs` must return HTTP 202 Accepted immediately with `{id: ..., status: "pending"}`.
  - Offload execution to an asynchronous background worker (e.g. ARQ with Redis or FastAPI `BackgroundTasks` for single-node deployments).
  - Add job heartbeats and a recovery sweeper to mark orphaned jobs as `failed` on service startup.

---

### Finding F-04: Check-Then-Act Concurrency Race Condition in Price Snapshot Recording
- **Severity**: **High**
- **Category**: Concurrency / Data Integrity
- **Classification**: **Confirmed Defect**
- **Evidence**:
  - `backend/app/services/harvester/price_history.py:84-110`:
    ```python
    latest_stmt = select(PriceSnapshot).where(...).order_by(desc(PriceSnapshot.observed_at)).limit(1)
    last_snap = (await session.execute(latest_stmt)).scalar_one_or_none()
    if last_snap is not None and last_snap.price == float(price) and ...:
        return last_snap
    snapshot = PriceSnapshot(...)
    session.add(snapshot)
    await session.flush()
    ```
  - `backend/app/models/price_snapshot.py:11-35`: `price_snapshots` table lacks any composite unique constraint or exclusion lock on `(product_id, price, observed_at)`.
- **Impact**: Two concurrent requests checking the price of the same product simultaneously will both execute the `SELECT`, find no recent snapshot, and both insert duplicate rows, violating the documented deduplication guarantee.
- **Remediation**:
  - Add an advisory lock or `SELECT ... FOR UPDATE` on the parent `Product` row during price snapshot recording.
  - Or define a unique index or idempotency key window (e.g. `(product_id, date_trunc('minute', observed_at))`).

---

### Finding F-05: Missing Database Connection Pool Configuration
- **Severity**: **High**
- **Category**: Database / Scalability
- **Classification**: **Missing Capability**
- **Evidence**:
  - `backend/app/core/database.py:42`: `create_async_engine(async_url, pool_pre_ping=True)`.
  - `backend/app/core/config.py:13-36`: `Settings` contains no parameters for `database_pool_size`, `database_max_overflow`, `database_pool_timeout`, or `database_pool_recycle`.
- **Impact**: Under production traffic spikes, SQLAlchemy falls back to default `QueuePool` settings (pool_size=5, max_overflow=10). Exhausting these 15 connections will cause `TimeoutError: QueuePool limit of size 5 overflow 10 reached, connection timed out`.
- **Remediation**: Expose configurable connection pool settings in `Settings` (`DB_POOL_SIZE=20`, `DB_MAX_OVERFLOW=10`, `DB_POOL_TIMEOUT=30`, `DB_POOL_RECYCLE=1800`) and pass them to `create_async_engine`.

---

### Finding F-06: Missing Composite Indexes for High-Frequency Queries
- **Severity**: **High**
- **Category**: Database Performance
- **Classification**: **Confirmed Defect**
- **Evidence**:
  - `backend/app/models/price_snapshot.py:28`: Index exists on `product_id` alone and on `observed_at` alone.
  - `backend/alembic/versions/0002_add_price_snapshots.py:47-50`: Separate single-column indexes:
    `op.create_index("ix_price_snapshots_product_id", "price_snapshots", ["product_id"])`
    `op.create_index("ix_price_snapshots_observed_at", "price_snapshots", ["observed_at"])`
  - `backend/app/services/harvester/price_history.py:129-136`: Queries filter by `product_id` AND order/filter by `observed_at`.
- **Impact**: As price observations accumulate (e.g. thousands of snapshots per product), Postgres cannot perform an efficient index scan for chronological ranges or latest-observation lookups without expensive bitmap index merges or in-memory sorts.
- **Remediation**: Create an Alembic migration adding a composite index:
  `CREATE INDEX ix_price_snapshots_product_observed ON price_snapshots (product_id, observed_at DESC);`

---

### Finding F-07: Use of IEEE 754 Floating-Point for Monetary Values
- **Severity**: **High**
- **Category**: Data Integrity
- **Classification**: **Confirmed Defect**
- **Evidence**:
  - `backend/app/models/product.py:22-23`: `discounted_price: Mapped[float | None] = mapped_column(Float, nullable=True)`, `actual_price: Mapped[float | None] = mapped_column(Float)`.
  - `backend/app/models/price_snapshot.py:23-24`: `price: Mapped[float] = mapped_column(Float, nullable=False)`.
  - `backend/alembic/versions/0001_add_core_entities.py:28-29`: `sa.Column("discounted_price", sa.Float(), nullable=True)`.
- **Impact**: Binary floating-point representation causes inexact decimal storage (e.g. `199.99` represented as `199.990000000000009`). This leads to subtle price calculation drift and comparison errors in price history deltas.
- **Remediation**: Migrate monetary columns from `Float` / `sa.Float()` to `Numeric(12, 2)` / `Decimal` in PostgreSQL models and Pydantic schemas.

---

### Finding F-08: Complete Absence of API Rate Limiting and Abuse Prevention
- **Severity**: **High**
- **Category**: Security / Infrastructure
- **Classification**: **Missing Capability**
- **Evidence**:
  - No rate limiting middleware or decorators exist across `app/main.py` or any API router.
  - `pyproject.toml` contains no rate limiting dependency (such as `slowapi` or Redis-backed token bucket).
- **Impact**: An attacker or rogue script can hammer `POST /api/v1/analysis/topics` with large payloads, exhausting CPU and memory and causing Denial of Service for legitimate users.
- **Remediation**: Integrate rate limiting (e.g. `slowapi` with IP/API-key bucket limits) and configure reasonable thresholds (e.g. 60 requests/minute for analysis endpoints, 5 requests/minute for harvesting).

---

### Finding F-09: Missing Request Correlation ID and Structured JSON Logging
- **Severity**: **High**
- **Category**: Observability
- **Classification**: **Confirmed Defect**
- **Evidence**:
  - `backend/app/core/logging.py:13-33`: `StructuredFormatter` checks for `record.request_id`, but no middleware generates or propagates an `X-Request-ID` header.
  - `backend/app/main.py:22-42`: No correlation ID middleware is registered.
  - Logs are output as plain-text `key=value` strings rather than JSON objects.
- **Impact**: In multi-replica cloud environments, logs from concurrent requests interleave, making it impossible to trace the lifecycle of a failed request across log aggregators (CloudWatch, Datadog, Loki).
- **Remediation**:
  - Add an ASGI middleware that generates a UUID4 `X-Request-ID` for incoming requests (or captures incoming header) and attaches it to a `contextvars.ContextVar`.
  - Update `StructuredFormatter` or add `python-json-logger` to output machine-readable JSON in non-development environments.

---

### Finding F-10: Pydantic Validation Exception Handler Discards Error Details
- **Severity**: **Medium**
- **Category**: API Usability / Contract
- **Classification**: **Confirmed Defect**
- **Evidence**:
  - `backend/app/core/errors.py:24-30`:
    ```python
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, _exc: RequestValidationError) -> JSONResponse:
        logger.info("Invalid request path=%s", request.url.path)
        return JSONResponse(status_code=422, content={"detail": "Invalid request"})
    ```
- **Impact**: When a client submits a payload with an invalid field (e.g. wrong type or out-of-range value), the API returns a generic `{"detail": "Invalid request"}` without indicating *which* field failed. This violates standard REST/FastAPI contracts and severely hinders frontend debugging.
- **Remediation**: Return structured validation error details (e.g. `{"detail": "Validation error", "errors": exc.errors()}`) while sanitizing internal path details.

---

### Finding F-11: Provider Client Implementation is Incomplete (Stubbed Network Calls)
- **Severity**: **Medium**
- **Category**: Integrations
- **Classification**: **Missing Capability**
- **Evidence**:
  - `backend/app/services/harvester/authorized_provider.py:77-92`: `AmazonCreatorApiProvider.get_product_by_asin` verifies credentials and then unconditionally raises `ProviderNotConfiguredError("Live network calls without verified sandbox or production tokens are disabled...")`.
  - No AWS SigV4 HTTP client implementation (using `httpx` with AWS auth or `boto3`) exists.
- **Impact**: Even if valid Amazon PA-API credentials are provided in `.env`, the system cannot actually execute live item lookup requests.
- **Remediation**: Implement the actual signed HTTP POST client to `https://webservices.amazon.in/paapi5/getitems` with request timeouts, token bucket rate limiting (1 TPS), and error mapping.

---

### Finding F-12: Absence of Operational Metrics Endpoint and Health Check Depth
- **Severity**: **Medium**
- **Category**: Observability / Monitoring
- **Classification**: **Missing Capability**
- **Evidence**:
  - `backend/app/api/v1/health.py:17-58`: Implements `/health` and `/ready`.
  - No Prometheus metrics endpoint (`/metrics`) exists.
  - No monitoring for database pool saturation, request latency percentiles (p50, p95, p99), or error rates.
- **Impact**: Site reliability engineering (SRE) and Kubernetes horizontal pod autoscalers (HPA) lack standard metrics to monitor latency spikes or automatically scale replicas.
- **Remediation**: Integrate `prometheus-fastapi-instrumentator` to export standard HTTP request durations, active connection gauges, and status code counters on `/metrics` (restricted to internal network/monitoring scraper).

---

### Finding F-13: Missing Containerization, CI/CD, and Production Deployment Assets
- **Severity**: **Medium**
- **Category**: DevOps / Deployment
- **Classification**: **Missing Capability**
- **Evidence**:
  - Repository contains no `Dockerfile`, `docker-compose.yml`, or `.github/workflows/`.
  - No production WSGI/ASGI configuration (e.g. multi-worker Gunicorn with Uvicorn worker class).
- **Impact**: Deployments are manual and environment-dependent, risking "works on my machine" failures in production staging.
- **Remediation**: Create a multi-stage production `Dockerfile` (distroless or Debian slim, non-root user), a `docker-compose.yml` with PostgreSQL for local testing, and a GitHub Actions workflow executing lint, format check, and pytest.

---

### Finding F-14: Inefficient Offset Pagination on Large Catalog Tables
- **Severity**: **Low**
- **Category**: Database Performance
- **Classification**: **Unverified Assumption (Architecture Ceiling)**
- **Evidence**:
  - `backend/app/services/harvester/importer.py:213-240`: `list_products` and `list_reviews` use `.limit(limit).offset(offset)`.
- **Impact**: Works fine for small datasets (~1,500 products), but degrades to $O(N)$ table scans in PostgreSQL if catalogs grow to 100,000+ reviews.
- **Remediation**: Retain offset pagination for small catalogs; document upgrade path to keyset pagination (`WHERE id > :cursor LIMIT :limit`) for scale.

---

## 4. Summary Matrix of Findings

| ID | Title | Severity | Classification | Impacted Subsystem |
|---|---|---|---|---|
| **F-01** | Arbitrary Server File Path Ingestion | **Critical** | Confirmed Defect | `harvester.py`, `JobStartRequest` |
| **F-02** | Total Absence of Auth/AuthZ Controls | **Critical** | Missing Capability | Entire API Surface |
| **F-03** | Synchronous Request Execution for Batch Ingestion | **Critical** | Confirmed Defect | `importer.py`, `start_job` |
| **F-04** | Check-Then-Act Race Condition in Price Snapshots | **High** | Confirmed Defect | `price_history.py` |
| **F-05** | Missing Database Connection Pool Configuration | **High** | Missing Capability | `database.py`, `config.py` |
| **F-06** | Missing Composite Indexes on Price Observations | **High** | Confirmed Defect | `price_snapshot.py`, Migrations |
| **F-07** | Floating-Point Used for Monetary Storage | **High** | Confirmed Defect | `product.py`, `price_snapshot.py` |
| **F-08** | Complete Absence of API Rate Limiting | **High** | Missing Capability | API Gateway / Middleware |
| **F-09** | Missing Request Correlation ID & JSON Logs | **High** | Confirmed Defect | `logging.py`, Middleware |
| **F-10** | Validation Exception Handler Discards Field Details | **Medium** | Confirmed Defect | `errors.py` |
| **F-11** | Live Provider Client Implementation Incomplete | **Medium** | Missing Capability | `authorized_provider.py` |
| **F-12** | Absence of Operational Metrics Endpoint | **Medium** | Missing Capability | `health.py`, Monitoring |
| **F-13** | Missing Docker, Compose, and CI/CD Pipeline | **Medium** | Missing Capability | DevOps / Tooling |
| **F-14** | Offset Pagination Scalability Ceiling | **Low** | Unverified Assumption | `importer.py` |

---

## 5. Prioritized Implementation Roadmap

To systematically bring the backend to production readiness without creating brittle massive diffs, the work should be executed across **4 distinct, test-driven milestones**:

```
┌────────────────────────────────┐
│ Milestone 1: Security & Auth   │ ──► Close F-01 (Path Traversal), F-02 (Auth), F-08 (Rate Limiting)
└────────────────┬───────────────┘
                 │
                 ▼
┌────────────────────────────────┐
│ Milestone 2: DB & Persistence  │ ──► Close F-04 (Race), F-05 (Pool), F-06 (Index), F-07 (Numeric)
└────────────────┬───────────────┘
                 │
                 ▼
┌────────────────────────────────┐
│ Milestone 3: Async Ingestion   │ ──► Close F-03 (Background Jobs), F-10 (Error Details)
└────────────────┬───────────────┘
                 │
                 ▼
┌────────────────────────────────┐
│ Milestone 4: DevOps & Observ.  │ ──► Close F-09 (Req-ID), F-12 (Metrics), F-13 (Docker/CI), F-11 (Provider)
└────────────────────────────────┘
```

---

### Milestone 1: Security Hardening, Authentication, and Rate Limiting
- **Goal**: Protect API endpoints from arbitrary file access, unauthorized execution, and denial-of-service abuse.
- **Scope**:
  1. Remove `csv_path` from `JobStartRequest`. Bind import strictly to server-configured `AMAZON_CSV_PATH` or an authenticated sandboxed upload.
  2. Implement API authentication (`API_KEY` header or JWT Bearer authentication dependency).
  3. Introduce rate limiting (`slowapi` with in-memory or Redis backend) on all endpoints.
- **Acceptance Criteria**:
  - `POST /api/v1/harvester/jobs` rejects any external file path injection attempts (HTTP 422 or unauthorized).
  - Unauthenticated requests to administrative endpoints return HTTP 401 Unauthorized.
  - Burst requests exceeding configured limits receive HTTP 429 Too Many Requests with a `Retry-After` header.
- **Regression Tests**:
  - `test_unauthenticated_requests_rejected_401()`
  - `test_job_start_disallows_arbitrary_file_paths()`
  - `test_rate_limiter_throttles_excessive_traffic()`

---

### Milestone 2: Database Hardening, Concurrency, and Numeric Precision
- **Goal**: Guarantee transactional integrity, concurrency safety, connection scalability, and financial precision.
- **Scope**:
  1. Expose database connection pool parameters (`DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_TIMEOUT`, `DB_POOL_RECYCLE`) in `Settings` and pass to `create_async_engine`.
  2. Add an Alembic migration creating a composite index on `price_snapshots (product_id, observed_at DESC)`.
  3. Convert monetary columns (`discounted_price`, `actual_price`, `price`) from `Float` to `Numeric(12, 2)` / Python `Decimal`.
  4. Wrap price snapshot recording in an advisory lock or row-level `SELECT ... FOR UPDATE` to eliminate concurrent duplicate insertion.
- **Acceptance Criteria**:
  - Concurrent `POST /check-price` requests for the same product at the same millisecond insert exactly one snapshot.
  - Price queries against products with 10,000+ snapshots utilize index-only or index-range scans without in-memory sorting.
  - Currency mathematics is exact to 2 decimal places with no binary floating-point representation drift.
- **Regression Tests**:
  - `test_concurrent_price_snapshot_deduplication()`
  - `test_numeric_precision_exact_cents()`
  - `test_connection_pool_saturation_and_recovery()`

---

### Milestone 3: Asynchronous Ingestion & Resilient Job Lifecycles
- **Goal**: Decouple heavy data collection from HTTP request cycles, preventing gateway timeouts and orphaned tasks.
- **Scope**:
  1. Refactor `POST /api/v1/harvester/jobs` to return HTTP 202 immediately with job metadata.
  2. Offload `run_csv_import` to an asynchronous task execution queue.
  3. Batch database inserts (e.g. 100 rows per transaction) instead of committing after every individual product row.
  4. Implement an automatic startup sweeper that transitions stale `running` jobs to `failed` upon application restart.
  5. Enhance `validation_exception_handler` to include Pydantic field-level error messages in the HTTP 422 response body.
- **Acceptance Criteria**:
  - `POST /jobs` returns HTTP 202 in <50 ms regardless of dataset file size.
  - Client disconnections do not abort ongoing background import jobs.
  - A killed and restarted backend server automatically reconciles interrupted jobs.
- **Regression Tests**:
  - `test_job_start_returns_202_immediately()`
  - `test_job_status_polling_tracks_background_progress()`
  - `test_stale_job_recovery_on_startup()`
  - `test_validation_error_returns_field_specific_details()`

---

### Milestone 4: Production Observability, DevOps, and Upstream Integration
- **Goal**: Enable production deployments, containerization, request tracing, and automated CI/CD verification.
- **Scope**:
  1. Add ASGI Request Correlation ID middleware injecting `X-Request-ID` into response headers and logging contexts.
  2. Implement structured JSON logging for staging and production environments.
  3. Export standard Prometheus metrics (`/metrics`) for request duration and HTTP status codes.
  4. Create production multi-stage `Dockerfile` (non-root unprivileged user) and `docker-compose.yml` with PostgreSQL.
  5. Implement live AWS SigV4 signed client in `AmazonCreatorApiProvider` with token bucket rate limiting (1 TPS) and exponential backoff.
  6. Add GitHub Actions CI workflow executing `pytest`, `ruff check`, and `ruff format`.
- **Acceptance Criteria**:
  - Every log entry contains matching `request_id` for correlated tracing.
  - Container builds pass vulnerability scanning and run with non-root UID.
  - Automated CI workflow runs on every pull request and passes cleanly.
- **Regression Tests**:
  - `test_request_id_header_injected_and_propagated()`
  - `test_metrics_endpoint_exports_prometheus_format()`
  - `test_live_provider_sigv4_request_signing()`

---

## 6. External Prerequisites & Deployment Infrastructure

Before launching ReviewPulse in a live production environment, the following external accounts and infrastructure must be provisioned:

1. **Amazon Associates / Creator Credentials**:
   - Approved Amazon Associates account in the `amazon.in` locale with at least 3 qualifying sales within the past 180 days.
   - PA-API 5.0 Access Key ID, Secret Key, and Partner Associate Tag.
2. **Managed PostgreSQL Database**:
   - PostgreSQL 16+ instance (e.g. AWS RDS, Supabase, or GCP Cloud SQL) with SSL enforced (`sslmode=require`).
   - Provisioned connection limits aligned with backend replica counts (`max_connections >= (replicas * DB_POOL_SIZE) + 20`).
3. **Redis Broker (Optional for Milestone 3, Recommended for Multi-Replica)**:
   - Redis 7+ instance for distributed task queuing (ARQ/Celery) and distributed rate-limiting buckets across replicas.
4. **Production Host & Container Registry**:
   - Container orchestration environment (AWS ECS Fargate, GCP Cloud Run, or Kubernetes) with secret management integration (AWS Secrets Manager, Doppler, or HashiCorp Vault).

---

## 7. Production-Readiness Sign-Off Checklist

Before general availability deployment, ensure every item below has been verified:

- [ ] **Security**: Path traversal in `JobStartRequest.csv_path` eliminated (F-01).
- [ ] **Security**: API authentication enabled on all state-modifying and administrative endpoints (F-02).
- [ ] **Security**: API rate limiting enabled and verified under load (F-08).
- [ ] **Security**: Production CORS origins verified and wildcard origins prohibited.
- [ ] **Data Integrity**: Concurrency race condition on price snapshot recording eliminated (F-04).
- [ ] **Data Integrity**: Monetary columns migrated to `Numeric(12, 2)` (F-07).
- [ ] **Performance**: Composite index `(product_id, observed_at DESC)` created and verified with `EXPLAIN ANALYZE` (F-06).
- [ ] **Performance**: Database connection pool tuned with overflow and recycle limits (F-05).
- [ ] **Reliability**: Batch review harvesting executed asynchronously with durable job status tracking (F-03).
- [ ] **Observability**: Request correlation IDs propagated across all logs (F-09).
- [ ] **Observability**: Prometheus metrics exported and scraped by monitoring system (F-12).
- [ ] **API Contract**: HTTP 422 errors return descriptive field-level error messages (F-10).
- [ ] **DevOps**: Multi-stage Docker image built, tested, and running as non-root (F-13).
- [ ] **DevOps**: Automated CI workflow passing on all PRs.
- [ ] **Disaster Recovery**: Automated daily database backups with point-in-time recovery (PITR) configured.

---

*Audit completed by Antigravity IDE Autonomous Agent on 2026-10-21.*
