"""Tests for gtm_mcp.safety.audit — two-phase audit logging."""

from __future__ import annotations

import uuid

from gtm_mcp.safety.audit import log_attempt, log_result, read_audit_log


def test_log_attempt_returns_uuid():
    request_id = log_attempt("create_tag", dry_run=True, container_id="C1")
    # Should be a valid UUID4 string
    parsed = uuid.UUID(request_id, version=4)
    assert str(parsed) == request_id


def test_attempt_and_result_write_entries():
    request_id = log_attempt("update_tag", dry_run=False, container_id="C2")
    log_result(request_id, success=True)

    entries = read_audit_log()
    assert len(entries) == 2

    attempt = entries[0]
    assert attempt["phase"] == "attempt"
    assert attempt["request_id"] == request_id
    assert attempt["operation"] == "update_tag"
    assert attempt["dry_run"] is False
    assert attempt["container_id"] == "C2"

    result = entries[1]
    assert result["phase"] == "result"
    assert result["request_id"] == request_id
    assert result["success"] is True


def test_read_audit_log_limit():
    # Write 3 pairs (6 entries)
    for i in range(3):
        rid = log_attempt(f"op_{i}", dry_run=True, container_id="C1")
        log_result(rid, success=True)

    all_entries = read_audit_log()
    assert len(all_entries) == 6

    limited = read_audit_log(limit=1)
    assert len(limited) == 1
    # Should be the very last entry (a result record)
    assert limited[0]["phase"] == "result"


def test_read_audit_log_empty_when_no_file():
    # The autouse fixture gives us a fresh tmp dir; no writes yet beyond this test.
    # We need to ensure the file doesn't exist for this test.
    from gtm_mcp.safety import audit as _mod

    original = _mod._AUDIT_PATH
    import tempfile, pathlib  # noqa: E401

    _mod._AUDIT_PATH = pathlib.Path(tempfile.mkdtemp()) / "nonexistent.jsonl"
    try:
        assert read_audit_log() == []
    finally:
        _mod._AUDIT_PATH = original
