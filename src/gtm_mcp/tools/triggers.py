"""GTM Trigger tools."""

from __future__ import annotations

from typing import Any

from gtm_mcp.api import client
from gtm_mcp.config import GtmMcpConfig
from gtm_mcp.safety.guards import check_destructive, check_write_safety


try:
    from gtm_mcp.safety.audit import log_attempt, log_result
except ImportError:  # pragma: no cover
    def log_attempt(*a: Any, **kw: Any) -> str:  # type: ignore[misc]
        return "no-audit"

    def log_result(*a: Any, **kw: Any) -> None:  # type: ignore[misc]
        pass


def _workspace_parent(account_id: str, container_id: str, workspace_id: str) -> str:
    return f"accounts/{account_id}/containers/{container_id}/workspaces/{workspace_id}"


def _trigger_path(
    account_id: str, container_id: str, workspace_id: str, trigger_id: str
) -> str:
    return f"{_workspace_parent(account_id, container_id, workspace_id)}/triggers/{trigger_id}"


def _normalise_trigger(trigger: dict[str, Any]) -> dict[str, Any]:
    return {
        "trigger_id": trigger.get("triggerId", ""),
        "name": trigger.get("name", ""),
        "type": trigger.get("type", ""),
        "custom_event_filter": trigger.get("customEventFilter", []),
        "filter": trigger.get("filter", []),
        "auto_event_filter": trigger.get("autoEventFilter", []),
        "wait_for_tags": trigger.get("waitForTags", {}),
        "check_validation": trigger.get("checkValidation", {}),
        "unique_trigger_id": trigger.get("uniqueTriggerId", ""),
        "notes": trigger.get("notes", ""),
        "fingerprint": trigger.get("fingerprint", ""),
    }


def list_triggers(
    config: GtmMcpConfig,
    *,
    account_id: str,
    container_id: str,
    workspace_id: str,
) -> dict[str, Any]:
    """List all triggers in a GTM workspace."""
    parent = _workspace_parent(account_id, container_id, workspace_id)
    response = client.execute(
        config, "accounts.containers.workspaces.triggers.list", parent=parent
    )
    if "error" in response:
        return response

    triggers = response.get("trigger", [])
    return {
        "triggers": [
            {
                "trigger_id": t.get("triggerId", ""),
                "name": t.get("name", ""),
                "type": t.get("type", ""),
                "custom_event_filter": t.get("customEventFilter", []),
                "filter": t.get("filter", []),
            }
            for t in triggers
        ],
        "total": len(triggers),
    }


def get_trigger(
    config: GtmMcpConfig,
    *,
    account_id: str,
    container_id: str,
    workspace_id: str,
    trigger_id: str,
) -> dict[str, Any]:
    """Get full details for a single trigger, including filter conditions."""
    path = _trigger_path(account_id, container_id, workspace_id, trigger_id)
    response = client.execute(
        config, "accounts.containers.workspaces.triggers.get", path=path
    )
    if "error" in response:
        return response

    return {
        "trigger_id": response.get("triggerId", ""),
        "name": response.get("name", ""),
        "type": response.get("type", ""),
        "custom_event_filter": response.get("customEventFilter", []),
        "filter": response.get("filter", []),
        "auto_event_filter": response.get("autoEventFilter", []),
        "wait_for_tags": response.get("waitForTags", {}),
        "check_validation": response.get("checkValidation", {}),
        "unique_trigger_id": response.get("uniqueTriggerId", ""),
        "notes": response.get("notes", ""),
    }


