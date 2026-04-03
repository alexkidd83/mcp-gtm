"""Tests for gtm_mcp.tools.tags."""

from __future__ import annotations

from unittest.mock import patch

from gtm_mcp.config import SafetyConfig
from gtm_mcp.tools.tags import create_tag, delete_tag, get_tag, list_tags, update_tag

WS_KWARGS = dict(account_id="1", container_id="2", workspace_id="3")
TAG_BODY = {
    "name": "GA4 Event",
    "type": "gaawe",
    "parameter": [{"key": "eventName", "type": "template", "value": "purchase"}],
}


def test_list_tags_success(config, mock_execute):
    mock_execute.return_value = {
        "tag": [
            {
                "tagId": "T1",
                "name": "GA4 Config",
                "type": "gaawc",
                "firingTriggerId": ["100"],
                "blockingTriggerId": [],
                "paused": False,
            }
        ]
    }
    result = list_tags(config, **WS_KWARGS)
    assert result["total"] == 1
    assert result["tags"][0]["tag_id"] == "T1"
    assert result["tags"][0]["type"] == "gaawc"
    mock_execute.assert_called_once_with(
        config,
        "accounts.containers.workspaces.tags.list",
        parent="accounts/1/containers/2/workspaces/3",
    )


def test_list_tags_api_error(config, mock_execute):
    mock_execute.return_value = {"error": "Rate limit", "status": 429}
    result = list_tags(config, **WS_KWARGS)
    assert "error" in result


def test_get_tag_success(config, mock_execute):
    mock_execute.return_value = {
        "tagId": "T1",
        "name": "GA4 Config",
        "type": "gaawc",
        "parameter": [{"type": "template", "key": "measurementId", "value": "G-XXX"}],
        "firingTriggerId": ["100"],
        "blockingTriggerId": [],
        "tagFiringOption": "oncePerEvent",
        "paused": False,
        "notes": "main config tag",
        "setupTag": [],
        "teardownTag": [],
    }
    result = get_tag(config, **WS_KWARGS, tag_id="T1")
    assert result["tag_id"] == "T1"
    assert result["parameter"][0]["key"] == "measurementId"
    assert result["tag_firing_option"] == "oncePerEvent"
    mock_execute.assert_called_once_with(
        config,
        "accounts.containers.workspaces.tags.get",
        path="accounts/1/containers/2/workspaces/3/tags/T1",
    )


def test_get_tag_api_error(config, mock_execute):
    mock_execute.return_value = {"error": "Not found", "status": 404}
    result = get_tag(config, **WS_KWARGS, tag_id="T999")
    assert result["error"] == "Not found"


def test_list_tags_empty(config, mock_execute):
    mock_execute.return_value = {"tag": []}
    result = list_tags(config, **WS_KWARGS)
    assert result["total"] == 0
    assert result["tags"] == []


def test_create_tag_blocked_in_read_only_mode(config, mock_execute):
    with patch("gtm_mcp._read_only", True):
        result = create_tag(config, **WS_KWARGS, tag=TAG_BODY, dry_run=True)
    assert "error" in result
    assert "read-only" in result["error"].lower()
    mock_execute.assert_not_called()


def test_create_tag_dry_run_preview(config, mock_execute):
    with patch("gtm_mcp._read_only", False):
        result = create_tag(config, **WS_KWARGS, tag=TAG_BODY, dry_run=True)
    assert result["dry_run"] is True
    assert result["operation"] == "create_tag"
    assert result["would_call"] == "accounts.containers.workspaces.tags.create"
    mock_execute.assert_not_called()


def test_create_tag_live_requires_dry_run_disabled_in_config(config, mock_execute):
    with patch("gtm_mcp._read_only", False):
        result = create_tag(config, **WS_KWARGS, tag=TAG_BODY, dry_run=False)
    assert "error" in result
    assert "require_dry_run" in result["error"]
    mock_execute.assert_not_called()


def test_create_tag_live_calls_api_when_allowed(config, mock_execute):
    config.safety = SafetyConfig(require_dry_run=False)
    mock_execute.return_value = {"tagId": "T100", **TAG_BODY}
    with patch("gtm_mcp._read_only", False):
        result = create_tag(config, **WS_KWARGS, tag=TAG_BODY, dry_run=False)
    assert result["dry_run"] is False
    assert result["tag"]["tag_id"] == "T100"
    mock_execute.assert_called_once_with(
        config,
        "accounts.containers.workspaces.tags.create",
        parent="accounts/1/containers/2/workspaces/3",
        body=TAG_BODY,
    )


def test_update_tag_live_calls_api_when_allowed(config, mock_execute):
    config.safety = SafetyConfig(require_dry_run=False)
    mock_execute.return_value = {"tagId": "T1", **TAG_BODY}
    with patch("gtm_mcp._read_only", False):
        result = update_tag(
            config,
            **WS_KWARGS,
            tag_id="T1",
            tag=TAG_BODY,
            dry_run=False,
        )
    assert result["dry_run"] is False
    assert result["tag"]["tag_id"] == "T1"
    mock_execute.assert_called_once_with(
        config,
        "accounts.containers.workspaces.tags.update",
        path="accounts/1/containers/2/workspaces/3/tags/T1",
        body=TAG_BODY,
    )


def test_delete_tag_blocked_operation(config, mock_execute):
    config.safety = SafetyConfig(blocked_operations=["delete_tag"])
    with patch("gtm_mcp._read_only", False):
        result = delete_tag(config, **WS_KWARGS, tag_id="T1", dry_run=True)
    assert "error" in result
    assert "blocked" in result["error"]
    mock_execute.assert_not_called()


def test_delete_tag_destructive_guard_blocks_without_confirm(config, mock_execute):
    config.safety = SafetyConfig(require_dry_run=False)
    with patch("gtm_mcp._read_only", False):
        result = delete_tag(
            config, **WS_KWARGS, tag_id="T1", dry_run=False, confirm_destructive=False
        )
    assert "error" in result
    assert "confirm_destructive" in result["hint"].lower()
    mock_execute.assert_not_called()


def test_delete_tag_live_calls_api_when_confirmed(config, mock_execute):
    config.safety = SafetyConfig(require_dry_run=False)
    mock_execute.return_value = {}
    with patch("gtm_mcp._read_only", False):
        result = delete_tag(
            config, **WS_KWARGS, tag_id="T1", dry_run=False, confirm_destructive=True
        )
    assert result["deleted"] is True
    assert result["tag_id"] == "T1"
    mock_execute.assert_called_once_with(
        config,
        "accounts.containers.workspaces.tags.delete",
        path="accounts/1/containers/2/workspaces/3/tags/T1",
    )
