# Requirements: ReviewPulse

**Defined:** 2026-10-21
**Core Value:** Zero-dependency, high-speed review intelligence and product insights without relying on external commercial LLM APIs or brittle web scraping.

## v1 Requirements

Requirements derived from project documentation and specifications.

### Linguistic Analysis Engines

- [x] **REQ-LANG-01**: User can detect the natural language of review text with confidence scoring across 12 languages via `POST /api/v1/analysis/language`.
- [x] **REQ-READ-01**: User can evaluate readability and linguistic complexity (Flesch, FKGL, Fog, Coleman-Liau, Dale-Chall) via `POST /api/v1/analysis/readability`.
- [x] **REQ-SENT-01**: User can compute sentiment polarity, modifier-aware compound scores, and aspect-based sentiment via `POST /api/v1/analysis/sentiment`.
- [x] **REQ-TOPIC-01**: User can extract distinguishing unigrams and bigrams from a multi-document review corpus via `POST /api/v1/analysis/topics`.

### Review Harvester & Catalog Intelligence

- [x] **REQ-HARV-01**: User can trigger collection jobs to import and normalize review CSV datasets idempotently via `POST /api/v1/harvester/jobs`.
- [x] **REQ-CAT-01**: User can query paginated products, product details, and associated reviews via `/api/v1/harvester/products` and `/reviews`.
- [x] **REQ-INSIGHT-01**: User can retrieve aggregated review intelligence (sentiment distribution, top topics, ratings, readability) via `GET /api/v1/harvester/products/{id}/insights`.

### Price Tracking & Monitoring

- [ ] **REQ-PRICE-01**: User can check on-demand product prices and retrieve deduplicated historical price snapshots via `/api/v1/harvester/products/{id}/price-history` and `/check-price`.

## v2 Requirements

Deferred to future releases:
- **AUTH-01**: User registration, login, and JWT/session authentication.
- **WATCH-01**: User product watchlist and price alert notifications.
- **QUEUE-01**: Background task queue integration (ARQ / Redis) for scheduled continuous price monitoring.
- **UI-01**: Next.js frontend application with interactive review intelligence dashboards and price charts.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Live Amazon web scraping | Violates terms of service, brittle against anti-bot challenges |
| External commercial LLM API calls | Core NLP analysis must be deterministic, free, and sub-5ms |
| Heavyweight message broker in default dev setup | Keeps local developer onboarding zero-friction |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| REQ-LANG-01 | Phase 1 | Complete |
| REQ-READ-01 | Phase 1 | Complete |
| REQ-SENT-01 | Phase 1 | Complete |
| REQ-TOPIC-01 | Phase 1 | Complete |
| REQ-HARV-01 | Phase 2 | Complete |
| REQ-CAT-01 | Phase 2 | Complete |
| REQ-INSIGHT-01 | Phase 2 | Complete |
| REQ-PRICE-01 | Phase 3 | Complete |
