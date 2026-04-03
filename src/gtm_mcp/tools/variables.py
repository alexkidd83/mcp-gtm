"""GTM Variable tools."""

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


def _variable_path(
    account_id: str, container_id: str, workspace_id: str, variable_id: str
) -> str:
    return f"{_workspace_parent(account_id, container_id, workspace_id)}/variables/{variable_id}"


def _normalise_variable(variable: dict[str, Any]) -> dict[str, Any]:
    return {
        "variable_id": variable.get("variableId", ""),
        "name": variable.get("name", ""),
        "type": variable.get("type", ""),
        "parameter": variable.get("parameter", []),
        "format_value": variable.get("formatValue", {}),
        "notes": variable.get("notes", ""),
        "fingerprint": variable.get("fingerprint", ""),
    }


def list_variables(
    config: GtmMcpConfig,
    *,
    account_id: str,
    container_id: str,
    workspace_id: str,
) -> dict[str, Any]:
    """List all user-defined variables in a GTM workspace."""
    parent = _workspace_parent(account_id, container_id, workspace_id)
    response = client.execute(
        config, "accounts.containers.workspaces.variables.list", parent=parent
    )
    if "error" in response:
        return response

    variables = response.get("variable", [])
    return {
        "variables": [
            {
                "variable_id": v.get("variableId", ""),
                "name": v.get("name", ""),
                "type": v.get("type", ""),
            }
            for v in variables
        ],
        "total": len(variables),
    }


def get_variable(
    config: GtmMcpConfig,
    *,
    account_id: str,
    container_id: str,
    workspace_id: str,
    variable_id: str,
) -> dict[str, Any]:
    """Get full details for a single variable, including parameters."""
    path = _variable_path(account_id, container_id, workspace_id, variable_id)
    response = client.execute(
        config, "accounts.containers.workspaces.variables.get", path=path
    )
    if "error" in response:
        return response

    return {
        "variable_id": response.get("variableId", ""),
        "name": response.get("name", ""),
        "type": response.get("type", ""),
        "parameter": response.get("parameter", []),
        "format_value": response.get("formatValue", {}),
        "notes": response.get("notes", ""),
    }


def create_variable(
    config: GtmMcpConfig,
    *,
    account_id: str,
    container_id: str,
    workspace_id: str,
    variable: dict[str, Any],
    dry_run: bool = True,
) -> dict[str, Any]:
    """Create a variable in a GTM workspace (Gate 2, guarded)."""
    op_name = "create_variable"
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
            "would_call": "accounts.containers.workspaces.variables.create",
            "parent": parent,
            "variable_preview": _normalise_variable(variable),
        }

    success = False
    error_msg: str | None = None
    try:
        response = client.execute(
            config,
            "accounts.containers.workspaces.variables.create",
            parent=parent,
            body=variable,
        )
        if "error" in response:
            error_msg = response.get("error", "unknown")
            return response
        success = True
        return {"dry_run": False, "operation": op_name, "variable": _normalise_variable(response)}
    finally:
        log_result(request_id, success=success, error=error_msg)


def update_variable(
    config: GtmMcpConfig,
    *,
    account_id: str,
    container_id: str,
    workspace_id: str,
    variable_id: str,
    variable: dict[str, Any],
    dry_run: bool = True,
) -> dict[str, Any]:
    """Update an existing GTM variable in a workspace (Gate 2, guarded)."""
    op_name = "update_variable"
    guard_error = check_write_safety(
        config,
        container_id=container_id,
        operation=op_name,
        dry_run=dry_run,
    )
    if guard_error is not None:
        return guard_error

    path = _variable_path(account_id, container_id, workspace_id, variable_id)
    request_id = log_attempt(op_name, dry_run=dry_run, container_id=container_id)

    if dry_run:
        log_result(request_id, success=True)
        return {
            "dry_run": True,
            "operation": op_name,
            "would_call": "accounts.containers.workspaces.variables.update",
            "path": path,
            "variable_preview": _normalise_variable(variable),
        }

    success = False
    error_msg: str | None = None
    try:
        response = client.execute(
            config,
            "accounts.containers.workspaces.variables.update",
            path=path,
            body=variable,
        )
        if "error" in response:
            error_msg = response.get("error", "unknown")
            return response
        success = True
        return {"dry_run": False, "operation": op_name, "variable": _normalise_variable(response)}
    finally:
        log_result(request_id, success=success, error=error_msg)


def delete_variable(
    config: GtmMcpConfig,
    *,
    account_id: str,
    container_id: str,
    workspace_id: str,
    variable_id: str,
    dry_run: bool = True,
    confirm_destructive: bool = False,
) -> dict[str, Any]:
    """Delete a GTM variable from a workspace (Gate 2, guarded)."""
    op_name = "delete_variable"
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

    path = _variable_path(account_id, container_id, workspace_id, variable_id)
    request_id = log_attempt(op_name, dry_run=dry_run, container_id=container_id)

    if dry_run:
        log_result(request_id, success=True)
        return {
            "dry_run": True,
            "operation": op_name,
            "would_call": "accounts.containers.workspaces.variables.delete",
            "path": path,
        }

    success = False
    error_msg: str | None = None
    try:
        response = client.execute(
            config,
            "accounts.containers.workspaces.variables.delete",
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
            "variable_id": variable_id,
            "api_response": response,
        }
    finally:
        log_result(request_id, success=success, error=error_msg)
