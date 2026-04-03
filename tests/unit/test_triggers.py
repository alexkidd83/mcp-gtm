"""Tests for gtm_mcp.tools.triggers — list_triggers, get_trigger, write ops."""

from __future__ import annotations

from unittest.mock import patch

from gtm_mcp.config import SafetyConfig
from gtm_mcp.tools.triggers import (
    create_trigger,
    delete_trigger,
    get_trigger,
    list_triggers,
    update_trigger,
)

WS_KWARGS = dict(account_id="1", container_id="2", workspace_id="3")


def test_list_triggers_success(config, mock_execute):
    mock_execute.return_value = {
        "trigger": [
            {
                "triggerId": "TR1",
                "name": "All Pages",
                "type": "pageview",
                "customEventFilter": [],
                "filter": [],
            }
        ]
    }
    result = list_triggers(config, **WS_KWARGS)
    assert result["total"] == 1
    assert result["triggers"][0]["trigger_id"] == "TR1"
    assert result["triggers"][0]["type"] == "pageview"
    mock_execute.assert_called_once_with(
        config,
        "accounts.containers.workspaces.triggers.list",
        parent="accounts/1/containers/2/workspaces/3",
    )


def test_list_triggers_api_error(config, mock_execute):
    mock_execute.return_value = {"error": "Forbidden", "status": 403}
    result = list_triggers(config, **WS_KWARGS)
    assert "error" in result


def test_get_trigger_success(config, mock_execute):
    mock_execute.return_value = {
        "triggerId": "TR1",
        "name": "All Pages",
        "type": "pageview",
        "customEventFilter": [],
        "filter": [],
        "autoEventFilter": [],
        "waitForTags": {"value": "false"},
        "checkValidation": {},
        "uniqueTriggerId": "uid-123",
        "notes": "fires on every page",
    }
    result = get_trigger(config, **WS_KWARGS, trigger_id="TR1")
    assert result["trigger_id"] == "TR1"
    assert result["unique_trigger_id"] == "uid-123"
    assert result["wait_for_tags"] == {"value": "false"}
    mock_execute.assert_called_once_with(
        config,
        "accounts.containers.workspaces.triggers.get",
        path="accounts/1/containers/2/workspaces/3/triggers/TR1",
    )


def test_get_trigger_api_error(config, mock_execute):
    mock_execute.return_value = {"error": "Not found", "status": 404}
    result = get_trigger(config, **WS_KWARGS, trigger_id="TR999")
    assert result["error"] == "Not found"


def test_list_triggers_empty(config, mock_execute):
    mock_execute.return_value = {"trigger": []}
    result = list_triggers(config, **WS_KWARGS)
    assert result["total"] == 0
    assert result["triggers"] == []


TRIGGER_BODY = {
    "name": "All Pages",
    "type": "PAGEVIEW",
}


# ---------------------------------------------------------------------------
# create_trigger
# ---------------------------------------------------------------------------


def test_create_trigger_dry_run_returns_preview(config, mock_execute):
    with patch("gtm_mcp._read_only", False):
        result = create_trigger(config, **WS_KWARGS, trigger=TRIGGER_BODY, dry_run=True)
    assert result["dry_run"] is True
    assert result["operation"] == "create_trigger"
    assert result["would_call"] == "accounts.containers.workspaces.triggers.create"
    mock_execute.assert_not_called()


def test_create_trigger_read_only_blocks(config, mock_execute):
    with patch("gtm_mcp._read_only", True):
        result = create_trigger(config, **WS_KWARGS, trigger=TRIGGER_BODY, dry_run=True)
    assert "error" in result
    assert "read-only" in result["error"].lower()
    mock_execute.assert_not_called()


def test_create_trigger_live_calls_api(config, mock_execute):
    config.safety = SafetyConfig(require_dry_run=False)
    mock_execute.return_value = {"triggerId": "TR100", **TRIGGER_BODY}
    with patch("gtm_mcp._read_only", False):
        result = create_trigger(config, **WS_KWARGS, trigger=TRIGGER_BODY, dry_run=False)
    assert result["dry_run"] is False
    assert result["trigger"]["trigger_id"] == "TR100"
    mock_execute.assert_called_once_with(
        config,
        "accounts.containers.workspaces.triggers.create",
        parent="accounts/1/containers/2/workspaces/3",
        body=TRIGGER_BODY,
    )


# ---------------------------------------------------------------------------
# update_trigger
# ---------------------------------------------------------------------------


def test_update_trigger_dry_run_returns_preview(config, mock_execute):
    with patch("gtm_mcp._read_only", False):
        result = update_trigger(
            config, **WS_KWARGS, trigger_id="TR1", trigger=TRIGGER_BODY, dry_run=True
        )
    assert result["dry_run"] is True
    assert result["operation"] == "update_trigger"
    assert result["would_call"] == "accounts.containers.workspaces.triggers.update"
    mock_execute.assert_not_called()


def test_update_trigger_live_calls_api(config, mock_execute):
    config.safety = SafetyConfig(require_dry_run=False)
    mock_execute.return_value = {"triggerId": "TR1", **TRIGGER_BODY}
    with patch("gtm_mcp._read_only", False):
        result = update_trigger(
            config, **WS_KWARGS, trigger_id="TR1", trigger=TRIGGER_BODY, dry_run=False
        )
    assert result["dry_run"] is False
    assert result["trigger"]["trigger_id"] == "TR1"
    mock_execute.assert_called_once_with(
        config,
        "accounts.containers.workspaces.triggers.update",
        path="accounts/1/containers/2/workspaces/3/triggers/TR1",
        body=TRIGGER_BODY,
    )


# ---------------------------------------------------------------------------
# delete_trigger
# ---------------------------------------------------------------------------


def test_delete_trigger_dry_run_returns_preview(config, mock_execute):
    with patch("gtm_mcp._read_only", False):
        result = delete_trigger(config, **WS_KWARGS, trigger_id="TR1", dry_run=True)
    assert result["dry_run"] is True
    assert result["operation"] == "delete_trigger"
    assert result["would_call"] == "accounts.containers.workspaces.triggers.delete"
    mock_execute.assert_not_called()


def test_delete_trigger_confirm_destructive_false_blocks(config, mock_execute):
    config.safety = SafetyConfig(require_dry_run=False)
    with patch("gtm_mcp._read_only", False):
        result = delete_trigger(
            config, **WS_KWARGS, trigger_id="TR1", dry_run=False, confirm_destructive=False
        )
    assert "error" in result
    assert "destructive" in result["error"].lower()
    mock_execute.assert_not_called()


def test_delete_trigger_live_calls_api(config, mock_execute):
    config.safety = SafetyConfig(require_dry_run=False)
    mock_execute.return_value = {}
    with patch("gtm_mcp._read_only", False):
        result = delete_trigger(
            config,
            **WS_KWARGS,
            trigger_id="TR1",
            dry_run=False,
            confirm_destructive=True,
        )
    assert result["deleted"] is True
    assert result["trigger_id"] == "TR1"
    mock_execute.assert_called_once_with(
        config,
        "accounts.containers.workspaces.triggers.delete",
        path="accounts/1/containers/2/workspaces/3/triggers/TR1",
    )
