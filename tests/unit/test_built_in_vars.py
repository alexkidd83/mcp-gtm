"""Tests for gtm_mcp.tools.built_in_vars — enable/disable."""

from __future__ import annotations

from unittest.mock import patch

from gtm_mcp.config import SafetyConfig
from gtm_mcp.tools.built_in_vars import disable_built_in_variables, enable_built_in_variables

WS_KWARGS = dict(account_id="1", container_id="2", workspace_id="3")
TYPES = ["PAGE_URL", "PAGE_HOSTNAME"]
PARENT = "accounts/1/containers/2/workspaces/3"


# ---------------------------------------------------------------------------
# enable_built_in_variables
# ---------------------------------------------------------------------------


def test_enable_dry_run_returns_preview(config, mock_execute):
    with patch("gtm_mcp._read_only", False):
        result = enable_built_in_variables(config, **WS_KWARGS, variable_types=TYPES, dry_run=True)
    assert result["dry_run"] is True
    assert result["operation"] == "enable_built_in_variables"
    assert result["would_enable"] == TYPES
    assert result["parent"] == PARENT
    mock_execute.assert_not_called()


def test_enable_read_only_blocks(config, mock_execute):
    with patch("gtm_mcp._read_only", True):
        result = enable_built_in_variables(config, **WS_KWARGS, variable_types=TYPES, dry_run=True)
    assert "error" in result
    assert "read-only" in result["error"].lower()
    mock_execute.assert_not_called()


def test_enable_live_calls_api(config, mock_execute):
    config.safety = SafetyConfig(require_dry_run=False)
    mock_execute.return_value = {
        "builtInVariable": [
            {"name": "Page URL", "type": "PAGE_URL"},
            {"name": "Page Hostname", "type": "PAGE_HOSTNAME"},
        ]
    }
    with patch("gtm_mcp._read_only", False):
        result = enable_built_in_variables(
            config, **WS_KWARGS, variable_types=TYPES, dry_run=False
        )
    assert result["dry_run"] is False
    assert result["operation"] == "enable_built_in_variables"
    assert "PAGE_URL" in result["enabled"]
    mock_execute.assert_called_once_with(
        config,
        "accounts.containers.workspaces.built_in_variables.create",
        parent=PARENT,
        type=TYPES,
    )


# ---------------------------------------------------------------------------
# disable_built_in_variables
# ---------------------------------------------------------------------------


def test_disable_dry_run_returns_preview(config, mock_execute):
    with patch("gtm_mcp._read_only", False):
        result = disable_built_in_variables(
            config, **WS_KWARGS, variable_types=TYPES, dry_run=True
        )
    assert result["dry_run"] is True
    assert result["operation"] == "disable_built_in_variables"
    assert result["would_disable"] == TYPES
    assert result["parent"] == PARENT
    mock_execute.assert_not_called()


def test_disable_confirm_destructive_false_blocks(config, mock_execute):
    config.safety = SafetyConfig(require_dry_run=False)
    with patch("gtm_mcp._read_only", False):
        result = disable_built_in_variables(
            config,
            **WS_KWARGS,
            variable_types=TYPES,
            dry_run=False,
            confirm_destructive=False,
        )
    assert "error" in result
    assert "confirm" in result["error"].lower() or "destructive" in result["error"].lower()
    mock_execute.assert_not_called()


def test_disable_live_calls_api(config, mock_execute):
    config.safety = SafetyConfig(require_dry_run=False)
    mock_execute.return_value = {}
    with patch("gtm_mcp._read_only", False):
        result = disable_built_in_variables(
            config,
            **WS_KWARGS,
            variable_types=TYPES,
            dry_run=False,
            confirm_destructive=True,
        )
    assert result["dry_run"] is False
    assert result["operation"] == "disable_built_in_variables"
    assert result["disabled"] == TYPES
    mock_execute.assert_called_once_with(
        config,
        "accounts.containers.workspaces.built_in_variables.delete",
        parent=PARENT,
        type=TYPES,
    )
