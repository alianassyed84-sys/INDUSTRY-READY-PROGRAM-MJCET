# Synthesized Requirements

## REQ-HARV-01: CSV Dataset Review Harvester
- **Source**: `docs/harvester.md`
- **Scope**: `harvester`
- **Description**: Import and normalize Amazon product review CSV datasets into the relational database.
- **Acceptance Criteria**:
  - `POST /api/v1/harvester/jobs` starts collection job (HTTP 202) supporting `csv_amazon` source and optional path override.
  - Idempotently upserts `Product`, `User`, and `Review` records.
  - Updates job status to `done` or `failed` with items seen and inserted counts.
  - `GET /api/v1/harvester/jobs/{job_id}` returns job status and progress metrics.

## REQ-CAT-01: Product Catalog & Review Query API
- **Source**: `docs/harvester.md`
- **Scope**: `product-catalog`
- **Description**: Expose paginated endpoints for products and associated reviews.
- **Acceptance Criteria**:
  - `GET /api/v1/harvester/products` supports `limit` (1-100) and `offset` pagination.
  - `GET /api/v1/harvester/products/{id}` returns detailed product fields and aggregate review counts.
  - `GET /api/v1/harvester/reviews` supports filtering by `product_id` with limit/offset pagination.

## REQ-INSIGHT-01: Product Intelligence & Aggregated Insights
- **Source**: `docs/harvester.md`
- **Scope**: `insights-api`
- **Description**: Provide composite intelligence endpoint summarizing product review sentiment, topics, ratings, and readability.
- **Acceptance Criteria**:
  - `GET /api/v1/harvester/products/{product_id}/insights` aggregates review sentiment distribution, top TF-IDF topics, star ratings distribution, and readability metrics.
  - Supports query parameter `limit` (1-500) and optional comma-separated `aspects` for aspect-based polarity.

## REQ-LANG-01: Zero-Dependency Language Identifier
- **Source**: `docs/language_detector.md`
- **Scope**: `language-detection`
- **Description**: Detect natural language of text without third-party external services.
- **Acceptance Criteria**:
  - `POST /api/v1/analysis/language` identifies natural language for 12 ISO 639-1 languages.
  - Script fast-path detects non-Latin scripts (Arabic, Russian, Chinese, Japanese) with O(1) checks.
  - Cavnar & Trenkle character n-gram rank-order profiling accurately classifies Latin-script languages.
  - Returns detected language, confidence score, script classification, and top-3 candidates.

## REQ-READ-01: Zero-Dependency Readability Auditor
- **Source**: `docs/readability_auditor.md`
- **Scope**: `readability`
- **Description**: Evaluate linguistic complexity and reading difficulty using classic readability formulas.
- **Acceptance Criteria**:
  - `POST /api/v1/analysis/readability` computes Flesch Reading Ease, Flesch-Kincaid Grade Level, Gunning Fog, Coleman-Liau, and Dale-Chall.
  - Returns structural statistics: word count, sentence count, syllable count, complex word count, difficult word count.
  - Returns consensus reading difficulty band and execution latency (<5 ms).

## REQ-SENT-01: Review Sentiment & Aspect-Based Polarity
- **Source**: `docs/sentiment_analyzer.md`
- **Scope**: `sentiment-analysis`
- **Description**: Score review sentiment polarity and evaluate targeted product aspects.
- **Acceptance Criteria**:
  - `POST /api/v1/analysis/sentiment` evaluates text using a calibrated product-review lexicon.
  - Applies modifier rules: negation flipping, booster scaling, ALL-CAPS emphasis, exclamation amplification, and contrastive conjunction pivots (`but`, `however`).
  - Returns compound score in `[-1.0, 1.0]` and positive/negative/neutral proportions.
  - Aspect-based sentiment analysis (ABSA) returns polarity scores and matched snippets for requested aspect attributes.

## REQ-TOPIC-01: TF-IDF Keyphrase Extraction
- **Source**: `docs/topic_labeler.md`
- **Scope**: `topic-labeling`
- **Description**: Extract distinguishing unigram and bigram keyphrases from a review corpus.
- **Acceptance Criteria**:
  - `POST /api/v1/analysis/topics` computes TF-IDF weights over a multi-document corpus.
  - Cleans input with Unicode normalization, HTML/URL stripping, tokenization, and stop-word filtering.
  - Returns top ranked terms per document and corpus-level frequency statistics.

## REQ-PRICE-01: Price Tracking & Observation History
- **Source**: `docs/price_monitoring.md`
- **Scope**: `price-monitoring`
- **Description**: Record price observation snapshots and expose price tracking endpoints.
- **Acceptance Criteria**:
  - `GET /api/v1/harvester/products/{product_id}/price-history` returns historical price snapshots, min/max, and price change metrics.
  - `POST /api/v1/harvester/products/{product_id}/check-price` triggers an on-demand observation poll and records new price snapshot if changed.
  - Deduplicates consecutive identical observations and safeguards multi-currency calculations.
