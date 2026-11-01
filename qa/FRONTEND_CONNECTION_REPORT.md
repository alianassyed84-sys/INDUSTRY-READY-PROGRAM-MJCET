# ReviewPulse Frontend Connection & Alignment Report

> **Status:** 100% connected (All 16 frontend API calls MATCH backend endpoints; zero unverified or missing backend routes; all field deviations resolved or explicitly justified).
> **Date:** 2026-11-01
> **Adopted Frontend Commit:** `893520ac71491a1e0563512655ebcdba1671d31b` (Repo B)
> **Active Branch:** `adopt-frontend-v2`
> **Backend Codebase:** Repo A (`http://127.0.0.1:8000`) — 100% untouched.

---

## Executive Summary

- **Frontend Adoption:** The `frontend/` directory was 100% replaced from `abida/main` (commit `893520a`) and verified byte-for-byte via SHA-256 (85 files matched).
- **Backend Frozen:** Zero changes made to `backend/` during this integration task.
- **API Calls Matched:** **16 of 16** (100% MATCH).
- **Displayed Fields Traced to Backend:** **100%** traced and aligned.
- **Hardcoded Values Remaining:** **3** (All justified: offline demo fixtures guarded by `VITE_ENABLE_DEMO=true`, explicit "Example" preview badge on Landing, and decorative SVG hero animations).
- **Automated Contract Tests:** Automated OpenAPI contract suite (`src/test/contract.test.ts`) integrated into test suite.
- **Test Suite Results:** **66 of 66 passing** across 9 test files.
- **Production Build:** `tsc --noEmit && vite build` clean, 0 errors.

---

## Table 1: Frontend API Calls vs Backend OpenAPI Routes

| # | Frontend Call (`src/lib/api.ts`) | Method | Request Path | Backend OpenAPI Route | Status | Expected Response Type | Consuming Pages / Modules |
|---|---|---|---|---|---|---|---|
| 1 | `api.health(signal)` | `GET` | `/api/v1/health` | `/api/v1/health` | **MATCH** | `BackendHealthResponse` | `Harvester.tsx`, `Settings.tsx` |
| 2 | `api.ready(signal)` | `GET` | `/api/v1/ready` | `/api/v1/ready` | **MATCH** | `BackendReadyResponse` | `Settings.tsx` |
| 3 | `api.products(signal)` | `GET` | `/api/v1/harvester/products?limit=100` | `/api/v1/harvester/products` | **MATCH** | `BackendPaginatedProducts` | `useProduct.tsx`, `AppShell.tsx`, `Dashboard.tsx` |
| 4 | `api.product(id, signal)` | `GET` | `/api/v1/harvester/products/{id}` | `/api/v1/harvester/products/{product_id}` | **MATCH** | `BackendProductDetail` | `api.ts` (called in `api.insights`) |
| 5 | `api.insights(id, signal)` | `GET` | `/api/v1/harvester/products/{id}/insights?limit=100` | `/api/v1/harvester/products/{product_id}/insights` | **MATCH** | `BackendProductInsightsResponse` | `useProduct.tsx`, `Dashboard.tsx`, `Analysis.tsx`, `Analytics.tsx` |
| 6 | `api.reviews(id, signal)` | `GET` | `/api/v1/harvester/reviews?product_id={id}&limit=100` | `/api/v1/harvester/reviews` | **MATCH** | `BackendPaginatedReviews` | `useProduct.tsx`, `Reviews.tsx`, `Dashboard.tsx` |
| 7 | `api.priceHistory(id, signal)` | `GET` | `/api/v1/harvester/products/{id}/price-history` | `/api/v1/harvester/products/{product_id}/price-history` | **MATCH** | `BackendPriceHistoryResponse` | `api.ts` (called in `api.insights`) |
| 8 | `api.checkPrice(id, signal)` | `POST` | `/api/v1/harvester/products/{id}/check-price` | `/api/v1/harvester/products/{product_id}/check-price` | **MATCH** | `BackendPriceHistoryResponse` | `Analytics.tsx` |
| 9 | `api.analyzeUrl(url, signal)` | `POST` | `/api/v1/harvester/analyze-url` | `/api/v1/harvester/analyze-url` | **MATCH** | `BackendProductUrlAnalysisResponse` | `Harvester.tsx`, `UrlAnalyzer.tsx` |
| 10 | `api.scrapeFlipkart(params, signal)` | `POST` | `/api/v1/harvester/flipkart/scrape` | `/api/v1/harvester/flipkart/scrape` | **MATCH** | `BackendFlipkartScrapeResponse` | `Harvester.tsx` |
| 11 | `api.startJob(source, signal)` | `POST` | `/api/v1/harvester/jobs` | `/api/v1/harvester/jobs` | **MATCH** | `BackendJobStatusResponse` | `Harvester.tsx` |
| 12 | `api.getJob(jobId, signal)` | `GET` | `/api/v1/harvester/jobs/{job_id}` | `/api/v1/harvester/jobs/{job_id}` | **MATCH** | `BackendJobStatusResponse` | `api.ts` |
| 13 | `api.readability(text, signal)` | `POST` | `/api/v1/analysis/readability` | `/api/v1/analysis/readability` | **MATCH** | `BackendReadabilityResponse` | `Readability.tsx` |
| 14 | `api.detectLanguage(text, signal)` | `POST` | `/api/v1/analysis/language` | `/api/v1/analysis/language` | **MATCH** | `BackendLanguageDetectionResponse` | `Language.tsx` |
| 15 | `api.analyzeSentiment(text, aspects, signal)` | `POST` | `/api/v1/analysis/sentiment` | `/api/v1/analysis/sentiment` | **MATCH** | `BackendSentimentResponse` | `Analysis.tsx` |
| 16 | `api.extractTopics(docs, topN, focus, signal)` | `POST` | `/api/v1/analysis/topics` | `/api/v1/analysis/topics` | **MATCH** | `BackendTopicsResponse` | `Topics.tsx` |

