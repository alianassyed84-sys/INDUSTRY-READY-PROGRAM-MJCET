# ReviewPulse — API Integration Mapping

**Date:** October 22, 2026  
**Document:** `docs/api-integration-map.md`  
**Purpose:** Verified contract-first mapping between Kulsum's ReviewPulse Frontend pages/components and the FastAPI Backend endpoints.

---

## 1. Verified Endpoint Mapping Table

| Frontend Feature / Page | Actual HTTP Method & Path | Request Schema | Response Schema | Auth / Role Requirement | Integration Status |
|---|---|---|---|---|---|
| **Health Check** (Topbar, State) | `GET /api/v1/health` | None (empty body) | `HealthResponse`: `{ status: str, service: str }` | None (Public) | Verified Ready |
| **Readiness Probe** (Diagnostic) | `GET /api/v1/ready` | None (empty body) | `ReadyResponse`: `{ status: str, service: str, database: str }` | None (Public) | Verified Ready |
| **Product Catalog** (`Dashboard.tsx`, `Reviews.tsx`) | `GET /api/v1/harvester/products` | Query: `limit: int = 20`, `offset: int = 0` | `PaginatedProducts`: `{ items: ProductListItem[], total: int, limit: int, offset: int }` | Bearer JWT (`CurrentUser`) | Contract Defined; Adapt Frontend |
| **Product Detail** (`Dashboard.tsx`, `Analytics.tsx`) | `GET /api/v1/harvester/products/{id}` | Path param: `id: str` | `ProductDetailResponse`: `{ product_id, product_name, category, rating, rating_count, discounted_price, actual_price, discount_percentage, about_product, img_link, product_link, created_at }` | Bearer JWT (`CurrentUser`) | Contract Defined; Adapt Frontend |
| **Product Insights** (`Dashboard.tsx`, `Analytics.tsx`) | `GET /api/v1/harvester/products/{id}/insights` | Path param: `id: str`, Query: `limit: int = 100`, `aspects: str?` | `ProductInsightsResponse`: `{ product_id, total_reviews_in_db, total_reviews_analyzed, ratings_breakdown, sentiment_summary, top_topics, readability, analyzed_at }` | Bearer JWT (`CurrentUser`) | Contract Defined; Adapt Frontend |
| **Price History & Trend** (`Analytics.tsx`, `Dashboard.tsx`) | `GET /api/v1/harvester/products/{id}/price-history` | Path: `id`, Query: `start_date?`, `end_date?`, `limit=50`, `offset=0` | `PriceHistoryResponse`: `{ product_id, observations_count, first_observed_price, latest_observed_price, current_price, highest_observed_price, lowest_observed_price, price_change_amount, price_change_percentage, currency, is_multi_currency, snapshots: PriceSnapshotSchema[] }` | Bearer JWT (`CurrentUser`) | Contract Defined; Adapt Frontend |
| **On-Demand Price Poll** (`Analytics.tsx`, Admin) | `POST /api/v1/harvester/products/{id}/check-price` | Path: `id` | `PriceHistoryResponse` | Bearer JWT (`AdminUser`) | Contract Defined; Admin Guard |
| **Product Reviews List** (`Reviews.tsx`) | `GET /api/v1/harvester/reviews` | Query: `product_id?: str`, `limit: int = 20`, `offset: int = 0` | `PaginatedReviews`: `{ items: ReviewResponse[], total: int, limit: int, offset: int }` | Bearer JWT (`CurrentUser`) | Contract Defined; Adapt Frontend |
| **Amazon URL Analyzer** (`Analysis.tsx`, `Dashboard.tsx`) | `POST /api/v1/harvester/analyze-url` | `AnalyzeUrlRequest`: `{ url: str }` | `ProductUrlAnalysisResponse`: `{ asin, canonical_url, product, price_history, insights, status_note }` | Bearer JWT (`CurrentUser`) | Contract Defined; Adapt Frontend |
| **Language Identification** (`Language.tsx`) | `POST /api/v1/analysis/language` | `LanguageDetectionRequest`: `{ text: str }` (1-50,000 chars) | `LanguageDetectionResponse`: `{ language: str, language_name: str, confidence: float, confidence_level: str, is_reliable: bool, ranked_languages: RankedLanguage[] }` | Bearer JWT (`CurrentUser`) | Contract Defined; Adapt Frontend |
| **Readability Analysis** (`Readability.tsx`) | `POST /api/v1/analysis/readability` | `ReadabilityRequest`: `{ text: str }` (1-100,000 chars) | `ReadabilityResponse`: `{ scores: ReadabilityScores, statistics: TextStatistics, reliability: str, interpretation: str }` | Bearer JWT (`CurrentUser`) | Contract Defined; Adapt Frontend |
| **Sentiment Analysis & ABSA** (`Analysis.tsx`, `Dashboard.tsx`) | `POST /api/v1/analysis/sentiment` | `SentimentRequest`: `{ text: str, aspects?: str[] }` | `SentimentResponse`: `{ compound: float, sentiment_class: str, positive: float, negative: float, neutral: float, aspect_sentiments: AspectSentiment[], highlights: HighlightToken[] }` | Bearer JWT (`CurrentUser`) | Contract Defined; Adapt Frontend |
| **Keyphrase Extraction** (`Topics.tsx`) | `POST /api/v1/analysis/topics` | `TopicsRequest`: `{ documents: str[], focus_index?: int, top_n?: int }` | `TopicsResponse`: `{ keyphrases: DocumentKeyphrases[], corpus_stats: CorpusStats, limitations: str[] }` | Bearer JWT (`CurrentUser`) | Contract Defined; Adapt Frontend |
| **Ingestion Job Start** (`Harvester.tsx`) | `POST /api/v1/harvester/jobs` | `JobStartRequest`: `{ source: str = "csv_amazon" }` (No `csv_path` accepted from client) | `JobStatusResponse`: `{ id: int, source: str, status: str, products_imported: int, reviews_imported: int, error_sample: list, started_at: datetime, completed_at: datetime? }` | Bearer JWT (`AdminUser`) | Contract Defined; Admin Guard |
| **Ingestion Job Status** (`Harvester.tsx`) | `GET /api/v1/harvester/jobs/{id}` | Path param: `id: int` | `JobStatusResponse` | Bearer JWT (`AdminUser`) | Contract Defined; Admin Guard |
| **Personal Watchlist / Tracking** (`Dashboard.tsx`, User) | **None exists in Backend** | N/A | N/A | Requires user ownership DB models & endpoints | **BLOCKED (Backend Capability Missing)** |

