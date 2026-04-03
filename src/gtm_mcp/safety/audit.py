"""Two-phase audit logging — attempt + result written to ~/.gtm-mcp/audit.jsonl."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

_AUDIT_PATH: Path = Path("~/.gtm-mcp/audit.jsonl").expanduser()


def _ensure_dir() -> None:
    _AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)


def _append(record: dict) -> None:
    _ensure_dir()
    with open(_AUDIT_PATH, "a") as f:
        f.write(json.dumps(record, default=str) + "\n")


def log_read(operation: str, **kwargs: object) -> None:
    """Log a read operation (debug-level only, not persisted)."""
    logger.debug("read op=%s %s", operation, kwargs)


def log_attempt(
    operation: str,
    *,
    dry_run: bool,
    container_id: str,
    **kwargs: object,
) -> str:
    """Log the *attempt* phase of a write operation.

    Returns a ``request_id`` (UUID4 string) used to correlate the subsequent
    :func:`log_result` call.
    """
    request_id = str(uuid.uuid4())
    record = {
        "phase": "attempt",
        "request_id": request_id,
        "operation": operation,
        "dry_run": dry_run,
        "container_id": container_id,
        "ts": datetime.now(timezone.utc).isoformat(),
        **kwargs,
    }
    _append(record)
    return request_id


def log_result(
    request_id: str,
    *,
    success: bool,
    error: str | None = None,
    entity_ids: list[str] | None = None,
) -> None:
    """Log the *result* phase, correlated to a previous attempt."""
    record: dict = {
        "phase": "result",
        "request_id": request_id,
        "success": success,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    if error is not None:
        record["error"] = error
    if entity_ids is not None:
        record["entity_ids"] = entity_ids
    _append(record)


def read_audit_log(limit: int = 50) -> list[dict]:
    """Return the last *limit* entries from the audit log."""
    if not _AUDIT_PATH.exists():
        return []
    lines = _AUDIT_PATH.read_text().strip().splitlines()
    tail = lines[-limit:] if limit < len(lines) else lines
    return [json.loads(line) for line in tail]