**Count:** API calls matched: **16 of 16 (100%)**.

---

## Table 2: Backend Routes Not Called by Frontend

| # | Backend Route | Method | Purpose in OpenAPI Schema | Frontend Status & Justification |
|---|---|---|---|---|
| 1 | `/api/v1/harvester/products/{product_id}/compare` | `GET` | Dual-platform price and ABSA comparison | **Approved omission**. Per `qa/FRONTEND_SPEC.md` v4: `/compare` is designated as *"LATER, only when their backend exists: /reports, Processing Center, Buyer/Seller mode, /compare."* |
| 2 | `/api/v1/harvester/seed` | `POST` | Database fixture and mock review seeder | **Approved omission**. Administrative server maintenance endpoint, not intended for user UI navigation. |

---

## Table 3: Field-Level Audit & Data Honesty Fixes

| Field / Component | Raw Backend Value | Previous Adapter Behavior | Fixed Behavior in Phase 3 | Status |
|---|---|---|---|---|
| `Product.brand` | `category: string \| null` | Set `brand = item.category ?? undefined` | `brand` is set to `undefined`; `category` is preserved separately. Never confuses brand with category. | **RESOLVED** |
| `Product.marketplace` | Inferred from URL domain | Hardcoded `'Amazon.in'` | Derived dynamically from `product_link` URL: `'Amazon.in'` for Amazon URLs, `'Flipkart'` for Flipkart URLs, `undefined` if unrecognized. | **RESOLVED** |
| `Review.date` | `created_at: string \| null` | Displayed DB insertion time as review date | `date` is set to `undefined`. ReviewCard hides date time tag rather than presenting DB ingestion time as review date. | **RESOLVED** |
| `Review.source` | Not in `ReviewListItem` | Hardcoded `'Amazon.in'` | Set to `undefined`. ReviewCard hides source badge rather than attributing non-Amazon reviews to Amazon. | **RESOLVED** |
| `readability.fleschReadingEase` | `average_reading_ease: number \| null` | `backend.readability.average_reading_ease ?? 0` | Preserves `null`. UI displays `"Not available"` instead of misleading 0.0. | **RESOLVED** |
| `readability.gradeLevel` | `consensus_grade_level: number \| null` | `backend.readability.consensus_grade_level ?? 0` | Preserves `null`. UI displays `"Not available"` instead of misleading Grade 0.0. | **RESOLVED** |
| `readability.distribution` | Not in `ProductInsightsResponse` | Passed empty array `[]` into chart | Empty distribution is explicitly checked; renders plain-text notice instead of broken empty chart. | **RESOLVED** |
| Error detail (4xx/5xx) | `detail: string \| list` | Rendered raw JSON or generic HTTP string | Formatted into readable plain words; FastAPI 422 arrays flattened into plain sentences. | **RESOLVED** |

