"""Structured process logging without sensitive fields."""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.config import Settings


class StructuredFormatter(logging.Formatter):
    """Emit compact key=value log lines suitable for local development."""

    def format(self, record: logging.LogRecord) -> str:
        timestamp = self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S")
        parts = [
            f"ts={timestamp}",
            f"level={record.levelname}",
            f"logger={record.name}",
            f"msg={record.getMessage()}",
        ]
        request_id = getattr(record, "request_id", None)
        path = getattr(record, "path", None)
        if request_id:
            parts.append(f"request_id={request_id}")
        if path:
            parts.append(f"path={path}")
        if record.exc_info:
            parts.append("exc=1")
        return " ".join(parts)


def configure_logging(settings: Settings) -> None:
    """Configure the root logger once for the process."""
    level_name = settings.log_level.upper()
    level = getattr(logging, level_name, logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
