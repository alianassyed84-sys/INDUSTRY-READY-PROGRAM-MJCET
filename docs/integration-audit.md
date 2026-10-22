# ReviewPulse — Frontend-Backend Integration Audit

**Date:** October 22, 2026  
**Auditor:** Senior Full-Stack & Integration Architect (Antigravity Agent)  
**Target:** Integration of Kulsum's ReviewPulse Frontend (`ReviewPulse/`) with the ReviewPulse FastAPI Backend (`backend/`)  
**Status:** Audit & Reconnaissance Complete — Verified against live code and schemas.

---

## 1. Executive Summary

ReviewPulse consists of two distinct subsystems:
1. **Frontend (`INDUSTRY-READY-PROGRAM-MJCET/ReviewPulse`)**: A React 18, Vite 5, TypeScript single-page application styled with Tailwind CSS, utilizing React Router DOM v6, TanStack Query v5, Recharts, GSAP, and Lucide icons. Currently, it operates with mock demo fixtures (`src/data/demo.ts`) and a prototype device-only session hook (`src/hooks/useSession.tsx`).
2. **Backend (`irppp/backend`)**: A hardened Python 3.12 FastAPI service with 329 passing unit and regression tests, zero lint warnings, structured request correlation tracing (`X-Request-ID`), JWT Bearer verification (Clerk compatible), in-memory sliding window rate-limiting, and pure standard-library NLP engines.

This document establishes the verified truth of both codebases and defines the exact path to integrate them without fabricating endpoints, faking persistence, or breaking existing visual designs.

---

## 2. Frontend Architecture & Inventory

### 2.1 Technology Stack
- **Framework**: React 18.3.1 with Vite 5.4.21 (`@vitejs/plugin-react`).
- **Language**: TypeScript 5.9.3 (`tsconfig.json` target ES2020).
- **Styling**: Tailwind CSS 3.4.19 with custom design tokens in `tailwind.config.js` (`rp-primary`, `rp-navy`, `rp-coral`, `rp-surface`, etc.), PostCSS, and `@fontsource-variable/inter` / `manrope`.
- **Routing**: `react-router-dom` 6.30.6 with centralized route definitions in `src/lib/routes.ts`.
- **State & Data Fetching**: `@tanstack/react-query` 5.104.5.
- **Charts & 3D**: `recharts` 3.10.1 and `three` 0.186.1 / `gsap` 3.12.
- **Form Handling**: `react-hook-form` 7.90.0 with `zod` 4.6.7 and `@hookform/resolvers`.
- **Testing**: Vitest 2.1.9 with `@testing-library/react` and `jsdom`.

### 2.2 Existing Pages & Routes
| Route | Page Component | Current Data Source | Planned Real Backend Mapping |
|---|---|---|---|
| `/` | `Landing.tsx` | Static / ThreeHero | Public marketing landing page; links to `/login`, `/register`, `/dashboard`. |
| `/dashboard` | `Dashboard.tsx` | Demo fixtures (`useInsights`, `useProductContext`) | `GET /api/v1/harvester/products`, `GET /api/v1/harvester/products/{id}/insights`. |
| `/analysis` | `Analysis.tsx` | Mock analyzer | `POST /api/v1/harvester/analyze-url` (Amazon URL analysis). |
| `/analytics` | `Analytics.tsx` | Demo price/rating fixtures | `GET /api/v1/harvester/products/{id}/price-history`, `GET /api/v1/harvester/products/{id}/insights`. |
| `/reviews` | `Reviews.tsx` | Demo review fixtures | `GET /api/v1/harvester/reviews?product_id={id}`. |
| `/harvester` | `Harvester.tsx` | Static placeholder form | `POST /api/v1/harvester/jobs`, `GET /api/v1/harvester/jobs/{id}` (Admin only). |
| `/language` | `Language.tsx` | Local mock | `POST /api/v1/analysis/language`. |
| `/readability` | `Readability.tsx` | Local mock | `POST /api/v1/analysis/readability`. |
| `/topics` | `Topics.tsx` | Local mock | `POST /api/v1/analysis/topics`. |
| `/about` | `About.tsx` | Static content | Static informational page. |
| `/settings` | `Settings.tsx` | `sessionStorage` | Configuration and user session details. |
| `/login` | `Auth.tsx` | Prototype `sessionStorage` | Clerk Auth / Session login integration. |
| `/register` | `Auth.tsx` | Prototype `sessionStorage` | Clerk Auth / Registration flow. |
| `/recover` | `Auth.tsx` | Prototype stub | Password recovery via Clerk. |

---

## 3. Backend Architecture & API Surface

### 3.1 Technology Stack
- **Framework**: FastAPI 0.143.3 on Uvicorn with Starlette.
- **Database ORM**: SQLAlchemy 2.1.5 (asyncpg for PostgreSQL, aiosqlite for tests).
- **Migrations**: Alembic 1.20.0 (Revisions: `0001_add_core_entities`, `0002_add_price_snapshots`, `0003_harden_database_and_monetary_types`).
- **Security & Tracing**: Clerk-compatible JWT Bearer authentication, RBAC admin guards, Sliding-window rate limiter, and `RequestIdMiddleware` (`X-Request-ID`).
- **NLP Engines**: Zero-dependency rule-based sentiment with ABSA, n-gram language detection (12 languages), Flesch/ARI readability metrics, and TF-IDF keyphrase extraction.

### 3.2 Global API Prefix
All application API routes are mounted under:
`api_v1_prefix: str = "/api/v1"`

