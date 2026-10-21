# Synthesized Decisions

## DEC-001: Authorized Amazon Data Providers & Scraping Prohibition
- **Source**: `docs/authorized_providers.md`
- **Status**: Locked (Accepted)
- **Scope**: `amazon-data-providers`, `data-collection`
- **Decision Statement**:
  1. Live scraping of Amazon.in web pages is strictly forbidden (violates project constraints, terms of service, and anti-abuse policies).
  2. Amazon Product Advertising API (PA-API 5.0) provides metadata and pricing snapshots, but expressly forbids caching or extracting customer review text/prose.
  3. Live external API calls remain disabled by default when external credentials are not configured (`AMAZON_PROVIDER=mock` supported for integration tests; explicit `ProviderNotConfiguredError` raised when live credentials absent).
  4. Review NLP analysis relies on authorized partner feeds or pre-ingested review corpora (`csv_amazon`).

## DEC-002: Minimal-Diff Scheduler Policy
- **Source**: `docs/price_monitoring.md`
- **Status**: Locked (Accepted)
- **Scope**: `price-monitoring`, `job-scheduling`
- **Decision Statement**:
  In alignment with minimal-diff engineering (Ponytail ladder), a heavyweight background queue (Celery, ARQ, Redis Queue) is not introduced without explicit infrastructure provisioning. Price monitoring provides stateless on-demand polling endpoints (`/check-price`, `/price-history`), deferring message-broker workers to future infrastructure milestones.

## DEC-003: Review Content Comma-Splitting Fallback
- **Source**: `docs/harvester.md`
- **Status**: Locked (Accepted)
- **Scope**: `harvester`, `csv-adapter`
- **Decision Statement**:
  In multi-review CSV rows where review content contains internal commas preventing deterministic 1:1 comma splitting with review IDs, the full content text is assigned to the first review (`idx == 0`); secondary reviews are assigned `review_content = None`.
