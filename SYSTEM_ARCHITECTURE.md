# SYSTEM_ARCHITECTURE.md

# ReviewPulse — System Architecture

**Document status:** Proposed architecture for initial implementation  
**Project stage:** Starting from scratch  
**Team size:** 3 members  
**Primary objective:** Build a modular, maintainable AI-powered e-commerce review intelligence platform  
**Architecture style:** Modular monolith with a separately deployed frontend and backend  
**Frontend:** Next.js  
**Backend:** Python FastAPI  
**Initial deployment target:** Vercel for the frontend and a separate hosting provider for the backend  
**Audience:** Project contributors, AI coding agents, technical reviewers, and future maintainers

---

## 1. Purpose and Scope

This document defines the proposed system architecture for ReviewPulse, including application boundaries, data management, AI analysis, background processing, APIs, authentication, security, deployment, team ownership, and quality assurance.

ReviewPulse helps e-commerce sellers, small businesses, and product teams understand customer feedback across products. It combines review analytics, natural-language processing, statistical analysis, and evidence-grounded AI to identify emerging complaints, compare product claims with customer experiences, and surface contradictions between numerical ratings and written review content.

This document is the architectural source of truth for the initial implementation. It does not assert that the described components, services, directories, database, or deployment infrastructure already exist.

### 1.1 Architectural goals

1. Establish clear boundaries between the frontend, backend, data layer, and analysis pipeline.
2. Enable three contributors to work in parallel without relying on undocumented internal interfaces.
3. Preserve traceability from every important AI-generated finding to the underlying review evidence.
4. Process uploaded review datasets reliably, including failures and retries.
5. Begin with a manageable college-project prototype while retaining a practical upgrade path.
6. Protect uploaded datasets and enforce account or workspace isolation.
7. Make technical decisions explicit, testable, and revisable.

### 1.2 Non-goals for the initial prototype

Unless subsequently approved, the initial architecture does not require:

- Microservices or a distributed service mesh.
- Kubernetes or multi-region infrastructure.
- Real-time streaming ingestion from multiple commerce platforms.
- Automatic scraping of e-commerce websites.
- Training or hosting a custom foundation model.
- Enterprise-scale distributed tracing.
- A complex organization hierarchy or enterprise role system.
- Production-grade high availability across multiple regions.

These capabilities may be evaluated if real usage demonstrates a need.

---

## 2. Decision Status and Evidence

This document distinguishes three kinds of statements.

- **[CONFIRMED]** — A requirement explicitly provided during project discovery.
- **[RECOMMENDED]** — A proposed technical choice that should become the default unless the team identifies a concrete reason to change it.
- **[ASSUMED]** — An implementation detail not yet confirmed and therefore requiring validation during development.

A recommendation in this document is not evidence that the team has installed, configured, or deployed the corresponding technology.

### 2.1 Confirmed requirements

| Area | Confirmed requirement |
|---|---|
| Project stage | Starting from scratch |
| Team | Three people |
| Frontend | Next.js |
| Backend | Python FastAPI |
| Architecture | Modular monolith |
| Review ingestion | CSV and spreadsheet uploads initially |
| Dataset organization | Centralized review dataset with product and source associations |
| Analysis approach | Hybrid statistical/NLP processing with LLM use where justified |
| Long-running work | Background jobs |
| Authentication | Social sign-in is required |
| API | A documented API contract is required |
| Security | Basic security controls and audit records for important actions |
| LLM integration | Replaceable provider interface; hosted provider initially if appropriate |
| Frontend hosting | Vercel |
| Backend hosting | A separate backend host |
| Team ownership | Frontend, backend, and AI/ML role split |
| Scale | Small college prototype |
| Observability | Logs, job tracking, health checks, and basic metrics |

### 2.2 Recommended initial decisions

| Area | Recommended default | Reason |
|---|---|---|
| Backend structure | Feature modules with internal layers | Clear boundaries without excessive abstraction |
| Database | PostgreSQL | Relational integrity, query flexibility, and workspace isolation |
| Database access | SQLAlchemy 2.x with Alembic migrations | Explicit models and repeatable schema changes |
| Validation | Pydantic v2 | Structured validation for requests, responses, and configuration |
| Authentication | OpenID Connect/OAuth-based social sign-in through a compatible identity provider | Avoid implementing password and OAuth security from scratch |
| Authorization | Workspace-scoped access with a small role set | Prevent cross-account data exposure |
| Background jobs | Celery with Redis where the selected host supports both reliably | Established task queue pattern for longer-running work |
| File storage | Object storage for uploaded files; PostgreSQL for metadata and analysis results | Separates large binary files from transactional data |
| Job updates | Polling a job-status API initially | Simple deployment and debugging |
| API style | Versioned REST API under `/api/v1` | Straightforward integration and documentation |
| AI integration | Provider-neutral adapter around hosted LLM calls | Reduces provider lock-in |
| Quality checks | Progressive automation from linting to integration and security checks | Appropriate balance of rigor and setup cost |

The exact package versions, hosting provider, identity provider, and managed service plans should be selected and recorded when implementation begins. Do not invent or pin unverified versions in this architecture document.

### 2.3 Assumptions requiring validation

1. **[ASSUMED]** The prototype will initially serve a limited number of users and modest review datasets.
2. **[ASSUMED]** The application will support multiple users and may eventually support multiple businesses or workspaces.
3. **[ASSUMED]** Users will upload files they are authorized to process.
4. **[ASSUMED]** Review data can be retained in the application database for analysis and history, subject to the project's retention policy.
5. **[ASSUMED]** The chosen hosting providers will support the database connectivity, background worker execution, and object storage access required by this architecture.
6. **[ASSUMED]** AI-generated findings will be advisory and will not automatically make consequential business decisions.
7. **[ASSUMED]** Email notifications, external commerce integrations, and live review synchronization are future capabilities rather than initial requirements.

---

## 3. High-Level Architecture

ReviewPulse will use a modular monolith: one main backend application containing clearly separated feature modules, supported by a relational database and a background-processing subsystem.

The Next.js frontend and FastAPI backend will be deployed separately. Background workers will execute resource-intensive analysis outside the normal HTTP request lifecycle.

```text
Users
  |
  v
Next.js Frontend
(Vercel)
  |
  | HTTPS / JSON REST API
  v
FastAPI Application
  |
  +-- Authentication and Workspace Access
  |
  +-- Product and Review Management
  |
  +-- Upload and Ingestion
  |
  +-- Analysis Orchestration
  |
  +-- Evidence and Findings
  |
  +-- Reporting and Exports
  |
  +-- Audit and Health
  |
  +--------------------+
  |                    |
  v                    v
PostgreSQL          Task Queue
  |                 (Redis)
  |                    |
  |                    v
  |                Background Worker
  |                    |
  |                    +-- Data Validation
  |                    +-- NLP / Statistical Analysis
  |                    +-- Complaint Detection
  |                    +-- Claim Comparison
  |                    +-- Rating/Text Contradictions
  |                    +-- Optional LLM Calls
  |                    |
  +<-------------------+
  |
  +-- Products and Reviews
  +-- Job States and Results
  +-- Evidence References
  +-- Findings and Audit Records

Uploaded File Contents
  |
  v
Private Object Storage
  |
  +-- Original Uploads
  +-- Optional Processed Artifacts
```