### 3.3 Complete Verified Backend Route Inventory
| Method | Path | Auth / Role Required | Rate Limit | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/health` | None (Public) | Exempt | Service liveness probe. |
| `GET` | `/api/v1/ready` | None (Public) | Exempt | Dependency & database readiness check. |
| `POST` | `/api/v1/analysis/readability` | Bearer JWT (`CurrentUser`) | 60/min | Linguistic complexity & readability scoring. |
| `POST` | `/api/v1/analysis/language` | Bearer JWT (`CurrentUser`) | 60/min | Cavnar & Trenkle n-gram language identification. |
| `POST` | `/api/v1/analysis/sentiment` | Bearer JWT (`CurrentUser`) | 60/min | Polarity & aspect-based sentiment analysis. |
| `POST` | `/api/v1/analysis/topics` | Bearer JWT (`CurrentUser`) | 60/min | TF-IDF keyphrase and topic extraction. |
| `GET` | `/api/v1/harvester/products` | Bearer JWT (`CurrentUser`) | 120/min | Paginated product catalog (`?limit=20&offset=0`). |
| `GET` | `/api/v1/harvester/products/{id}` | Bearer JWT (`CurrentUser`) | 120/min | Full product details. |
| `GET` | `/api/v1/harvester/products/{id}/insights` | Bearer JWT (`CurrentUser`) | 120/min | Aggregated sentiment, topics, ratings, readability. |
| `GET` | `/api/v1/harvester/products/{id}/price-history` | Bearer JWT (`CurrentUser`) | 120/min | Historical price snapshots & trend metrics. |
| `POST` | `/api/v1/harvester/products/{id}/check-price` | Bearer JWT (`AdminUser`) | 20/min | Trigger on-demand provider price observation. |
| `GET` | `/api/v1/harvester/reviews` | Bearer JWT (`CurrentUser`) | 120/min | Paginated reviews (`?product_id=&limit=20&offset=0`). |
| `POST` | `/api/v1/harvester/analyze-url` | Bearer JWT (`CurrentUser`) | 10/min | Validate Amazon India URL, fetch or ingest, compute insights. |
| `POST` | `/api/v1/harvester/jobs` | Bearer JWT (`AdminUser`) | 10/min | Start batch review CSV ingestion (synchronous). |
| `GET` | `/api/v1/harvester/jobs/{id}` | Bearer JWT (`AdminUser`) | 10/min | Query status of an ingestion job. |

---

## 4. Authentication Architecture & Clerk Verification Contract

### 4.1 Verification Logic (`backend/app/core/auth.py`)
- **Transport**: `Authorization: Bearer <JWT>` header on all protected requests.
- **Signature Algorithms**: `RS256` (via Clerk JWKS URL or configured PEM public key), fallback to `HS256` (via secret key).
- **Issuer Validation**: If `CLERK_ISSUER` is configured, `iss` claim must match exactly.
- **Audience Validation**: If `CLERK_AUDIENCE` is configured, `aud` claim must match. Otherwise, audience verification is disabled (`verify_aud=False`).
- **Subject Extraction**: `sub` claim is extracted as the immutable `user_id`.
- **Role & Privilege Resolution**:
  - `admin` role is granted if `"admin"` is present in `claims["roles"]`, `claims["role"]`, `claims["org_role"]`, or `public_metadata["role"]`.
  - Non-admin authenticated tokens have standard user access.
- **Local Dev / Test Bypass**:
  - When `AUTH_ENABLED=False` in backend `.env`, `get_current_user` and `require_admin` bypass verification and return an anonymous admin user (`test_user_anonymous`).

---

## 5. Architectural Blockers & Unsupported Capabilities

### 5.1 Personal Watchlists & User-Owned Tracking (CRITICAL BLOCKER)
- **Status**: **NOT SUPPORTED BY BACKEND DATABASE OR API**.
- **Evidence**:
  - `backend/app/models/` contains `User` (which represents review authors extracted from Amazon CSV datasets, not authenticated SaaS users).
  - There is no `watchlist`, `user_watchlist`, `user_products`, or `tracked_items` table or migration in Alembic.
  - There are no endpoints for `/users/me/watchlist`, `/users/me/tracked-products`, or user alert preferences.
- **Integration Action**:
  - **Do NOT simulate persistence in `localStorage` and label it an account-level watchlist.**
  - Clearly label the feature as "Personal Watchlist (Backend Persistence Pending)" in the UI or disable the watchlist mutation controls while allowing global catalog exploration.
  - Document the required minimal backend migration for a future milestone.

### 5.2 Asynchronous Background Queue for CSV Ingestion
- **Status**: **ARCHITECTURAL CEILING (Documented)**.
- **Evidence**:
  - `backend/app/api/v1/harvester.py:116-149`: `start_job` runs synchronously within the HTTP request cycle (`await run_csv_import(...)`) taking 1–3 seconds for 1,465 rows before responding.
- **Integration Action**:
  - The UI must treat `POST /api/v1/harvester/jobs` as a synchronous execution rather than establishing an infinite polling loop for a pending job.

---

## 6. Environment & CORS Configuration

### 6.1 Frontend Origin
The Vite development server runs at:
`http://localhost:5173` (or `http://127.0.0.1:5173`).

### 6.2 Backend CORS Settings
`backend/app/core/config.py` and `backend/app/main.py`:
- `CORS_ORIGINS` must include `http://localhost:5173` and `http://127.0.0.1:5173`.
- `allow_headers`: `["Authorization", "Content-Type", "Accept", "X-Request-ID"]`.
- `expose_headers`: `["X-Request-ID"]`.

---

## 7. Migration & Regression Safety

1. **Alembic Status**: Head is `0003` (`0003_harden_database_and_monetary_types.py`). Database models and migrations are synchronized.
2. **Backend Regression Status**: 329 passing tests, 0 warnings with `-W error`.
3. **Preservation**: No backend refactoring or schema tampering will be performed during frontend integration.
