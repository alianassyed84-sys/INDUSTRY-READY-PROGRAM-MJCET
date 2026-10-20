# ReviewPulse — Price Tracking & Monitoring Architecture (Milestone 7)

## 1. Overview & Infrastructure Audit

### 1.1 Existing Infrastructure Findings
- **Scheduler Audit**: Inspection of dependencies (`pyproject.toml`, `uv.lock`) and application code confirms that **no background job infrastructure or task scheduler** (such as Celery, ARQ, Redis Queue, or APScheduler) is currently installed.
- **Synchronous Execution Model**: Existing collection jobs and URL analyses run synchronously within the HTTP request lifecycle.
- **Architectural Policy**: In alignment with minimal-diff engineering (Ponytail ladder), a heavyweight background queue is **not introduced without explicit infrastructure sign-off**. Instead, ReviewPulse provides:
  1. A stateless polling service (`poll_product_price`) in `app.services.harvester.price_history`.
  2. On-demand API endpoints:
     - `GET /api/v1/harvester/products/{product_id}/price-history`
     - `POST /api/v1/harvester/products/{product_id}/check-price`
  3. This documented target architecture for production background scheduling.

---

## 2. Production Scheduler Design

### 2.1 Proposed Background Architecture (Target State)
When production Redis or PostgreSQL message brokers are provisioned, price monitoring should be implemented via **ARQ** (async Redis queue) or a cron daemon:

```
┌────────────────────────┐      ┌───────────────────────────┐      ┌────────────────────────┐
│  Periodic Cron Worker  │ ───► │  Price Monitor Job Queue  │ ───► │ Worker: poll_product_  │
│  (e.g., 0 */12 * * *)  │      │  (Rate-Limited Leaky Bkt) │      │ price(session, prod)   │
└────────────────────────┘      └───────────────────────────┘      └───────────┬────────────┘
                                                                               │
                                                                               ▼
                                                                   ┌────────────────────────┐
                                                                   │ DB: PriceSnapshot      │
                                                                   │ (deduped, timestamped) │
                                                                   └────────────────────────┘
```

### 2.2 Rate Limit & Quota Governance
- **Amazon PA-API 5.0 Constraints**:
  - Maximum request rate: **1 request per second (TPS)** per account.
  - Daily request allowance: Begins at **8,640 requests per day** and scales based on qualifying revenue generated in the past 30 days.
  - Concurrency rule: Scheduled workers must enforce a token-bucket rate limiter with a 1-second replenishment interval to prevent HTTP 429 throttling.
- **Provider Priority & Fallback**:
  - Products with active user watchlists are prioritized in the queue over low-traffic catalog items.

### 2.3 Data Integrity & Deduplication Rules
1. **Deduplication**: If the provider returns a price, original price, and currency identical to the most recent recorded observation, no duplicate row is created.
2. **Multi-Currency Protection**: When price history contains multiple currencies, statistics (price change, min/max, percent delta) are strictly calculated across snapshots matching the primary currency.
3. **No Fabricated History**: A single observation is explicitly labeled as a baseline, never as an established historical peak.
