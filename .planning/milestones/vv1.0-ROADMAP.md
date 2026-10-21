# Roadmap: ReviewPulse

## Overview

ReviewPulse is built systematically starting from high-speed, zero-dependency linguistic analysis engines, advancing through catalog data harvesting and multi-dimensional review insights, to historical price monitoring and upcoming user dashboards.

## Phases

- [x] **Phase 1: Core Linguistic Analysis Engines** - Pure Python zero-dependency language identification, readability scoring, aspect-based sentiment, and TF-IDF topic labeling.
- [x] **Phase 2: Review Harvester & Catalog Intelligence** - Idempotent CSV review collection jobs, product catalog APIs, and aggregated product intelligence.
- [x] **Phase 3: Price Tracking & Observation History** - Historical price snapshots, observation deduplication, currency safety, and on-demand price checking.

## Phase Details

### Phase 1: Core Linguistic Analysis Engines
**Goal**: Deliver local, deterministic, and sub-5ms linguistic analysis endpoints for consumer review text.
**Depends on**: Nothing (foundation)
**Requirements**: REQ-LANG-01, REQ-READ-01, REQ-SENT-01, REQ-TOPIC-01
**Success Criteria** (what must be TRUE):
  1. User can identify natural language across 12 languages with confidence and script metadata via `POST /api/v1/analysis/language`.
  2. User can score reading difficulty across 5 classic formulas (Flesch, FKGL, Fog, Coleman-Liau, Dale-Chall) via `POST /api/v1/analysis/readability`.
  3. User can compute review sentiment polarity and target aspect breakdowns via `POST /api/v1/analysis/sentiment`.
  4. User can extract keyphrase unigrams and bigrams from a multi-review corpus via `POST /api/v1/analysis/topics`.
**Plans**: Complete (190 unit/service tests passing)

### Phase 2: Review Harvester & Catalog Intelligence
**Goal**: Import review datasets into PostgreSQL/SQLite and expose product catalog intelligence.
**Depends on**: Phase 1
**Requirements**: REQ-HARV-01, REQ-CAT-01, REQ-INSIGHT-01
**Success Criteria** (what must be TRUE):
  1. User can trigger idempotent CSV import jobs via `POST /api/v1/harvester/jobs` and query progress via `GET /api/v1/harvester/jobs/{id}`.
  2. User can search and view paginated products and reviews via `/api/v1/harvester/products` and `/reviews`.
  3. User can fetch composite review intelligence (sentiment, topics, ratings, readability) for any product via `GET /api/v1/harvester/products/{id}/insights`.
**Plans**: Complete (Harvester APIs and CSV adapter verified)

### Phase 3: Price Tracking & Observation History
**Goal**: Record price observations over time and provide price movement metrics for catalog products.
**Depends on**: Phase 2
**Requirements**: REQ-PRICE-01
**Success Criteria** (what must be TRUE):
  1. User can query historical price snapshots and computed deltas via `GET /api/v1/harvester/products/{id}/price-history`.
  2. User can trigger an on-demand price check via `POST /api/v1/harvester/products/{id}/check-price`.
  3. Identical consecutive observations are deduplicated to prevent redundant storage.
  4. Multi-currency price deltas are strictly calculated against matching currency baselines.
**Plans**: 1 plan (Complete)

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Core Linguistic Analysis Engines | 1/1 | Complete | 2026-10-19 |
| 2. Review Harvester & Catalog Intelligence | 1/1 | Complete | 2026-10-19 |
| 3. Price Tracking & Observation History | 1/1 | Complete | 2026-10-21 |
