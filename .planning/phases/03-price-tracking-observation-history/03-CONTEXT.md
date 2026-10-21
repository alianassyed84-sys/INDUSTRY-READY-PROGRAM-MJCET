# Phase 3: Price Tracking & Observation History - Context

**Gathered:** 2026-10-21
**Status:** Ready for execution
**Mode:** Smart Discuss (Autonomous)

<domain>
## Phase Boundary

Record price observations over time and provide price movement metrics for catalog products without introducing heavyweight message queues or unverified web scrapers.
</domain>

<decisions>
## Implementation Decisions

### Snapshot Deduplication
- Consecutive observations matching on price, original price, currency, and source return the existing snapshot rather than creating duplicate rows in the database.

### Peak & Baseline Semantics
- Single observations within a requested time window are treated strictly as a baseline, setting `is_historical_peak = False` and populating an explicit explanatory `status_note`. Multiple observations are required before establishing a historical peak.

### Multi-Currency Calculation Safety
- Cross-currency mathematics is prevented; when multiple currencies appear in a product's price history, analytical metrics (first price, latest price, change amount, percentage delta) are calculated strictly against records matching the primary observation currency.

### External Provider Safety & Polling Model
- In the absence of live Amazon credentials, tests use `MockProductDataProvider`, and live requests raise `ProviderNotConfiguredError`. Live web scraping is forbidden per DEC-001.
</decisions>

<code_context>
## Existing Code Insights

- **Data Models**: `app.models.price_snapshot.PriceSnapshot` provides persistence with columns for `product_id`, `price`, `original_price`, `currency`, `source`, and `observed_at`.
- **Service Layer**: `app.services.harvester.price_history` exposes `record_price_snapshot`, `get_price_history`, and `poll_product_price`.
- **API Endpoints**: `app.api.v1.harvester` exposes `GET /api/v1/harvester/products/{id}/price-history` and `POST /api/v1/harvester/products/{id}/check-price`.
- **Test Suite**: `backend/tests/test_milestone7_price_tracking.py` contains 16 comprehensive test cases covering deduplication, analytics, multi-currency guards, date filtering, and API contracts.
</code_context>

<specifics>
## Specific Ideas

- Ensure all responses serialize timestamps in ISO-8601 UTC format.
- Gracefully handle nonexistent products with HTTP 404.
- Validate date range ordering (`start_date <= end_date`) with HTTP 422.
</specifics>

<deferred>
## Deferred Ideas

- Background task worker daemon (ARQ / Redis) for scheduled continuous price polling across the full product catalog.
</deferred>
