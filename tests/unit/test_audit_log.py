"""Tests for gtm_mcp.tools.audit_log."""

from __future__ import annotations

import sys
from unittest.mock import patch

from gtm_mcp.tools.audit_log import get_audit_log


def test_get_audit_log_returns_structure():
    result = get_audit_log(limit=10)
    assert "entries" in result
    assert "total" in result
    assert isinstance(result["entries"], list)
    assert result["total"] == len(result["entries"])


def test_get_audit_log_handles_missing_module(monkeypatch):
    # Simulate ImportError from the audit module by temporarily hiding it.
    original = sys.modules.get("gtm_mcp.safety.audit")
    monkeypatch.setitem(sys.modules, "gtm_mcp.safety.audit", None)  # type: ignore[arg-type]
    try:
        result = get_audit_log(limit=5)
    finally:
        if original is not None:
            monkeypatch.setitem(sys.modules, "gtm_mcp.safety.audit", original)
        else:
            monkeypatch.delitem(sys.modules, "gtm_mcp.safety.audit", raising=False)
    assert result["entries"] == []
    assert result["total"] == 0
