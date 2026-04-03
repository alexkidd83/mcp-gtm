"""GTM audit log tools."""

from __future__ import annotations

from typing import Any


def get_audit_log(*, limit: int = 50) -> dict[str, Any]:
    """Read recent mutation audit entries."""
    try:
        from gtm_mcp.safety.audit import read_audit_log

        entries = read_audit_log(limit=limit)
    except (ImportError, Exception):
        entries = []
    return {"entries": entries, "total": len(entries)}
