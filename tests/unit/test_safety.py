"""Tests for gtm_mcp.safety.guards — read-only, container allowlist, blocked ops."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from gtm_mcp.config import GtmMcpConfig, SafetyConfig
from gtm_mcp.safety.guards import (
    SafetyViolation,
    check_blocked_operation,
    check_container_allowed,
    check_destructive,
    check_read_only,
    check_write_safety,
)


# --- check_read_only ---


def test_check_read_only_returns_error_when_true():
    with patch("gtm_mcp._read_only", True):
        result = check_read_only()
    assert result is not None
    assert "error" in result
    assert "read-only" in result["error"].lower()


def test_check_read_only_returns_none_when_false():
    with patch("gtm_mcp._read_only", False):
        result = check_read_only()
    assert result is None


# --- check_container_allowed ---


def test_container_allowed_empty_list_allows_all():
    cfg = SafetyConfig(allowed_container_ids=[])
    # Should not raise
    check_container_allowed("ANY-CONTAINER", cfg)


def test_container_allowed_rejects_unlisted():
    cfg = SafetyConfig(allowed_container_ids=["GTM-GOOD"])
    with pytest.raises(SafetyViolation, match="GTM-BAD"):
        check_container_allowed("GTM-BAD", cfg)


def test_container_allowed_permits_listed():
    cfg = SafetyConfig(allowed_container_ids=["GTM-GOOD", "GTM-ALSO"])
    # Should not raise
    check_container_allowed("GTM-GOOD", cfg)


# --- check_blocked_operation ---


def test_blocked_operation_raises_when_blocked():
    cfg = SafetyConfig(blocked_operations=["delete_tag", "delete_trigger"])
    with pytest.raises(SafetyViolation, match="delete_tag"):
        check_blocked_operation("delete_tag", cfg)


def test_blocked_operation_allows_unblocked():
    cfg = SafetyConfig(blocked_operations=["delete_tag"])
    # Should not raise
    check_blocked_operation("list_tags", cfg)


def test_blocked_operation_empty_list_allows_all():
    cfg = SafetyConfig(blocked_operations=[])
    # Should not raise
    check_blocked_operation("delete_tag", cfg)


# --- check_write_safety ---


def test_check_write_safety_returns_none_when_all_pass():
    config = GtmMcpConfig(safety=SafetyConfig(require_dry_run=False))
    with patch("gtm_mcp._read_only", False):
        result = check_write_safety(
            config, container_id="C1", operation="create_tag", dry_run=False
        )
    assert result is None


def test_check_write_safety_returns_error_when_read_only():
    config = GtmMcpConfig()
    with patch("gtm_mcp._read_only", True):
        result = check_write_safety(
            config, container_id="C1", operation="create_tag", dry_run=True
        )
    assert result is not None
    assert "read-only" in result["error"].lower()


def test_check_write_safety_returns_error_when_container_not_allowed():
    config = GtmMcpConfig(
        safety=SafetyConfig(allowed_container_ids=["GTM-OK"])
    )
    with patch("gtm_mcp._read_only", False):
        result = check_write_safety(
            config, container_id="GTM-BAD", operation="create_tag", dry_run=True
        )
    assert result is not None
    assert "GTM-BAD" in result["error"]


def test_check_write_safety_returns_error_when_operation_blocked():
    config = GtmMcpConfig(
        safety=SafetyConfig(blocked_operations=["delete_tag"])
    )
    with patch("gtm_mcp._read_only", False):
        result = check_write_safety(
            config, container_id="C1", operation="delete_tag", dry_run=True
        )
    assert result is not None
    assert "blocked" in result["error"]


def test_check_write_safety_returns_error_when_require_dry_run_and_live():
    config = GtmMcpConfig(safety=SafetyConfig(require_dry_run=True))
    with patch("gtm_mcp._read_only", False):
        result = check_write_safety(
            config, container_id="C1", operation="create_tag", dry_run=False
        )
    assert result is not None
    assert "require_dry_run" in result["error"]


# --- check_destructive ---


def test_check_destructive_false_returns_error():
    result = check_destructive(False)
    assert result is not None
    assert "error" in result
    assert "confirm_destructive" in result["hint"].lower()


def test_check_destructive_true_returns_none():
    result = check_destructive(True)
    assert result is None
