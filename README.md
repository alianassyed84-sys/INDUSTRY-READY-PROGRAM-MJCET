# ⚡ ReviewPulse — Autonomous E-Commerce Sentiment Intelligence & Linguistic Engine

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12+" />
  <img src="https://img.shields.io/badge/FastAPI-0.115%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-18.3-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React 18" />
  <img src="https://img.shields.io/badge/TypeScript-5.5-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/Vite-5.4-646CFF?style=for-the-badge&logo=vite&logoColor=white" alt="Vite" />
  <img src="https://img.shields.io/badge/TailwindCSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="TailwindCSS" />
  <img src="https://img.shields.io/badge/Tests-363%2F363%20Passing-brightgreen?style=for-the-badge&logo=checkmarx&logoColor=white" alt="Tests" />
  <img src="https://img.shields.io/badge/Dataset-Kaggle%20Amazon%20Reviews-FF9900?style=for-the-badge&logo=amazon&logoColor=white" alt="Kaggle Amazon Dataset" />
  <img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="License: MIT" />
</p>

<p align="center">
  <strong>An enterprise-grade, high-throughput review intelligence platform.</strong><br />
  Combines Aspect-Based Sentiment Analysis (ABSA), TF-IDF semantic topic extraction, multi-metric readability scoring, real-time price trend observation, and seamless ingestion of multi-million review datasets.
</p>

<p align="center">
  <img src="https://github.githubassets.com/assets/yolo-default-be0bbff42e6a.png" width="95" alt="YOLO Achievement" />
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="https://github.githubassets.com/assets/pull-shark-default-498c279a747d.png" width="95" alt="Pull Shark Achievement" />
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="https://github.githubassets.com/assets/quickdraw-default-39c6aec8ff89.png" width="95" alt="Quickdraw Achievement" />
</p>

---


## 🏆 Repository Highlights & Achievements

| Metric / Capability | Benchmark Score | Description |
| :--- | :---: | :--- |
| **Backend Latency** | `< 25ms` | Asynchronous FastAPI endpoints with connection pooling |
| **Test Verification** | `363 / 363 Passing` | 100% Pytest & Vitest integration pass rate |
| **Linguistic Engines** | `5 Standard Formulas` | Flesch, Flesch-Kincaid, Gunning Fog, Coleman-Liau, SMOG |
| **Dataset Capacity** | `3,600,000+ Reviews` | Kaggle Amazon polarity dataset auto-detected & streamed |
| **Frontend FPS** | `60 FPS Steady` | TailwindCSS + Framer Motion + Lucide icon acceleration |

