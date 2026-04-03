"""Tests for gtm_mcp.tools.workspaces — create_workspace."""

from __future__ import annotations

from unittest.mock import patch

from gtm_mcp.config import SafetyConfig
from gtm_mcp.tools.workspaces import create_workspace

CONTAINER_KWARGS = dict(account_id="1", container_id="2")
PARENT = "accounts/1/containers/2"


def test_create_workspace_dry_run_returns_preview(config, mock_execute):
    with patch("gtm_mcp._read_only", False):
        result = create_workspace(
            config, **CONTAINER_KWARGS, name="My Workspace", description="test ws", dry_run=True
        )
    assert result["dry_run"] is True
    assert result["operation"] == "create_workspace"
    assert result["parent"] == PARENT
    assert result["workspace_preview"]["name"] == "My Workspace"
    assert result["workspace_preview"]["description"] == "test ws"
    mock_execute.assert_not_called()


def test_create_workspace_read_only_blocks(config, mock_execute):
    with patch("gtm_mcp._read_only", True):
        result = create_workspace(
            config, **CONTAINER_KWARGS, name="My Workspace", dry_run=True
        )
    assert "error" in result
    assert "read-only" in result["error"].lower()
    mock_execute.assert_not_called()


def test_create_workspace_live_calls_api(config, mock_execute):
    config.safety = SafetyConfig(require_dry_run=False)
    mock_execute.return_value = {
        "workspaceId": "W42",
        "name": "My Workspace",
        "description": "test ws",
    }
    with patch("gtm_mcp._read_only", False):
        result = create_workspace(
            config,
            **CONTAINER_KWARGS,
            name="My Workspace",
            description="test ws",
            dry_run=False,
        )
    assert result["dry_run"] is False
    assert result["operation"] == "create_workspace"
    assert result["workspace"]["workspace_id"] == "W42"
    assert result["workspace"]["name"] == "My Workspace"
    mock_execute.assert_called_once_with(
        config,
        "accounts.containers.workspaces.create",
        parent=PARENT,
        body={"name": "My Workspace", "description": "test ws"},
    )
