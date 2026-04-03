"""Tests for gtm_mcp.tools.variables — list_variables, get_variable, write ops."""

from __future__ import annotations

from unittest.mock import patch

from gtm_mcp.config import SafetyConfig
from gtm_mcp.tools.variables import (
    create_variable,
    delete_variable,
    get_variable,
    list_variables,
    update_variable,
)

WS_KWARGS = dict(account_id="1", container_id="2", workspace_id="3")


def test_list_variables_success(config, mock_execute):
    mock_execute.return_value = {
        "variable": [
            {"variableId": "V1", "name": "dlv - ecommerce", "type": "v"},
            {"variableId": "V2", "name": "cjs - timestamp", "type": "jsm"},
        ]
    }
    result = list_variables(config, **WS_KWARGS)
    assert result["total"] == 2
    assert result["variables"][0]["variable_id"] == "V1"
    assert result["variables"][1]["type"] == "jsm"
    mock_execute.assert_called_once_with(
        config,
        "accounts.containers.workspaces.variables.list",
        parent="accounts/1/containers/2/workspaces/3",
    )


def test_list_variables_api_error(config, mock_execute):
    mock_execute.return_value = {"error": "Auth failed", "status": 401}
    result = list_variables(config, **WS_KWARGS)
    assert "error" in result


def test_get_variable_success(config, mock_execute):
    mock_execute.return_value = {
        "variableId": "V1",
        "name": "dlv - ecommerce",
        "type": "v",
        "parameter": [{"type": "template", "key": "name", "value": "ecommerce"}],
        "formatValue": {"convertNullToValue": {"type": "template", "value": ""}},
        "notes": "data layer variable",
    }
    result = get_variable(config, **WS_KWARGS, variable_id="V1")
    assert result["variable_id"] == "V1"
    assert result["parameter"][0]["key"] == "name"
    assert result["format_value"]["convertNullToValue"]["type"] == "template"
    mock_execute.assert_called_once_with(
        config,
        "accounts.containers.workspaces.variables.get",
        path="accounts/1/containers/2/workspaces/3/variables/V1",
    )


def test_get_variable_api_error(config, mock_execute):
    mock_execute.return_value = {"error": "Not found", "status": 404}
    result = get_variable(config, **WS_KWARGS, variable_id="V999")
    assert result["error"] == "Not found"


def test_list_variables_empty(config, mock_execute):
    mock_execute.return_value = {"variable": []}
    result = list_variables(config, **WS_KWARGS)
    assert result["total"] == 0
    assert result["variables"] == []


VARIABLE_BODY = {
    "name": "dlv - transaction_id",
    "type": "v",
    "parameter": [{"type": "template", "key": "name", "value": "transactionId"}],
}


# ---------------------------------------------------------------------------
# create_variable
# ---------------------------------------------------------------------------


def test_create_variable_dry_run_returns_preview(config, mock_execute):
    with patch("gtm_mcp._read_only", False):
        result = create_variable(config, **WS_KWARGS, variable=VARIABLE_BODY, dry_run=True)
    assert result["dry_run"] is True
    assert result["operation"] == "create_variable"
    assert result["would_call"] == "accounts.containers.workspaces.variables.create"
    mock_execute.assert_not_called()


def test_create_variable_read_only_blocks(config, mock_execute):
    with patch("gtm_mcp._read_only", True):
        result = create_variable(config, **WS_KWARGS, variable=VARIABLE_BODY, dry_run=True)
    assert "error" in result
    assert "read-only" in result["error"].lower()
    mock_execute.assert_not_called()


def test_create_variable_live_calls_api(config, mock_execute):
    config.safety = SafetyConfig(require_dry_run=False)
    mock_execute.return_value = {"variableId": "V100", **VARIABLE_BODY}
    with patch("gtm_mcp._read_only", False):
        result = create_variable(config, **WS_KWARGS, variable=VARIABLE_BODY, dry_run=False)
    assert result["dry_run"] is False
    assert result["variable"]["variable_id"] == "V100"
    mock_execute.assert_called_once_with(
        config,
        "accounts.containers.workspaces.variables.create",
        parent="accounts/1/containers/2/workspaces/3",
        body=VARIABLE_BODY,
    )


# ---------------------------------------------------------------------------
# update_variable
# ---------------------------------------------------------------------------


def test_update_variable_dry_run_returns_preview(config, mock_execute):
    with patch("gtm_mcp._read_only", False):
        result = update_variable(
            config, **WS_KWARGS, variable_id="V1", variable=VARIABLE_BODY, dry_run=True
        )
    assert result["dry_run"] is True
    assert result["operation"] == "update_variable"
    assert result["would_call"] == "accounts.containers.workspaces.variables.update"
    mock_execute.assert_not_called()


def test_update_variable_live_calls_api(config, mock_execute):
    config.safety = SafetyConfig(require_dry_run=False)
    mock_execute.return_value = {"variableId": "V1", **VARIABLE_BODY}
    with patch("gtm_mcp._read_only", False):
        result = update_variable(
            config, **WS_KWARGS, variable_id="V1", variable=VARIABLE_BODY, dry_run=False
        )
    assert result["dry_run"] is False
    assert result["variable"]["variable_id"] == "V1"
    mock_execute.assert_called_once_with(
        config,
        "accounts.containers.workspaces.variables.update",
        path="accounts/1/containers/2/workspaces/3/variables/V1",
        body=VARIABLE_BODY,
    )


# ---------------------------------------------------------------------------
# delete_variable
# ---------------------------------------------------------------------------


def test_delete_variable_dry_run_returns_preview(config, mock_execute):
    with patch("gtm_mcp._read_only", False):
        result = delete_variable(config, **WS_KWARGS, variable_id="V1", dry_run=True)
    assert result["dry_run"] is True
    assert result["operation"] == "delete_variable"
    assert result["would_call"] == "accounts.containers.workspaces.variables.delete"
    mock_execute.assert_not_called()


def test_delete_variable_confirm_destructive_false_blocks(config, mock_execute):
    config.safety = SafetyConfig(require_dry_run=False)
    with patch("gtm_mcp._read_only", False):
        result = delete_variable(
            config, **WS_KWARGS, variable_id="V1", dry_run=False, confirm_destructive=False
        )
    assert "error" in result
    assert "destructive" in result["error"].lower()
    mock_execute.assert_not_called()


def test_delete_variable_live_calls_api(config, mock_execute):
    config.safety = SafetyConfig(require_dry_run=False)
    mock_execute.return_value = {}
    with patch("gtm_mcp._read_only", False):
        result = delete_variable(
            config,
            **WS_KWARGS,
            variable_id="V1",
            dry_run=False,
            confirm_destructive=True,
        )
    assert result["deleted"] is True
    assert result["variable_id"] == "V1"
    mock_execute.assert_called_once_with(
        config,
        "accounts.containers.workspaces.variables.delete",
        path="accounts/1/containers/2/workspaces/3/variables/V1",
    )
