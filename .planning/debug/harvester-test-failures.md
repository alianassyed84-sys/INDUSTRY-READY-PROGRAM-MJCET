---
status: resolved
trigger: "please complete it /gsd-debug"
created: 2026-10-19
updated: 2026-10-19
slug: harvester-test-failures
symptoms:
  expected: "All 190 tests pass and ruff check/format passes."
  actual: "3 tests fail: test_multi_review_row (None == 'Loved it.') and test_post_jobs_invalid_source / test_post_jobs_extra_field_rejected (503 == 422)."
  errors: "AssertionError in tests/test_harvester.py and tests/test_harvester_api.py"
  timeline: "Milestone 3 Harvester implementation"
  reproduction: "pytest in backend/"
---

## Resolution
- root_cause:
  1. `app/services/harvester/csv_adapter.py` attempted to split `review_content` by commas and match part counts to `review_id` count, evaluating to `None` for all reviews on mismatch instead of attaching the full content blob to the first review (`idx == 0`) and `None` to subsequent reviews as documented.
  2. `app/core/database.py`'s `get_db` dependency was raising `HTTPException(503)` eagerly when `DATABASE_URL` was unset, preempting FastAPI's Pydantic schema validation of request bodies (which should return 422 for invalid requests).
- fix:
  1. Updated `csv_adapter.py` to assign `content_val = clean_text(row.get("review_content"), max_len=_MAX_TEXT) if idx == 0 else None`.
  2. Updated `app/core/database.py` so `get_db` yields `None` when `DATABASE_URL` is unconfigured, allowing Pydantic validation to run and letting the route handlers enforce `_require_db(settings)` (503).
  3. Cleaned up lint and formatting across `backend/` to ensure `ruff check .` and `ruff format --check .` cleanly pass.
- verification: "All 190 pytest unit tests passing (100%), ruff checks passed, ruff formatting verified."
- files_changed:
  - `backend/app/services/harvester/csv_adapter.py`
  - `backend/app/core/database.py`
  - `backend/app/api/v1/harvester.py`
  - `docs/harvester.md`
  - `README.md`