**Important:** This diagram describes the target design. It is not a report of deployed or verified infrastructure.

### 3.1 Component responsibilities

| Component | Responsibility |
|---|---|
| Next.js frontend | Navigation, dashboards, upload workflows, filters, charts, findings, evidence views |
| FastAPI application | Authentication enforcement, authorization, input validation, business rules, API responses |
| PostgreSQL | Persistent application records, normalized reviews, jobs, analysis outputs, evidence links, audit records |
| Object storage | Original upload files and optional large artifacts |
| Task queue | Dispatch background tasks and coordinate their execution |
| Background worker | Validate datasets and execute analysis pipelines |
| NLP/statistical modules | Compute measurable review and product signals |
| LLM adapter | Optional language-model tasks with bounded inputs and structured outputs |
| Identity provider | Social sign-in and identity verification |
| Logging and metrics | Diagnose errors, track jobs, and assess system health |

### 3.2 Architectural principles

- Keep business rules in the backend, not duplicated across frontend components.
- Keep the initial backend deployable as one application, with a separate worker process if supported by the host.
- Do not make the frontend connect directly to the database, Redis, or object storage credentials.
- Use asynchronous jobs for processing that may exceed a short HTTP request.
- Keep data ingestion, analysis, evidence storage, and presentation independently testable.
- Prefer simple interfaces over premature abstractions.
- Add a new service only when a concrete scaling, reliability, or ownership requirement justifies it.

---

## 4. Proposed Repository Structure

The following is a proposed starting layout, not a verified description of an existing repository. The team may adapt it to the actual repository conventions before implementation.

```text
reviewpulse/
├── frontend/
│   ├── app/
│   │   ├── (auth)/
│   │   ├── (dashboard)/
│   │   ├── api/                 # Only if frontend proxy routes are needed
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── ui/
│   │   ├── charts/
│   │   ├── evidence/
│   │   └── features/
│   ├── lib/
│   │   ├── api-client.ts
│   │   ├── auth.ts
│   │   └── validation.ts
│   ├── public/
│   ├── tests/
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── logging.py
│   │   │   └── errors.py
│   │   ├── api/
│   │   │   ├── router.py
│   │   │   └── dependencies.py
│   │   ├── db/
│   │   │   ├── session.py
│   │   │   ├── base.py
│   │   │   └── models/
│   │   ├── modules/
│   │   │   ├── auth/
│   │   │   ├── workspaces/
│   │   │   ├── products/
│   │   │   ├── reviews/
│   │   │   ├── ingestion/
│   │   │   ├── analysis/
│   │   │   ├── findings/
│   │   │   ├── evidence/
│   │   │   ├── reports/
│   │   │   ├── notifications/
│   │   │   └── audit/
│   │   ├── workers/
│   │   │   ├── celery_app.py
│   │   │   └── tasks/
│   │   └── integrations/
│   │       ├── llm/
│   │       └── storage/
│   ├── migrations/
│   ├── tests/
│   ├── alembic.ini
│   └── pyproject.toml
│
├── docs/
│   ├── SYSTEM_ARCHITECTURE.md
│   ├── DATA_SCHEMA.md
│   ├── API_CONTRACTS.md
│   ├── INNOVATION_SPECIFICATIONS.md
│   ├── TEAM_WORKFLOW.md
│   ├── TESTING_AND_VALIDATION.md
│   └── DECISION_LOG.md
│
├── .github/
│   └── workflows/
├── .env.example
├── .gitignore
└── README.md
```

### 4.1 Backend module convention

Each substantial feature module should use a consistent internal structure. Avoid creating every possible layer for trivial modules; add a layer when it clarifies a real responsibility.

```text
modules/<feature>/
├── router.py       # HTTP routes and request/response handling
├── schemas.py      # Pydantic request and response schemas
├── service.py      # Business logic and orchestration
├── repository.py   # Database queries and persistence
├── models.py       # Feature-specific ORM models, when appropriate
└── tests/
```

Analysis code may need a separate internal structure:

```text
modules/analysis/
├── router.py
├── schemas.py
├── service.py
├── pipeline.py
├── metrics.py
├── evidence.py
├── detectors/
│   ├── complaint_spikes.py
│   ├── promise_reality.py
│   ├── rating_text_conflicts.py
│   └── review_reliability.py
├── providers/
│   └── llm_adapter.py
└── tests/
```

**Dependency rule:** routers call services; services use repositories and domain logic; repositories manage persistence. Analysis detectors should not depend on FastAPI request objects or frontend-specific data structures.

---

## 5. Backend Architecture and API Boundaries

### 5.1 Modular monolith

The FastAPI application should remain a single logical backend with feature modules. The worker may run as a separate process using the same codebase and domain modules.

Benefits for this team:

- One shared domain model.
- Easier local development and debugging.
- Clear module ownership without distributed-service overhead.
- Straightforward database transactions and migrations.
- A path to extract specific modules into services later if proven necessary.

Avoid circular imports between modules. Cross-module operations should use explicit service interfaces rather than reaching into another module's internal repository implementation.

### 5.2 API conventions

**[RECOMMENDED]** Use versioned REST endpoints under `/api/v1`.

General rules:

- JSON request and response bodies, except for upload endpoints.
- Explicit request and response schemas.
- Consistent error response structures.
- UTC timestamps in API responses, serialized using ISO 8601.
- Stable identifiers for products, reviews, uploads, jobs, findings, and evidence.
- Pagination for review lists and other potentially large results.
- Server-side authorization for every protected resource.
- Filters validated by the backend, even if the frontend also validates them.
- API documentation generated from FastAPI's OpenAPI support.

Example endpoint groups:

| Resource | Example routes | Purpose |
|---|---|---|
| Health | `GET /health/live`, `GET /health/ready` | Process and dependency health |
| Current user | `GET /api/v1/me` | Authenticated user context |
| Workspaces | `GET /api/v1/workspaces` | Accessible workspaces |
| Products | `GET /api/v1/products` | List and create products |
| Product detail | `GET /api/v1/products/{product_id}` | Product details and summary |
| Reviews | `GET /api/v1/products/{product_id}/reviews` | Paginated review exploration |
| Uploads | `POST /api/v1/uploads` | Register or initiate an upload |
| Ingestion jobs | `POST /api/v1/ingestion-jobs` | Validate and import uploaded data |
| Jobs | `GET /api/v1/jobs/{job_id}` | Retrieve job status and progress |
| Analysis | `POST /api/v1/products/{product_id}/analysis-jobs` | Request analysis |
| Findings | `GET /api/v1/products/{product_id}/findings` | Retrieve generated findings |
| Evidence | `GET /api/v1/findings/{finding_id}/evidence` | Retrieve supporting review evidence |
| Audit | Internal or restricted query interface | Authorized audit review |