**Count:** Displayed fields traced to a backend field: **100%**.

---

## Table 4: Hardcoded Values & Justifications

| # | Element / Screen | Hardcoded Item | Origin | Justification |
|---|---|---|---|---|
| 1 | `src/data/demo.ts` | Demo fixtures (`demoProducts`, `demoReviews`, `demoInsights`) | Fictional fallback data | **Justified**. Default is OFF in runtime. Only active when `VITE_ENABLE_DEMO=true` or in offline unit testing. When backend is down, UI surfaces plain "Try again" error. |
| 2 | `Landing.tsx` & `SignalJourney.tsx` | `68.0% positive` and `5 themes found` | Computed sample metrics | **Justified**. Computed directly from the sample fixture and explicitly labelled with the `"Example"` and `"Example preview"` badge. |
| 3 | `PulseHero.tsx` | SVG animated heartbeat and path coordinates | Decorative SVG artwork | **Justified**. Purely illustrative visual presentation with reduced-motion toggle support. |

**Count:** Hardcoded values remaining: **3 (each justified)**.

---

## Verification Evidence & Test Execution

### 1. Test Suite Results (66 / 66 Passing)
```text
Test Files  9 passed (9)
     Tests  66 passed (66)
  Duration  40.68s

✓ src/test/contract.test.ts (17 tests)
✓ src/test/alignment_3a.test.ts (3 tests)
✓ src/test/alignment_3b.test.ts (2 tests)
✓ src/test/alignment_3e.test.ts (2 tests)
✓ src/test/app.test.tsx (21 tests)
✓ src/test/interactions.test.tsx (7 tests)
✓ src/test/flipkart.test.ts (6 tests)
✓ src/test/landing_phase4.test.tsx (4 tests)
✓ src/test/amazon.test.ts (4 tests)
```

### 2. TypeScript & Build Verification
```text
> reviewpulse-frontend@0.1.0 build
> tsc --noEmit && vite build

✓ 2745 modules transformed.
dist/index.html                   0.98 kB │ gzip:   0.46 kB
dist/assets/index-BzVSnVH1.css    83.79 kB │ gzip:  19.76 kB
dist/assets/vendor-DJkb65Nt.js   276.64 kB │ gzip:  93.21 kB
dist/assets/index-C-Ey2XV5.js    384.46 kB │ gzip: 116.17 kB
dist/assets/charts-wGRK0z1K.js   430.11 kB │ gzip: 122.39 kB
✓ built in 18.97s
```

### 3. Responsive Landing Screenshots
- **Mobile (375x812):** `qa/screenshots/landing-375.png` (149,474 bytes)
- **Tablet (768x1024):** `qa/screenshots/landing-768.png` (311,048 bytes)
- **Desktop (1440x900):** `qa/screenshots/landing-1440.png` (541,652 bytes)

---

## Conclusion

The new frontend adopted from commit `893520a` is **100% connected** to Repo A's backend. All forbidden jargon has been purged, data honesty rules are enforced, both landing entry points are operational, and the automated contract check guarantees ongoing alignment.
