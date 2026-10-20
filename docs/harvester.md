# ReviewPulse — Review Harvester

## 1. Overview

The **Review Harvester** module imports and normalizes product review datasets into the ReviewPulse persistence layer. It persists `Product`, `User`, `Review`, and `CollectionJob` records using PostgreSQL (via SQLAlchemy 2.x async / `asyncpg`) or in-memory SQLite for tests.

## 2. Supported Sources & Limitations

### 2.1 Supported Sources
- **`csv_amazon`**: Bundled Amazon product reviews CSV dataset (1,465 rows, 1,351 unique products, ~9k reviews).
- External scraping or live API sources are explicitly stubbed or deferred due to absence of external API credentials.

### 2.2 CSV Import Configuration
The CSV path can be provided per request or via environment settings:
- Environment variable: `AMAZON_CSV_PATH`
- Request field: `csv_path` in `POST /api/v1/harvester/jobs`

### 2.3 Known Limitations
1. **Synchronous Execution**: Import runs synchronously within the request context (~0.5–2s for the 1,465-row dataset). Background task workers (e.g. Celery/ARQ) are deferred to subsequent milestones.
2. **Review Content Comma Splitting**: In the raw dataset, `review_content` contains internal commas that prevent deterministic multi-review alignment. As a documented design decision, the entire content blob is assigned to the first review in each multi-review row; secondary reviews have `review_content=None`.

## 3. Job Lifecycle

1. **Submission**: Client posts to `POST /api/v1/harvester/jobs`.
2. **Creation**: A `CollectionJob` record is initialized with status `pending`.
3. **Execution**: The CSV is streamed row-by-row, parsing and upserting products, users, and reviews idempotently.
4. **Completion**: Upon finishing, status updates to `done` (or `failed` if an unrecoverable exception occurs), tracking counts for items seen and inserted.

## 4. API Reference

### `POST /api/v1/harvester/jobs`
Start an import job synchronously.
- **Request Body**:
  - `source`: Literal `"csv_amazon"` (required)
  - `csv_path`: Optional string path to CSV override
- **Response**: `JobStatusResponse` (status code 202)

### `GET /api/v1/harvester/jobs/{job_id}`
Fetch the current status and metrics of a collection job.

### `GET /api/v1/harvester/products`
Fetch paginated list of products.
- Query parameters:
  - `limit`: Integer (1–100, default 20)
  - `offset`: Integer (>= 0, default 0)

### `GET /api/v1/harvester/products/{product_id}`
Fetch detailed product information.

### `GET /api/v1/harvester/products/{product_id}/insights`
Fetch aggregated review intelligence, sentiment breakdown, top TF-IDF topics, ratings distribution, and readability metrics for a product.
- Query parameters:
  - `limit`: Integer (1–500, default 100) — maximum reviews sampled for analysis
  - `aspects`: Optional comma-separated string (e.g. `quality,battery,price`) for aspect-based sentiment polarity


### `GET /api/v1/harvester/reviews`
Fetch paginated list of reviews.
- Query parameters:
  - `product_id`: Optional string filter
  - `limit`: Integer (1–100, default 20)
  - `offset`: Integer (>= 0, default 0)

## 5. Testing & Verification

Run the test suite and quality checks from the `backend/` directory:

```powershell
python -m pytest
python -m ruff check .
python -m ruff format --check .
```