These are proposed endpoint shapes, not finalized API contracts. Confirm request schemas, response bodies, status codes, pagination, and authorization rules in `API_CONTRACTS.md` before parallel implementation.

### 5.3 API error format

Use one predictable error format throughout the backend.

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The uploaded file contains invalid review rows.",
    "request_id": "request-correlation-id",
    "details": [
      {
        "field": "rating",
        "message": "Rating must be within the supported range."
      }
    ]
  }
}
```

Do not expose stack traces, database details, secret values, provider responses containing sensitive data, or internal file paths to the browser.

---

## 6. Authentication, Authorization, and Workspace Isolation

### 6.1 Social sign-in

**[CONFIRMED]** Social sign-in is required.

**[RECOMMENDED]** Use an established identity provider supporting OAuth 2.0 and OpenID Connect rather than implementing provider login and token validation from scratch.

The chosen provider and its supported Next.js/FastAPI integration must be evaluated before implementation. The frontend and backend must agree on the session and access-token strategy.

Responsibilities:

1. Redirect the user through the provider's authorization flow.
2. Validate the authentication response using the supported library or server-side integration.
3. Establish the application's authenticated session.
4. Resolve the corresponding ReviewPulse user record.
5. Verify workspace membership for every workspace-scoped operation.
6. Provide sign-out and session-expiration handling.

Never treat a user ID or workspace ID supplied by the browser as proof of authorization.

### 6.2 Session strategy

**[RECOMMENDED]** Prefer a secure server-managed session or a carefully designed backend-validated token strategy.

If browser cookies are used, configure them appropriately for the deployment:

- `HttpOnly`
- `Secure` in HTTPS environments
- Appropriate `SameSite` policy
- Narrow cookie scope
- CSRF protections for cookie-authenticated state-changing operations where applicable

If the frontend and backend are deployed on different origins, assess cookie behavior, CORS, CSRF, and token handling together. Do not store long-lived authentication tokens in browser local storage by default.

### 6.3 Minimum permission model

Start with a small role set:

- **Owner:** manages the workspace and its membership.
- **Member:** accesses permitted products, uploads, reviews, and analysis within the workspace.

Additional roles should be introduced only when actual workflows require them.

### 6.4 Workspace isolation

Use explicit ownership relationships for all workspace data.

Every workspace-owned product, upload, job, finding, and report must be associated with a workspace. Reviews should be reachable only through an authorized workspace/product relationship.

Authorization must be enforced on the server for reads, writes, downloads, exports, and background-job results.

Tests must verify that a user from Workspace A cannot access records belonging to Workspace B by substituting identifiers in a URL or request body.

### 6.5 Authentication is not authorization

A successfully authenticated user is not automatically permitted to access every product, upload, finding, or evidence record. Every protected request must validate both identity and resource permissions.

---

## 7. Data Architecture

### 7.1 Database recommendation

**[RECOMMENDED]** Use PostgreSQL as the primary relational database.

Why:

- Product, review, workspace, job, finding, and evidence records have clear relationships.
- Referential integrity is important for preserving evidence links.
- Filtering, grouping, aggregation, and pagination are central product requirements.
- Workspace-level ownership can be represented explicitly.
- PostgreSQL supports a practical migration path from a prototype to a more capable hosted application.

SQLite may be useful for isolated experiments or unit tests, but it should not be the default shared production database for this multi-user architecture.

The final database hosting choice remains open. Evaluate cost, connection limits, backups, TLS, migration support, and compatibility with the backend host.

### 7.2 Core entities

The initial schema should cover the following logical entities. Exact columns and constraints belong in `DATA_SCHEMA.md`.

| Entity | Purpose |
|---|---|
| `users` | Application user identity and profile metadata |
| `workspaces` | Business or project boundary for data isolation |
| `workspace_memberships` | User-to-workspace membership and role |
| `products` | Product identity, category, and metadata |
| `product_claims` | Product promises or claims used in comparisons |
| `reviews` | Normalized review text, rating, date, source, and product association |
| `uploads` | Original file metadata, checksum, storage reference, and uploader |
| `ingestion_jobs` | File validation and import execution history |
| `analysis_jobs` | Analysis requests, configuration, status, and execution history |
| `findings` | Product-level or review-level detected issues and insights |
| `finding_evidence` | Links between findings and supporting reviews or claim records |
| `analysis_runs` | Algorithm/model version, parameters, time window, and provenance |
| `saved_insights` | User-saved findings or comparisons, if implemented |
| `notifications` | In-app notification records, if implemented |
| `audit_events` | Important security and administrative events |

Avoid placing all entities into one unstructured JSON field. JSON columns may be useful for flexible metadata, but core relationships and frequently queried fields should have explicit columns.

### 7.3 Review data contract

The shared review contract must be agreed upon before parallel feature implementation.

Proposed raw fields:

- `review_id`
- `product_id`
- `product_name`
- `product_category`
- `rating`
- `review_title`
- `review_text`
- `review_date`
- `source`
- `product_url`
- `language`
- `language_confidence`

Product claims should be modeled separately where multiple claims can exist for one product. If claims are temporarily provided in a spreadsheet column, ingestion must normalize them into the internal claim representation.

Analysis outputs should not overwrite the original review text or rating.

Potential derived fields include:

- `readability_score`
- `readability_category`
- `topics`
- `primary_aspect`
- `helpfulness_score`
- `reliability_flags`
- `rating_text_conflict`

These values should be stored with sufficient provenance to identify which analysis run produced them.

Product-level derived metrics may include:

- `average_rating`
- `review_health_score`
- `top_positive_aspect`
- `top_negative_aspect`
- `complaint_spike_topic`
- `complaint_spike_ratio`
- `risk_level`
- `recommended_action`

Derived metrics should be reproducible from stored reviews and analysis configuration where practical. Define their formulas and limitations in `INNOVATION_SPECIFICATIONS.md`.

### 7.4 Data integrity

- Use stable identifiers instead of relying on row order.
- Define uniqueness rules for review identity within a product/source context.
- Validate rating ranges and date formats.
- Preserve source and import provenance.
- Handle missing text, duplicate rows, unsupported encodings, and malformed records explicitly.
- Use database constraints for critical relationships.
- Use transactions for logically atomic database updates.
- Use migrations for schema changes.
- Avoid silently discarding invalid rows; report counts and actionable reasons.

---

## 8. File Upload and Ingestion Architecture

### 8.1 Supported input

**[CONFIRMED]** CSV and spreadsheet uploads are the initial ingestion method.

Support CSV and XLSX initially. Add other spreadsheet formats only after confirming that the selected parsing library and the required formats are practical to support.

### 8.2 Upload processing sequence

1. The user selects a file and the target product or import context.
2. The backend authenticates the user and verifies workspace access.
3. The application validates the file extension, permitted MIME type, file size, and upload authorization.
4. The original file is stored in private object storage.
5. The database records upload metadata and its workspace association.
6. An ingestion job is created.
7. The worker parses the file and validates the column mapping.
8. The worker normalizes rows into the internal review schema.
9. Duplicate detection and validation rules are applied.
10. Valid records are persisted using bounded transactions or batches.
11. Import counts, rejected-row details, and job status are stored.
12. The frontend displays a completion summary and provides access to imported reviews.

The frontend must not assume that an upload is fully processed merely because the file transfer completed.

### 8.3 File storage trade-offs

| Option | Advantages | Disadvantages | Decision |
|---|---|---|---|
| Store file contents directly in PostgreSQL | Fewer infrastructure services; transactional metadata and content | Database growth, backup overhead, less convenient large-file delivery and lifecycle management | Not the default |
| Store files in private object storage and metadata in PostgreSQL | Better separation, scalable file storage, independent retention policies | Additional service configuration, access controls, and possible cost | Recommended |
| Store only metadata and delete originals immediately | Lower retained-file storage | Harder debugging, reprocessing, and auditability | Consider only with a deliberate retention policy |

**Default:** Keep original upload contents in private object storage and keep their metadata, checksum, owner, processing state, and storage key in PostgreSQL.

This recommendation assumes the deployment budget and hosting environment permit object storage. If that assumption fails, use a temporary prototype fallback with strict file-size limits and a documented migration plan. Do not store uploaded files on ephemeral application-host disks and assume they will remain available.

### 8.4 Upload security

- Generate storage keys server-side.
- Do not trust filenames supplied by the browser.
- Enforce upload size and parsing limits.
- Keep uploaded files private.
- Use short-lived signed URLs or backend-mediated downloads when appropriate.
- Never expose object-storage credentials to the frontend.
- Treat review text and spreadsheet cell contents as untrusted input.
- Prevent spreadsheet formula injection when exporting user-controlled text to CSV.
- Define retention and deletion behavior for source files and derived data.

---

## 9. Background Job Architecture

### 9.1 Why jobs are necessary

Importing spreadsheets, calculating product metrics, analyzing large review collections, and making hosted LLM requests can take longer than a normal HTTP request should remain open.

**[CONFIRMED]** Long-running processing must use background jobs.

### 9.2 Recommended job system

**[RECOMMENDED]** Start with Celery and Redis if the selected backend host supports a persistent worker and the required Redis service within the project budget.

This is a recommendation, not a confirmed dependency.

Before committing to the stack, verify that the selected services support:

- Persistent background worker processes.
- Reliable queue connectivity.
- Appropriate job timeouts.
- Operational logs.
- Restart and deployment behavior.
- Sufficient resource limits for spreadsheet and NLP workloads.

If Celery and Redis impose excessive operational overhead for the prototype, compare a simpler managed task service supported by the chosen host. Record the final choice in `DECISION_LOG.md`.

### 9.3 Job lifecycle

Use an explicit state machine.

```text
queued
  |
  v