---

## 2. Key Data Contract Translations (Frontend Adapter Requirements)

### 2.1 Products Adapter
- **Backend Model (`ProductListItem`)**:
  - `product_id: string` (e.g. `"B084J4MZK6"`)
  - `product_name: string`
  - `category: string | null`
  - `discounted_price: number | null` (from `Decimal`)
  - `actual_price: number | null` (from `Decimal`)
  - `discount_percentage: number | null`
  - `rating: number | null`
  - `rating_count: number | null`
  - `img_link: string | null`
  - `product_link: string | null`
- **Frontend Current Model (`src/lib/types.ts: Product`)**:
  - Expected `id`, `title`, `imageUrl`, `price`, `listPrice`, `rating`, `ratingCount`.
- **Adapter Resolution**:
  - `id`: maps from `product_id`.
  - `title`: maps from `product_name`.
  - `imageUrl`: maps from `img_link`.
  - `price`: maps from `discounted_price`.
  - `listPrice`: maps from `actual_price`.
  - `asin`: maps from `product_id`.
  - Maintain both raw backend keys and convenient UI accessors in a clean adapter layer.

### 2.2 Product Insights Adapter
- **Backend Model (`ProductInsightsResponse`)**:
  - `ratings_breakdown`: `{ average_rating: float, total_ratings_count: int, stars_1: int, stars_2: int, stars_3: int, stars_4: int, stars_5: int }`
  - `sentiment_summary`: `{ positive_count: int, negative_count: int, neutral_count: int, compound_average: float, positive_percentage: float, negative_percentage: float, neutral_percentage: float, aspect_insights: AspectInsight[] }`
  - `top_topics`: list of `{ topic: string, frequency: int, score: float }`
  - `readability`: `{ average_flesch_reading_ease: float, average_grade_level: float, grade_interpretation: string, total_analyzed: int }`
- **Frontend Translation**:
  - Rating breakdown object: `{ '1': stars_1, '2': stars_2, '3': stars_3, '4': stars_4, '5': stars_5 }`.
  - Sentiment mix: `{ positive: positive_count, neutral: neutral_count, negative: negative_count, avgPolarity: compound_average }`.
  - Radar chart: maps `aspect_insights` (`aspect` name, `compound_average` mapped to `score`).
  - Trending complaints: negative aspect insights or negative topics ordered by frequency.

### 2.3 Product Reviews Adapter
- **Backend Model (`PaginatedReviews` -> `ReviewResponse`)**:
  - `id: int`
  - `review_id: string`
  - `product_id: string`
  - `user_id: string | null`
  - `user_name: string | null`
  - `rating: float | null`
  - `review_title: string | null`
  - `review_content: string | null`
  - `created_at: string`
- **Frontend Translation**:
  - `text`: combination of `review_title` and `review_content`.
  - `rating`: direct float/int.
  - `date`: `created_at` formatted with `fmtDate`.

---

## 3. Blocked Feature Specification: Personal Watchlists

- **Requirement**: Users expect a private watchlist where they can bookmark products and monitor price fluctuations.
- **Backend Blocker**: The database does not contain a user watchlist or user-to-product subscription table.
- **Action Taken**:
  - In `Dashboard.tsx` and `Analytics.tsx`, the watchlist/starred actions will display: `"Personal Watchlist (Backend Persistence Pending)"`.
  - The UI will NOT write to `localStorage` and pretend it is synced across user sessions.
  - Real catalog products will be displayed from `GET /api/v1/harvester/products`.
