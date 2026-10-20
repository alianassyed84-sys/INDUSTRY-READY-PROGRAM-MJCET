"""CSV source adapter for the bundled Amazon product review dataset.

Supported source
----------------
File: ``amazon.csv`` (1,465 rows, 1,351 unique products, ~9k unique reviews)
Location: configured via ``Settings.amazon_csv_path`` or the ``AMAZON_CSV_PATH``
environment variable.

CSV schema (columns)
--------------------
product_id, product_name, category, discounted_price, actual_price,
discount_percentage, rating, rating_count, about_product, user_id, user_name,
review_id, review_title, review_content, img_link, product_link

Multi-value columns
-------------------
The following columns are comma-separated multi-value strings — one entry per
reviewer on that product row:

    - ``user_id``      — always aligned with ``review_id`` (verified: 0 mismatches)
    - ``user_name``    — usually aligned; 11 rows mismatch → padded / truncated
    - ``review_id``    — source of truth for number of reviews per row
    - ``review_title`` — aligned with ``review_id``

``review_content`` contains commas *within* each review text, making reliable
comma-splitting impossible (1,265/1,465 rows fail alignment check).  Mitigation:
the full ``review_content`` cell is stored on the **first review** of each product
row; all subsequent reviews within the same row receive ``review_content=None``.
This is a documented limitation.

Limitations
-----------
- No live API fetch — dataset is a fixed local file.
- ``review_content`` stored on first review only (see above).
- No per-row timestamp in source; ``created_at`` is set by the DB server default.
"""

from __future__ import annotations

import csv
import logging
from collections.abc import Iterator
from pathlib import Path

from app.services.harvester.base import (
    NormalizedProduct,
    NormalizedReview,
    NormalizedUser,
    RecordTuple,
    SourceAdapter,
    SourceNotConfiguredError,
)
from app.services.harvester.normalizer import (
    clean_text,
    parse_percentage,
    parse_price,
    parse_rating,
    parse_rating_count,
)

logger = logging.getLogger(__name__)

#: Maximum characters stored for large text fields (about_product, review_content)
_MAX_TEXT = 10_000
#: Maximum characters for URLs
_MAX_URL = 2048


class CsvAmazonAdapter(SourceAdapter):
    """Source adapter that reads the bundled Amazon review CSV dataset."""

    source_id = "csv_amazon"

    def __init__(self, csv_path: str) -> None:
        path = Path(csv_path)
        if not path.exists():
            raise SourceNotConfiguredError(
                f"Amazon CSV not found at '{csv_path}'. "
                "Set AMAZON_CSV_PATH to the correct file location."
            )
        self._csv_path = path
        self.warning_count: int = 0

    # ------------------------------------------------------------------
    # SourceAdapter interface
    # ------------------------------------------------------------------

    def records(self) -> Iterator[RecordTuple]:
        """Yield one ``(product, users, reviews)`` tuple per CSV row."""
        with self._csv_path.open(encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            for row_num, row in enumerate(reader, start=2):  # 2 = first data row
                try:
                    yield from self._parse_row(row, row_num)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("csv_adapter row=%d parse_error=%s", row_num, exc)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _parse_row(self, row: dict[str, str], row_num: int) -> Iterator[RecordTuple]:
        """Parse one CSV row into a (product, users, reviews) tuple.

        Yields nothing if the row lacks a usable ``product_id`` or ``review_id``.
        """
        product_id = clean_text(row.get("product_id"))
        if not product_id:
            logger.debug("csv_adapter row=%d skip: missing product_id", row_num)
            return

        product = NormalizedProduct(
            product_id=product_id,
            product_name=clean_text(row.get("product_name")) or "",
            category=clean_text(row.get("category")),
            discounted_price=parse_price(row.get("discounted_price")),
            actual_price=parse_price(row.get("actual_price")),
            discount_percentage=parse_percentage(row.get("discount_percentage")),
            rating=parse_rating(row.get("rating")),
            rating_count=parse_rating_count(row.get("rating_count")),
            about_product=clean_text(row.get("about_product"), max_len=_MAX_TEXT),
            img_link=clean_text(row.get("img_link"), max_len=_MAX_URL),
            product_link=clean_text(row.get("product_link"), max_len=_MAX_URL),
        )

        # --- multi-value columns -----------------------------------------
        raw_user_ids = self._split_csv(row.get("user_id", ""))
        raw_user_names = self._split_csv(row.get("user_name", ""))
        raw_review_ids = self._split_csv(row.get("review_id", ""))
        raw_review_titles = self._split_csv(row.get("review_title", ""))

        if not raw_review_ids:
            logger.debug("csv_adapter row=%d skip: no review_ids", row_num)
            return

        # Align user_names to user_ids (pad with "Anonymous" or truncate)
        user_names = self._align_list(
            raw_user_names, len(raw_user_ids), default="Anonymous"
        )

        users: list[NormalizedUser] = []
        for uid, uname in zip(raw_user_ids, user_names, strict=False):
            uid = uid.strip()
            if uid:
                users.append(
                    NormalizedUser(
                        user_id=uid,
                        user_name=clean_text(uname) or "Anonymous",
                    )
                )

        # Build uid lookup for review → user linkage
        uid_by_index = {i: u.user_id for i, u in enumerate(users) if u.user_id}

        # Check alignment for review text:
        # If single review in row, map 1:1 directly
        # If multiple reviews: titles aligned if count matches; content is stored
        # on the first review only (see module docstring on comma-splitting limitation).
        is_single_review = len(raw_review_ids) == 1
        titles_match = is_single_review or (
            len(raw_review_titles) == len(raw_review_ids)
        )

        reviews: list[NormalizedReview] = []
        for idx, review_id in enumerate(raw_review_ids):
            review_id = review_id.strip()
            if not review_id:
                continue
            title_val = (
                clean_text(row.get("review_title"))
                if is_single_review
                else (
                    clean_text(raw_review_titles[idx])
                    if titles_match and idx < len(raw_review_titles)
                    else None
                )
            )
            content_val = (
                clean_text(row.get("review_content"), max_len=_MAX_TEXT)
                if idx == 0
                else None
            )
            reviews.append(
                NormalizedReview(
                    review_id=review_id,
                    product_id=product_id,
                    user_id=uid_by_index.get(idx),
                    rating=None,  # Amazon CSV has aggregate rating, not per-review
                    review_title=title_val,
                    review_content=content_val,
                )
            )

        yield product, users, reviews

    @staticmethod
    def _split_csv(value: str) -> list[str]:
        """Split a comma-separated multi-value cell into a trimmed list."""
        if not value or not value.strip():
            return []
        return [item.strip() for item in value.split(",")]

    @staticmethod
    def _align_list(lst: list[str], target_len: int, default: str) -> list[str]:
        """Pad or truncate *lst* to *target_len*, using *default* for padding."""
        if len(lst) >= target_len:
            return lst[:target_len]
        return lst + [default] * (target_len - len(lst))