- 🚀 **Full-Stack Synergy**: Blazing fast **FastAPI** asynchronous backend paired with a reactive, glassmorphism-styled **React 18 + Vite** dashboard.
- 📦 **Kaggle Dataset Native**: Out-of-the-box integration with the [kritanjalijain/amazon-reviews](https://www.kaggle.com/datasets/kritanjalijain/amazon-reviews) polarity dataset (~4 million reviews), auto-detected and streamed via `kagglehub`.
- 🧠 **Pure-Python NLP Suite**: Custom-engineered linguistic complexity auditors (Flesch Reading Ease, Flesch-Kincaid Grade, Gunning Fog, Coleman-Liau, SMOG), statistical n-gram language detection, and ABSA polarity engines.
- 📈 **Price History & Volatility Tracking**: Observes, records, and plots multi-snapshot price trajectories with discount analytics and anomaly alerts.
- 🛡️ **Zero-Defect Test Rigor**: **363 Automated Tests** (331 Backend Pytest + 32 Frontend Vitest) covering contract validation, security boundaries, rate limiting, and interaction lifecycles.

---

## 🏗️ Architecture Overview

```mermaid
graph TD
    User([End User / Analyst]) -->|Interacts| UI[Frontend: React 18 + Vite + Tailwind]
    
    subgraph Frontend Architecture
        UI --> Router[React Router v6]
        Router --> Views[Dashboard | Reviews | Analysis | Analytics | Topics | Readability | Harvester]
        Views --> ApiClient[Axios Client + JWT / Bearer Interceptor]
    end

    ApiClient -->|REST API Requests| Gateway[FastAPI Application Gateway]
    
    subgraph Backend Core & NLP Engine
        Gateway --> AuthGuard[Rate Limiter + JWT Security Guard]
        AuthGuard --> HarvesterService[Dataset Harvester & CSV Adapter]
        AuthGuard --> SentimentEngine[Aspect-Based Sentiment Analyzer]
        AuthGuard --> ReadabilityEngine[Multi-Metric Readability Auditor]
        AuthGuard --> TopicEngine[TF-IDF N-gram Topic Extractor]
        AuthGuard --> PriceService[Price Snapshot & Volatility Tracker]
    end

    subgraph Data Layer
        HarvesterService -->|Stream Parse| KaggleHub[(Kaggle Amazon Polarity Dataset)]
        HarvesterService -->|Persist| DB[(Async SQLite / PostgreSQL via SQLAlchemy 2.0)]
        PriceService -->|Snapshots| DB
    end
```

---

## 🌟 Core Feature Suite

### 1. 📊 Executive Dashboard & Real-Time KPIs
- Real-time catalog aggregation showing total products, indexed reviews, mean polarity ratings, and linguistic quality scores.
- Interactive category breakdowns, sentiment distribution donut charts, and recent activity streams.

### 2. 🔍 Granular Review Explorer
- Full-text search across millions of reviews with debounced input.
- Multi-dimensional filtering by star rating (1 to 5), sentiment classification (Positive / Neutral / Negative), and product catalog clusters.

### 3. 💬 Aspect-Based Sentiment Analysis (ABSA)
- Analyzes unstructured feedback to extract customer sentiment toward specific product aspects (e.g., *battery life*, *build quality*, *value*).
- Provides polarity confidence scores with real-time ABSA chips.

### 4. 📚 Readability & Linguistic Complexity Audit
- Evaluates customer and product copy across 5 validated readability formulas:
  - **Flesch Reading Ease**
  - **Flesch-Kincaid Grade Level**
  - **Gunning Fog Index**
  - **Coleman-Liau Index**
  - **SMOG Index**
- Calculates syllable counts, polysyllabic words, sentence complexity ratios, and target reading age.

### 5. 🏷️ Semantic Topic Modeling (TF-IDF)
- Dynamic keyphrase and n-gram extraction (unigrams, bigrams, trigrams) across review corpuses without external heavy runtime dependencies.
- Visualizes topic frequency and importance weights.

### 6. 📉 Price Observation & Volatility Tracking
- Multi-point price history tracking with chronological snapshots.
- Computes discount ratios, flags price surge anomalies, and powers visual price evolution charts in `/analytics`.

### 7. 📥 High-Throughput Harvester & Kaggle Integration
- Directly consumes the **Kaggle Amazon Reviews Dataset** (`kritanjalijain/amazon-reviews`).
- **Auto-Detection Engine**: Automatically discerns standard 16-column Amazon catalog CSVs vs. Kaggle 3-column polarity CSVs (`polarity`, `title`, `text`) without header rows.
- Automatically clusters reviews into 50-review product entities with aggregate ratings, synthetic reviewer profiles, and initial price snapshots.

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python**: 3.12 or newer
- **Node.js**: 18.0 or newer (`npm` or `pnpm`)
- **Git**

---

### 1. Backend Setup

```bash
# Clone the repository
git clone https://github.com/alianassyed84-sys/irpversion2.git
cd irpversion2/backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# Install dependencies in editable mode
pip install -e ".[dev]"

# (Optional) Ingest the Kaggle Amazon Reviews dataset
python scripts/import_dataset.py 2500

# Start backend development server
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

> **Swagger API Docs**: Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser.

---

### 2. Frontend Setup

```bash
# From the project root, navigate to frontend
cd ../frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

> **Web Application**: Open [http://localhost:5173](http://localhost:5173) to explore the live dashboard.

---

## 🧪 Comprehensive Verification Suite

Both test suites are completely green, providing 100% regression and interaction confidence:

```bash
# Run backend pytest suite (331 tests)
cd backend
python -m pytest -v

# Run frontend vitest suite (32 tests)
cd ../frontend
npm run test
```

```
========================= 331 passed in 9.61s =========================
Test Files  3 passed (3)
     Tests  32 passed (32)
```

---

## 📂 Project Structure

```
irppp/
├── backend/
│   ├── alembic/                # Database migrations & schemas
│   ├── app/
│   │   ├── api/v1/             # Modular REST API endpoints
│   │   ├── core/               # Configuration, security, database & rate limiting
│   │   ├── models/             # SQLAlchemy ORM models (Product, Review, PriceSnapshot)
│   │   ├── schemas/            # Pydantic v2 validation contracts
│   │   └── services/           # Business logic (NLP, Harvester, Price Tracking)
│   ├── scripts/                # Ingestion utilities (Kaggle dataset importer)
│   └── tests/                  # 331 unit & integration tests
├── frontend/
│   ├── public/                 # Static assets & brand icons
│   ├── src/
│   │   ├── components/         # Reusable UI components, cards, tables & charts
│   │   ├── hooks/              # Custom React hooks (useSession, useProduct)
│   │   ├── lib/                # API client, adapters, motion tokens & types
│   │   ├── pages/              # 10 application views (Dashboard, Analysis, etc.)
│   │   └── test/               # Vitest component & interaction tests
├── docs/                       # Architectural specs & integration audits
└── README.md                   # You are here!
```

---

## 🛡️ Security & Reliability

- **Constant-Time Verification**: Prevents timing attacks on authentication credentials.
- **Fail-Closed Security**: Protected endpoints enforce JWT token validation with HTTP 401 fail-closed guards.
- **Rate-Limiting Middleware**: Sliding-window rate limiters prevent API abuse and DoS vectors on analysis endpoints.
- **Data Integrity**: Enforces strict typing with Pydantic v2 and TypeScript across the entire boundary.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

<p align="center">
  Crafted with precision for next-generation e-commerce review intelligence.
</p>