running
  |
  +------> succeeded
  |
  +------> failed
  |
  +------> cancelled (if cancellation is implemented)
```

Optional additional state: `retrying`, if exposed by the job API.

Each job should track, where applicable:

- Job ID and type.
- Workspace and initiating user.
- Associated upload, product, or analysis run.
- Status.
- Creation, start, and completion timestamps.
- Current stage.
- Stage progress, if measurable.
- Attempt count.
- Machine-readable error code.
- Safe user-facing error message.
- Result references and row counts.

Do not display invented progress percentages. If the worker can report stages but cannot measure exact completion, show stages rather than a misleading percentage.

### 9.4 Reliability baseline

Implement these controls from the beginning:

1. Retry transient failures using a bounded retry policy.
2. Do not automatically retry permanent validation errors.
3. Apply explicit task timeouts and resource limits.
4. Make import and analysis tasks idempotent wherever practical.
5. Use unique task identifiers or idempotency keys where duplicate submissions could create duplicate results.
6. Record failed jobs and their sanitized reasons.
7. Allow an authorized user to restart eligible failed jobs.
8. Preserve enough history to diagnose repeated failures.
9. Prevent a worker crash from leaving a job indefinitely marked as running; use recovery or stale-job detection.
10. Keep provider rate limits and transient service failures separate from invalid user input.

A job must not be marked successful until its required database writes and result records have completed.

### 9.5 Job status API

A polling endpoint such as `GET /api/v1/jobs/{job_id}` should return the current status, stage, available progress information, timestamps, and safe error details.

**[RECOMMENDED]** Begin with polling at a modest interval and back off for long-running jobs. WebSockets or server-sent events are unnecessary until polling becomes a demonstrated limitation.

---

## 10. AI and Review Analysis Pipeline

### 10.1 Design principle

Use deterministic statistical and NLP techniques for tasks that can be reliably measured. Use an LLM only when language understanding or structured synthesis provides meaningful additional value.

An LLM response must not be treated as ground truth merely because it is fluent or confident.

### 10.2 Proposed processing stages

1. **Input validation:** Confirm that required review fields are present and valid.
2. **Normalization:** Normalize dates, ratings, whitespace, and source metadata while preserving original values where needed.
3. **Language analysis:** Detect language and record confidence where the selected method supports it.
4. **Text quality analysis:** Compute supported readability or text-quality measures.
5. **Topic/aspect analysis:** Identify recurring themes using suitable NLP or statistical techniques.
6. **Sentiment and polarity analysis:** Apply a documented approach with known limitations.
7. **Complaint trend detection:** Compare complaint counts or rates across defined time windows.
8. **Promise-versus-reality comparison:** Compare product claims with relevant review evidence.
9. **Rating–text contradiction detection:** Identify reviews where the numerical rating and written sentiment appear inconsistent.
10. **Reliability indicators:** Apply documented heuristics to identify reviews requiring closer examination.
11. **Optional LLM synthesis:** Produce a structured explanation or summary based on a bounded set of source evidence.
12. **Evidence validation:** Verify that cited review IDs exist and belong to the relevant analysis scope.
13. **Persistence:** Store findings, metrics, evidence links, analysis configuration, and model provenance.
14. **Presentation:** Expose the results through the API for the frontend.

Not every task must run for every dataset. The pipeline should support configuration and safe skipping of optional stages.

### 10.3 Provider-neutral LLM interface

Keep LLM-specific SDK calls inside a dedicated adapter.

Proposed interface:

```python
from typing import Protocol, Any


