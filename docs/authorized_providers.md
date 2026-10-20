# Authorized Amazon Data Providers Investigation (Milestone 6C)

## 1. Overview
ReviewPulse requires product metadata and customer reviews for Amazon.in product URLs. This document records the verification of authorized external data providers, eligibility prerequisites, authentication models, cost structures, and data coverage.

## 2. Amazon Creator / Product Advertising API (PA-API 5.0)

### 2.1 Eligibility & Account Requirements
- Requires an active Amazon Associates / Influencer account registered in the **India locale (amazon.in)**.
- **Sales Threshold**: Accounts must achieve at least 3 qualifying sales within the initial 180 days of account creation. Accounts with no recent sales will have their API access throttled or revoked.
- PA-API access keys must be generated inside the Amazon Associates Portal under *Tools > Product Advertising API*.

### 2.2 Authentication & Protocol
- **Endpoint**: `https://webservices.amazon.in/paapi5/getitems`
- **Region**: `eu-west-1`
- **Signing**: AWS Signature Version 4 (HMAC-SHA256)
- **Headers**:
  - `host: webservices.amazon.in`
  - `x-amz-target: com.amazon.paapi5.v1.ProductAdvertisingAPIv1.GetItems`
  - `content-type: application/json; charset=utf-8`
  - `x-amz-date: <ISO-8601-Timestamp>`
  - `Authorization: AWS4-HMAC-SHA256 Credential=...`

### 2.3 Available Fields vs. Critical Review Limitation
- **Available Fields**: Product Title, Primary High-Res Images, Current Selling Offer / Price (INR), List Price / Savings, Item Dimensions, Manufacturer / Brand, Average Customer Star Rating summary.
- **Critical Limitation (Reviews)**: **PA-API 5.0 does NOT provide raw customer review text or reviewer identifiers.** Amazon Operating Agreement Section 4 and PA-API License forbids extracting or caching review prose. The API only supplies a customer reviews iframe URL.
- **Implication for ReviewPulse**:
  - For full review NLP intelligence (sentiment, topic labeling, readability), live API calls to official PA-API provide product metadata and price snapshots, but cannot populate the review corpus on demand without supplementary authorized partner review feeds or pre-ingested review corpora (like `amazon.csv`).

## 3. Authorized Third-Party Aggregators (e.g., Rainforest API)

### 3.1 Capabilities & Pricing
- Provides structured JSON responses for Amazon.in product detail (`type=product`) and customer reviews (`type=reviews`).
- Requires a paid monthly subscription (tier-based request credits, e.g. starting at $49/mo).
- Authentication via query param `api_key`.

### 3.2 Current Project Status & Decision
- No commercial API tokens are provided in the repository's `.env`.
- Live scraping of Amazon.in web pages is strictly forbidden (violates project constraints and terms of service).
- **Decision**: In conformance with Milestone 6C requirements, live network calls remain disabled by default. The pipeline supports `AMAZON_PROVIDER=mock` for verified end-to-end integration tests, and raises explicit `ProviderNotConfiguredError` when live credentials are absent.