def create_trigger(
    config: GtmMcpConfig,
    *,
    account_id: str,
    container_id: str,
    workspace_id: str,
    trigger: dict[str, Any],
    dry_run: bool = True,
) -> dict[str, Any]:
    """Create a trigger in a GTM workspace (Gate 2, guarded)."""
    op_name = "create_trigger"
    guard_error = check_write_safety(
        config,
        container_id=container_id,
        operation=op_name,
        dry_run=dry_run,
    )
    if guard_error is not None:
        return guard_error

    parent = _workspace_parent(account_id, container_id, workspace_id)
    request_id = log_attempt(op_name, dry_run=dry_run, container_id=container_id)

    if dry_run:
        log_result(request_id, success=True)
        return {
            "dry_run": True,
            "operation": op_name,
            "would_call": "accounts.containers.workspaces.triggers.create",
            "parent": parent,
            "trigger_preview": _normalise_trigger(trigger),
        }

    success = False
    error_msg: str | None = None
    try:
        response = client.execute(
            config,
            "accounts.containers.workspaces.triggers.create",
            parent=parent,
            body=trigger,
        )
        if "error" in response:
            error_msg = response.get("error", "unknown")
            return response
        success = True
        return {"dry_run": False, "operation": op_name, "trigger": _normalise_trigger(response)}
    finally:
        log_result(request_id, success=success, error=error_msg)


def update_trigger(
    config: GtmMcpConfig,
    *,
    account_id: str,
    container_id: str,
    workspace_id: str,
    trigger_id: str,
    trigger: dict[str, Any],
    dry_run: bool = True,
) -> dict[str, Any]:
    """Update an existing GTM trigger in a workspace (Gate 2, guarded)."""
    op_name = "update_trigger"
    guard_error = check_write_safety(
        config,
        container_id=container_id,
        operation=op_name,
        dry_run=dry_run,
    )
    if guard_error is not None:
        return guard_error

    path = _trigger_path(account_id, container_id, workspace_id, trigger_id)
    request_id = log_attempt(op_name, dry_run=dry_run, container_id=container_id)

    if dry_run:
        log_result(request_id, success=True)
        return {
            "dry_run": True,
            "operation": op_name,
            "would_call": "accounts.containers.workspaces.triggers.update",
            "path": path,
            "trigger_preview": _normalise_trigger(trigger),
        }

    success = False
    error_msg: str | None = None
    try:
        response = client.execute(
            config,
            "accounts.containers.workspaces.triggers.update",
            path=path,
            body=trigger,
        )
        if "error" in response:
            error_msg = response.get("error", "unknown")
            return response
        success = True
        return {"dry_run": False, "operation": op_name, "trigger": _normalise_trigger(response)}
    finally:
        log_result(request_id, success=success, error=error_msg)


def delete_trigger(
    config: GtmMcpConfig,
    *,
    account_id: str,
    container_id: str,
    workspace_id: str,
    trigger_id: str,
    dry_run: bool = True,
    confirm_destructive: bool = False,
) -> dict[str, Any]:
    """Delete a GTM trigger from a workspace (Gate 2, guarded)."""
    op_name = "delete_trigger"
    guard_error = check_write_safety(
        config,
        container_id=container_id,
        operation=op_name,
        dry_run=dry_run,
    )
    if guard_error is not None:
        return guard_error

    if not dry_run:
        destructive_error = check_destructive(confirm_destructive)
        if destructive_error is not None:
            return destructive_error

    path = _trigger_path(account_id, container_id, workspace_id, trigger_id)
    request_id = log_attempt(op_name, dry_run=dry_run, container_id=container_id)

    if dry_run:
        log_result(request_id, success=True)
        return {
            "dry_run": True,
            "operation": op_name,
            "would_call": "accounts.containers.workspaces.triggers.delete",
            "path": path,
        }

    success = False
    error_msg: str | None = None
    try:
        response = client.execute(
            config,
            "accounts.containers.workspaces.triggers.delete",
            path=path,
        )
        if "error" in response:
            error_msg = response.get("error", "unknown")
            return response
        success = True
        return {
            "dry_run": False,
            "operation": op_name,
            "deleted": True,
            "trigger_id": trigger_id,
            "api_response": response,
        }
    finally:
        log_result(request_id, success=success, error=error_msg)