class LLMProvider(Protocol):
    def generate_structured(
        self,
        *,
        task: str,
        input_data: dict[str, Any],
        output_schema: dict[str, Any],
    ) -> dict[str, Any]:
        ...
```

This is an illustrative interface, not a complete implementation. A real adapter must also handle asynchronous calls where appropriate, timeouts, retry policies, token limits, structured-output validation, logging, and provider errors.

The rest of the application should depend on the application's own analysis schemas rather than a provider's response format.

### 10.4 Evidence-first findings

Each important finding should include, where applicable:

- Finding ID and type.
- Product and workspace association.
- Concise explanation.
- Supporting review identifiers.
- Relevant quoted text or safely rendered excerpts.
- Time window analyzed.
- Number of reviews analyzed.
- Number of supporting reviews.
- Baseline and comparison values for trend claims.
- Detection method and configuration.
- Analysis run ID.
- Confidence or uncertainty information, if meaningfully supported.
- Known limitations.

Evidence excerpts must remain linked to their source review. Never fabricate review text, URLs, sample counts, citations, or confidence values.

If the model returns an invalid review ID, the finding should be rejected or marked for validation rather than silently attaching unrelated evidence.

### 10.5 Statistical safeguards

- Define sample-size thresholds for complaint alerts.
- Distinguish a rise in complaint count from a rise in complaint rate.
- Compare equivalent time windows when possible.
- Handle sparse data and seasonality carefully.
- Expose the time window and sample size used for every major insight.
- Avoid describing correlation as causation.
- Distinguish a heuristic risk indicator from a confirmed conclusion.
- Record the algorithm version and parameters used to produce each result.
- Make recalculation possible when the algorithm or source dataset changes.

### 10.6 Reliability flags are not fraud determinations

Rating/text mismatches and unusual review patterns can help prioritize investigation. They do not establish fraud, manipulation, or reviewer intent.

Use cautious language such as “possible rating–text mismatch” or “review requires further examination.” Display the evidence and the limitations behind the flag.

---

## 11. Innovation Feature Boundaries

The four major innovations should be implemented as separate analysis modules that share the common review schema and evidence model.

### 11.1 Early-Warning Radar

**Purpose:** Identify emerging complaint patterns.

Responsibilities:

- Aggregate complaint topics over defined time windows.
- Compare current counts or rates against a documented baseline.
- Apply minimum sample-size requirements.
- Record the triggering metric, threshold, comparison window, and supporting reviews.
- Return an interpretable severity level without implying certainty beyond the data.

### 11.2 Promise vs. Reality

**Purpose:** Compare stated product claims with review evidence.

Responsibilities:

- Store product claims separately from review text.
- Identify evidence relevant to each claim.
- Summarize supporting and conflicting customer experiences.
- Report evidence counts and analysis scope.
- Distinguish direct evidence from model-generated interpretation.

### 11.3 Evidence-First AI Investigator

**Purpose:** Provide understandable findings grounded in review data.

Responsibilities:

- Accept a supported analysis task.
- Retrieve relevant reviews through authorized application logic.
- Generate a structured explanation when LLM use is justified.
- Validate every evidence reference.
- Store the finding and its provenance.
- Return supporting evidence through a dedicated API.

### 11.4 Rating–Reality Contradiction Detector

**Purpose:** Flag potential disagreement between star ratings and review text.

Responsibilities:

- Apply a documented sentiment/rating comparison rule.
- Record the rule or model version.
- Store the rating, relevant text, and mismatch reason.
- Avoid treating the mismatch as evidence of fraud by itself.
- Allow users to inspect the original review.

### 11.5 Shared module contract

All four modules should accept validated review/product data and produce structured findings. They must not implement separate copies of file parsing, authentication, workspace authorization, or evidence persistence.

Shared contracts should be defined in `INNOVATION_SPECIFICATIONS.md` and reviewed by all three team members before implementation.

---

## 12. Frontend Architecture

### 12.1 Responsibilities

The Next.js frontend is responsible for:

- Authentication and application navigation.
- Overview dashboard.
- Product selection and product details.
- Review explorer with filters and pagination.
- Early-Warning Radar views.
- Promise-versus-reality analysis.
- Evidence-First AI Investigator views.
- Rating–Reality contradiction views.
- Upload and ingestion progress.
- Analysis-job status and errors.
- Findings, evidence drawers, and supported exports.
- Settings and workspace management, as implemented.

The frontend may improve usability through client-side filtering or validation, but the backend remains authoritative for access control and persisted business rules.

### 12.2 API client

Use one shared API client layer to centralize:

- Base URL configuration.
- Session or token handling.
- Request cancellation.
- Response parsing.
- Error normalization.
- Request correlation where supported.
- Typed request and response contracts.

Avoid embedding API URLs and authentication logic independently throughout UI components.

### 12.3 State ownership

Use local component state for temporary interface behavior and a shared state/query strategy for server data when needed.

Examples of server-owned state include products, reviews, findings, jobs, and saved insights. These should be fetched through the API rather than treated as permanent browser-only records.

Filters may persist across navigation where product requirements specify this, but the frontend must reset or reconcile filters that are no longer valid for the selected product.

### 12.4 UX requirements that affect architecture

- Show loading skeletons while retrieving server data.
- Display real job stages when the backend provides them.
- Preserve filter values in a consistent manner.
- Expose clear empty, partial-success, and failure states.
- Provide access to the reviews supporting an insight.
- Do not mix demo data with real workspace data without a clear mode distinction.
- Make tables, filters, dialogs, charts, and evidence views keyboard-accessible.
- Respect reduced-motion preferences.
- Treat all review text as untrusted content when rendering it.

---

## 13. Security and Privacy

### 13.1 Baseline controls

Implement the following as part of the initial architecture:

- HTTPS for deployed application traffic.
- Server-side authentication and authorization.
- Workspace-level data isolation.
- Strict input validation.
- Upload limits and file-type validation.
- Private file storage.
- Parameterized database access through the chosen ORM or database layer.
- Secure secret management through deployment environment configuration.
- Safe error responses.
- Dependency updates and vulnerability review.
- Rate limits or equivalent abuse controls on sensitive and expensive endpoints.
- Audit records for important security and administrative actions.

### 13.2 Audit events

Record events such as:

- Authentication and account events when available.
- Workspace membership and permission changes.
- File uploads and deletions.
- Ingestion and analysis restarts.
- Data exports.
- Significant settings changes.
- Administrative actions.

Audit records should include the actor when known, action, target, timestamp, outcome, and relevant correlation identifiers. Avoid storing passwords, access tokens, full review contents, or unnecessary personal data in audit logs.

### 13.3 LLM data handling

Before sending review content to a hosted model provider:

1. Confirm that the selected provider and configuration are appropriate for the project's data-handling requirements.
2. Send only the minimum necessary text and metadata.
3. Avoid including user credentials, internal secrets, or unrelated workspace records.
4. Define how provider requests and outputs are logged.
5. Handle provider failures and rate limits without exposing sensitive information.
6. Document that model-generated outputs may be incorrect and require evidence validation.

### 13.4 Upload and export risks

- Prevent cross-workspace file access.
- Avoid path traversal and unsafe filename handling.
- Limit parser resource consumption.
- Sanitize filenames and exported cell values.
- Avoid publicly accessible storage buckets.
- Require authorization for downloads and exports.
- Define retention and deletion policies before accumulating real customer datasets.

---

## 14. Failure Handling and Recovery

### 14.1 Failure categories

| Failure | Handling |
|---|---|
| Invalid spreadsheet structure | Mark import failed or partially successful with actionable validation details |
| Invalid review rows | Report rejected-row counts and reasons |
| Database transient error | Retry only where safe and supported |
| LLM timeout or rate limit | Apply bounded retry/backoff where appropriate; preserve job status |
| Invalid LLM structured output | Validate, retry if justified, or fail the relevant stage safely |
| Worker interruption | Detect stale jobs and recover or mark them for restart |
| Object-storage failure | Return a safe error and preserve a diagnosable job state |
| Unauthorized request | Reject without exposing protected resource details |
| Missing evidence record | Reject the invalid reference or mark the result for review |
| Export failure | Report failure without presenting an incomplete export as successful |

### 14.2 Partial results

Where the pipeline supports partial success, record which stages completed and which failed. Do not label a complete analysis successful if a required stage failed.

Optional stages may be skipped only when the analysis contract explicitly permits it. The response should make missing analysis capabilities visible.

### 14.3 Retry safety

A retry must not blindly duplicate reviews, findings, audit records, or analysis runs. Use unique constraints, stable job identifiers, transactional writes, and explicit retry semantics where appropriate.

### 14.4 User-facing errors

Errors should explain:

- What failed.
- Whether the original upload or existing data remains safe.
- Whether retrying is possible.
- What the user can do next.

Internal stack traces belong in protected logs, not in the frontend response.

---

## 15. Observability and Operational Health

### 15.1 Logging

Use structured application logs with consistent fields where practical:

- Timestamp.
- Severity.
- Application component.
- Environment.
- Request or correlation ID.
- Job ID when applicable.
- Workspace ID only where safe and useful.
- Event name.
- Sanitized error code.

Do not log secrets, raw authentication headers, or entire uploaded files. Avoid logging full review text unless explicitly justified and safely controlled.

### 15.2 Health checks

Provide separate checks for:

- **Liveness:** The application process is alive.
- **Readiness:** The application can serve requests given its essential dependencies.

Readiness checks should be bounded and should not trigger expensive work. The worker should also emit a heartbeat or equivalent operational signal if the chosen task system supports it.

### 15.3 Job tracking

Track at least:

- Number of queued, running, succeeded, and failed jobs.
- Job duration by job type.
- Retry count.
- Ingestion row counts.
- Validation rejection counts.
- Analysis-stage failures.
- LLM request failures and latency when applicable.

Metrics should help the team identify stuck jobs, repeated failures, slow imports, and unexpectedly expensive model usage.

### 15.4 Initial monitoring scope

**[CONFIRMED]** The prototype needs logs, job tracking, health checks, and basic metrics.

**[RECOMMENDED]** Start with host-provided logs and health monitoring plus lightweight application metrics. Introduce external monitoring or distributed tracing only when the deployment or debugging needs justify the additional setup.

---

## 16. Deployment Architecture

### 16.1 Target deployment

**[CONFIRMED]** Deploy the frontend to Vercel and the backend separately.

Proposed deployment components:

1. Next.js frontend on Vercel.
2. FastAPI application on a host that supports persistent Python web services.
3. PostgreSQL managed or hosted separately.
4. Redis and a persistent worker if Celery is selected.
5. Private object storage for uploads.
6. Hosted identity provider for social sign-in.
7. Hosted LLM provider when enabled and appropriate.

The final provider choices depend on budget, availability, region, and service capabilities.

### 16.2 Environment separation

Use separate configuration for local development and deployed environments. Where practical, maintain distinct development, staging, and production settings.

Never commit real secrets.

Provide an `.env.example` containing variable names and safe placeholders, not real credentials.

Potential configuration variables include:

```text
APP_ENV=
FRONTEND_ORIGIN=
API_BASE_URL=
DATABASE_URL=
REDIS_URL=
AUTH_ISSUER_URL=
AUTH_CLIENT_ID=
AUTH_CLIENT_SECRET=
OBJECT_STORAGE_ENDPOINT=
OBJECT_STORAGE_BUCKET=
OBJECT_STORAGE_ACCESS_KEY=
OBJECT_STORAGE_SECRET_KEY=
LLM_PROVIDER=
LLM_API_KEY=
LOG_LEVEL=
```

Only configure variables used by the selected implementation. Secret names and authentication settings must follow the chosen provider's requirements.

### 16.3 CORS and cross-origin requests

Configure the FastAPI CORS policy to allow only the intended frontend origins. Do not use unrestricted origins with credentialed requests.

Verify authentication cookies or token handling, CSRF protections where applicable, and production domain configuration together.

### 16.4 Database migrations

Use a versioned migration tool such as Alembic.

- Commit migrations with the code changes they support.
- Test migrations against a disposable test database.
- Avoid relying on automatic table creation at application startup.
- Document the deployment order for breaking schema changes.
- Ensure rollback or forward-fix procedures are considered before production changes.

### 16.5 Deployment limitations to validate

Before selecting providers, verify:

- Worker processes can run persistently.
- Request and upload limits fit the intended dataset size.
- Timeouts are compatible with upload and API operations.
- Database connection limits are sufficient.
- Object storage is private and reachable by the backend.
- Scheduled cleanup and stale-job recovery are supported if required.
- Provider secrets are available only to the components that need them.

---

## 17. Three-Person Team Ownership

The team will use a frontend/backend/AI-ML role split with shared API and data contracts.

### Member 1 — Frontend

**Primary ownership**

- Next.js application structure and routing.
- Dashboard and navigation.
- Product and review interfaces.
- Charts, filters, tables, and evidence panels.
- Upload and job-status experiences.
- Authentication integration on the frontend.
- Accessibility and responsive behavior.
- Frontend tests and deployment configuration.

**Dependencies**

- Agreed API request and response contracts.
- Agreed authentication/session approach.
- Stable review, finding, and evidence schemas.

### Member 2 — Backend and platform

**Primary ownership**

- FastAPI application and feature modules.
- Database schema, models, and migrations.
- Authentication enforcement and workspace authorization.
- Upload registration and ingestion orchestration.
- Job lifecycle and persistence.
- API documentation and error formats.
- Audit events, health checks, and operational logging.
- Backend tests and deployment configuration.

**Dependencies**

- Shared data schema.
- Analysis interfaces defined with Member 3.
- Frontend API requirements.
- Final hosting and storage decisions.

### Member 3 — AI/ML and analysis

**Primary ownership**

- Review normalization requirements for analysis.
- NLP and statistical feature modules.
- Early-Warning Radar detection logic.
- Promise-versus-reality analysis.
- Rating–text contradiction detection.
- Evidence selection and analysis provenance.
- LLM provider adapter and structured-output validation.
- Analysis tests, evaluation examples, and documented limitations.

**Dependencies**

- Shared review schema.
- Backend persistence and job interfaces.
- Agreed definitions for product metrics and findings.
- Authorized access to analysis inputs and outputs.

### 17.1 Shared ownership

All members are responsible for:

- Reviewing changes that affect shared contracts.
- Maintaining the common data schema.
- Participating in pull-request reviews.
- Keeping documentation aligned with implementation.
- Testing cross-module integration.
- Avoiding undocumented schema or API changes.
- Agreeing on changes to security, persistence, or deployment boundaries.

Role ownership does not mean that one member may independently change shared contracts without review.

---

## 18. Development Workflow and Integration Rules

### 18.1 Contract-first development

Before implementing feature modules in parallel, agree on:

1. Core review and product schema.
2. Workspace ownership and authorization model.
3. Upload and ingestion job lifecycle.
4. Analysis job request and status response.
5. Finding and evidence response formats.
6. Error response format.
7. API naming and pagination conventions.

Record the approved contracts in `DATA_SCHEMA.md` and `API_CONTRACTS.md`.

### 18.2 Git workflow

**[RECOMMENDED]** Use a shared integration branch and short-lived feature branches.

A possible convention is:

```text
main
develop
feature/frontend-dashboard
feature/backend-api
feature/ai-analysis
```

This is a proposed branch scheme. Adapt it to the repository's actual state and the team's workflow before using it.

Rules:

- Pull the latest integration branch before beginning work.
- Keep feature branches focused.
- Commit meaningful, reviewable changes.
- Open pull requests for shared-branch integration.
- Request at least one teammate review for changes affecting contracts, security, persistence, or shared infrastructure.
- Run required quality checks before merging.
- Update the relevant documentation when an approved decision changes.

### 18.3 API change process

Any breaking API or schema change must be communicated to the other owners before implementation is merged.

Prefer additive changes during parallel development. If a breaking change is necessary, update the contract, affected tests, and dependent implementation together.

### 18.4 Demo data

Sample or synthetic review datasets may be used to unblock frontend and analysis development. They must be clearly identified as test data and must not be presented as genuine user-uploaded evidence.

---

## 19. Staged Quality Assurance Strategy

### Stage 1 — Local development baseline

**Required first**

- Formatting and linting for frontend and backend.
- Type checking where applicable.
- Basic unit tests for shared logic.
- Frontend production build.
- Backend application startup and route validation.
- Environment-variable validation.
- Basic tests for input validation and error responses.

### Stage 2 — Feature-level testing

Before each feature is considered complete:

- Test successful requests and expected responses.
- Test invalid input.
- Test missing or malformed fields.
- Test empty datasets.
- Test duplicate records.
- Test loading, empty, partial-success, and failure UI states.
- Test job failure and retry behavior where applicable.
- Test the analysis module against representative examples.

### Stage 3 — Integration testing

Once frontend, backend, and AI/ML modules are connected:

- Test the complete CSV/XLSX ingestion workflow.
- Verify imported review counts and rejected-row reporting.
- Verify database relationships and migrations.
- Test analysis-job submission and status polling.
- Verify findings reference the correct reviews.
- Verify frontend error handling for backend and provider failures.
- Verify workspace isolation.
- Verify exports do not corrupt or misrepresent review data.

### Stage 4 — Security and reliability checks

Before external demonstrations using real user data, and before any production release:

- Check dependencies for known vulnerabilities.
- Test unauthorized access and cross-workspace access.
- Test upload limits and invalid file types.
- Review secret handling and CORS configuration.
- Verify that sensitive data is absent from ordinary logs.
- Test worker interruption and retry safety.
- Test stale-job recovery.
- Verify private storage and authorized downloads.
- Validate database backup and restoration procedures if persistent real data is retained.

### Stage 5 — Continuous integration

**[RECOMMENDED]** Add CI in increments.

Initial CI:

- Frontend lint and type checks.
- Frontend production build.
- Backend lint and tests.
- Basic schema or migration validation.

Next, add:

- API integration tests.
- Database migration tests against a disposable database.
- Security and dependency scanning.
- Targeted end-to-end tests for upload, analysis, and evidence retrieval.

Do not require expensive external LLM calls in every ordinary unit-test run. Use mocked provider responses for deterministic tests and maintain a small, deliberate integration/evaluation suite for provider-dependent behavior.

### Definition of done

A feature is not complete solely because its UI or endpoint renders.

A feature should include:

- Agreed behavior and contract.
- Input validation.
- Authorization checks where needed.
- Error and empty states.
- Tests appropriate to its risk.
- Relevant documentation.
- Evidence of successful integration when the feature crosses module boundaries.

---

## 20. Performance and Scaling Strategy

The prototype should optimize for correctness and simplicity first, while avoiding decisions that create unnecessary migration work.

### 20.1 Initial performance measures

- Paginate review lists.
- Apply filtering and aggregation in the backend for large datasets.
- Add database indexes based on actual query patterns.
- Use bounded batch sizes for spreadsheet imports.
- Avoid loading every review into the frontend at once.
- Limit concurrency for expensive NLP or LLM stages.
- Cache only results whose freshness and invalidation rules are clear.
- Keep uploaded binary content out of ordinary database query responses.
- Track job duration and dataset size to guide optimization.

### 20.2 Growth path

| Stage | Likely changes |
|---|---|
| College prototype | Single modular backend, one database, private object storage, a small worker setup |
| Early multi-user MVP | Stronger workspace authorization tests, managed backups, quotas, improved monitoring, more complete CI |
| Growing datasets | Database indexes and query tuning, larger worker capacity, improved batching, selective caching |
| Higher analysis volume | Queue tuning, controlled worker concurrency, dedicated analysis resources if justified |
| Commercial SaaS | Formal retention and deletion controls, operational alerting, stronger incident procedures, capacity planning and service-level targets |

Do not split the modular monolith into microservices solely in anticipation of growth. Extract a module only when there is a demonstrated need for independent scaling, deployment, fault isolation, or ownership.

---

## 21. Implementation Roadmap

The following order is recommended to minimize integration risk.

### Phase 1 — Foundations

- Establish the repository structure.
- Confirm package managers and supported versions.
- Create frontend and backend applications.
- Define environment configuration.
- Agree on the initial database and migration workflow.
- Finalize the shared review and product schemas.
- Finalize the first API contracts.
- Establish linting, formatting, and baseline tests.

**Exit criterion:** All three members can run their assigned application or module locally, and shared contracts are documented.

### Phase 2 — Identity and core data

- Integrate social sign-in.
- Implement users, workspaces, and memberships.
- Enforce workspace-scoped authorization.
- Implement products and review persistence.
- Create the upload metadata model.
- Add basic audit events.

**Exit criterion:** An authenticated user can access only the records belonging to an authorized workspace.

### Phase 3 — Ingestion and background processing

- Implement CSV and XLSX validation.
- Configure private file storage.
- Create ingestion jobs and job-status endpoints.
- Implement normalization and duplicate handling.
- Persist valid reviews and validation summaries.
- Add failure handling and retry-safe operations.

**Exit criterion:** A user can upload a supported file, track its import job, and inspect the resulting reviews or validation errors.

### Phase 4 — Analysis and evidence

- Implement baseline NLP and statistical functions.
- Define the analysis-run schema.
- Implement all four innovation modules incrementally.
- Establish the LLM adapter if justified.
- Store findings and review evidence references.
- Add deterministic tests and representative evaluation examples.

**Exit criterion:** Each finding can be traced to its analysis run and the source evidence used to support it.

### Phase 5 — Frontend integration

- Implement the dashboard shell and navigation.
- Add product selection and review exploration.
- Add ingestion progress and job failure handling.
- Add innovation feature views.
- Implement evidence drawers and interactive charts.
- Add loading, empty, and error states.
- Verify accessibility and responsive behavior.

**Exit criterion:** The frontend consumes real backend contracts end to end without depending on hard-coded production findings.

### Phase 6 — Reliability and deployment

- Configure Vercel deployment.
- Deploy the FastAPI application and required worker.
- Configure the database, object storage, and queue services.
- Verify production authentication, CORS, and secret handling.
- Enable health checks, logs, and basic metrics.
- Add integration CI and security checks.
- Test a full upload-to-evidence workflow in the deployed environment.

**Exit criterion:** The team can demonstrate the end-to-end product, explain its data lineage, and diagnose expected failure cases.

---

## 22. Architecture Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Three contributors implement incompatible schemas | Agree on shared contracts before parallel feature work |
| Frontend and backend authentication disagree | Decide the session/token strategy before protected API implementation |
| Background jobs duplicate data on retries | Use idempotency, uniqueness constraints, and transactional writes |
| Large files overload application memory | Enforce limits and use bounded streaming or batch processing where supported |
| Uploaded files become inaccessible after deployment | Use durable private object storage instead of relying on ephemeral local disks |
| AI findings cite unrelated or nonexistent reviews | Validate evidence IDs against the authorized analysis dataset |
| LLM costs become unpredictable | Set usage limits, bound context, track usage, and prefer deterministic analysis when sufficient |
| Workspace data leaks through identifiers | Enforce authorization at every resource access and test cross-workspace attacks |
| Deployment host cannot run a persistent worker | Validate host capabilities before selecting the job system |
| Prototype architecture becomes too complex | Keep a modular monolith and introduce infrastructure only when justified |
| Review-reliability flags are misinterpreted | Use cautious language, show evidence, and document the limits of heuristics |
| Analysis outputs become irreproducible | Store run configuration, detector/model version, time window, and source references |

---

## 23. Decisions Still Requiring Approval

The following decisions should be finalized and recorded in `DECISION_LOG.md` as implementation begins.

| Decision | Default recommendation | Validation required |
|---|---|---|
| Database provider | PostgreSQL | Budget, connection limits, backups, and host compatibility |
| ORM and migrations | SQLAlchemy 2.x and Alembic | Team familiarity and compatible versions |
| Identity provider | OIDC-compatible social sign-in provider | Available login methods, pricing, redirect configuration, and session integration |
| Session design | Secure server-managed session or validated token strategy | Frontend/backend origins and deployment constraints |
| Background jobs | Celery and Redis | Persistent worker support and operational cost |
| File storage | Private object storage | Provider availability, cost, lifecycle, and signed access |
| Job updates | HTTP polling | Expected job duration and UI update needs |
| LLM provider | Hosted provider behind an adapter | Privacy terms, supported structured outputs, budget, and rate limits |
| Review retention | Documented retention policy | Data rights, privacy expectations, and reprocessing needs |
| Analysis thresholds | Explicit minimum sample sizes and comparison windows | Representative test data and evaluation results |
| Deployment provider | Vercel plus a compatible FastAPI host | Region, worker support, budget, and operational limits |

These decisions should not block writing feature contracts or building independent prototypes, but dependent production implementations should not proceed on incompatible assumptions.

---

## 24. Final Architecture Summary

ReviewPulse should begin as a **modular monolith with a separately deployed Next.js frontend and FastAPI backend**. PostgreSQL is the recommended system of record, private object storage is the recommended location for original uploaded files, and a background worker handles ingestion and analysis outside the request lifecycle.

The three-person team should own frontend, backend/platform, and AI/ML responsibilities while sharing responsibility for API contracts, review schemas, testing, and integration. The analysis pipeline should combine reproducible statistical and NLP methods with selective LLM use. Every important finding should preserve its provenance and link to the source review evidence.

The initial system should prioritize:

1. Reliable CSV/XLSX ingestion.
2. Clear product, review, workspace, and job contracts.
3. Secure social sign-in and workspace-level authorization.
4. Retry-safe background processing.
5. Evidence-backed, appropriately qualified analysis.
6. Automated quality checks and useful operational visibility.
7. A straightforward deployment and a documented path for future growth.

The architecture remains a proposal until the team approves the outstanding choices and implements them. Update this document when a material decision changes, and record the reason for the change rather than allowing the architecture and codebase to drift apart.

---

## 25. Change Policy

When changing this document:

1. Identify whether the change affects a confirmed requirement, recommendation, or assumption.
2. Explain the technical or project reason.
3. Update affected API, data, security, deployment, and testing documents.
4. Notify the owners of dependent modules.
5. Record material architectural decisions in `DECISION_LOG.md`.
6. Keep the documentation aligned with the implemented system.

**Document ends — `SYSTEM_ARCHITECTURE.md`**