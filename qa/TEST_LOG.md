| ID | Node | Item | Status | Evidence |
|----|------|------|--------|----------|
| T-101 | N14 | Unicode-block script detection (Devanagari->hi, Telugu->te, Tamil->ta, Bengali->bn, Gujarati->gu, Kannada->kn, Malayalam->ml, Gurmukhi->pa, Arabic->ar) | PASS | `backend/tests/test_language_and_sentiment_fixes.py::TestLanguageDetectionCoverage` passed (3 samples each) |
| T-102 | N14 | Hinglish detection via Latin-script vocabulary (`hi-Latn`) | PASS | `backend/tests/test_language_and_sentiment_fixes.py::test_hinglish` passed (3 samples) |
| T-103 | N14 | Calibrated confidence (guesses never 1.0; unreliable outputs 'unknown') | PASS | `backend/tests/test_language_and_sentiment_fixes.py::TestConfidenceCalibration` passed |
| T-104 | N15 | Sentiment language gating (non-English returns `status="unsupported_language"`, does not silently return neutral 0.0) | PASS | `backend/tests/test_language_and_sentiment_fixes.py::TestSentimentLanguageGating` passed |
| T-105 | N19 | Insights aggregation excludes unsupported language reviews and reports `excluded_unsupported_language_count` | PASS | `backend/tests/test_language_and_sentiment_fixes.py::TestProductInsightsUnsupportedLanguageExclusion` passed |
| T-106 | ALL | Full backend regression test suite execution | PASS | `pytest backend/tests` - 399 passed in 42.29s |
| T-107 | FRONTEND | FRONTEND_SPEC v4 route integration & shell rendering | PASS | `frontend/src/test/app.test.tsx` passed, all 7 core routes mount cleanly |
| T-108 | FRONTEND | Dual landing entry points: URL link analyzer & dataset file upload | PASS | `frontend/src/test/app.test.tsx` asserts URL analyzer & upload dataset buttons |
| T-109 | FRONTEND | Deep-linkable product workspace (`/product/:id/:tab`) with 7 tabs | PASS | Workspace renders sticky header, category path, rating, and tab navigation |
| T-110 | FRONTEND | Forbidden terminology purge (backend, API, database, polarity, ASIN) | PASS | Text inspected across components; plain-language replacements applied |
| T-111 | FRONTEND | Full frontend build and test verification | PASS | `tsc --noEmit && vite build` built cleanly; `vitest run` 45/45 passed |
| T-112 | IMAGES | Authentic AI product photos pipeline & uniqueness | PASS | `backend/tests/test_product_images.py` 9/9 passed; zero duplicate links across catalog |
| T-113 | IMAGES | Sibling brand variant distinction (iPhone 15 Black vs iPhone 15 Pro Natural Titanium) | PASS | Separate photos generated for each model with distinct features; verified by `test_same_brand_phones_have_distinct_images` |
| T-114 | FRONTEND | Product photo thumbnail in workspace header and "Reviews with images" section | PASS | `frontend/src/test/overview.test.tsx` 4/4 passed; `vite build` 0 errors |
| T-115 | IMAGES | Zero-placeholder catalog coverage: all 67 products have 1-to-1 unique authentic photos | PASS | `backend/tests/test_product_images.py::test_full_database_has_zero_missing_images_and_all_exist_on_disk` passed; 0 missing images, 0 duplicate hashes |
| T-116 | REGRESSION | Full backend & frontend test suite pass with active daemons | PASS | Backend `pytest backend/tests`: 419 passed, 1 skipped in 57.99s; Frontend `vitest run`: 77/77 passed; `vite build` 0 errors |
