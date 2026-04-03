"""GTM Built-In Variable tools."""

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


def list_built_in_variables(
    config: GtmMcpConfig,
    *,
    account_id: str,
    container_id: str,
    workspace_id: str,
) -> dict[str, Any]:
    """List all enabled built-in variables in a GTM workspace."""
    parent = (
        f"accounts/{account_id}/containers/{container_id}/workspaces/{workspace_id}"
    )
    response = client.execute(
        config,
        "accounts.containers.workspaces.built_in_variables.list",
        parent=parent,
    )
    if "error" in response:
        return response

    variables = response.get("builtInVariable", [])
    return {
        "built_in_variables": [
            {
                "name": v.get("name", ""),
                "type": v.get("type", ""),
            }
            for v in variables
        ],
        "total": len(variables),
    }


def enable_built_in_variables(
    config: GtmMcpConfig,
    *,
    account_id: str,
    container_id: str,
    workspace_id: str,
    variable_types: list[str],
    dry_run: bool = True,
) -> dict[str, Any]:
    """Enable built-in variables in a GTM workspace (Gate 2, safety-guarded)."""
    op_name = "enable_built_in_variables"
    guard_error = check_write_safety(
        config,
        container_id=container_id,
        operation=op_name,
        dry_run=dry_run,
    )
    if guard_error is not None:
        return guard_error

    parent = (
        f"accounts/{account_id}/containers/{container_id}/workspaces/{workspace_id}"
    )
    request_id = log_attempt(op_name, dry_run=dry_run, container_id=container_id)

    if dry_run:
        log_result(request_id, success=True)
        return {
            "dry_run": True,
            "operation": op_name,
            "would_enable": variable_types,
            "parent": parent,
        }

    success = False
    error_msg: str | None = None
    try:
        response = client.execute(
            config,
            "accounts.containers.workspaces.built_in_variables.create",
            parent=parent,
            type=variable_types,
        )
        if "error" in response:
            error_msg = response.get("error", "unknown")
            return response
        success = True
        enabled = response.get("builtInVariable", [])
        return {
            "dry_run": False,
            "operation": op_name,
            "enabled": [v.get("type", "") for v in enabled],
        }
    finally:
        log_result(request_id, success=success, error=error_msg)


def disable_built_in_variables(
    config: GtmMcpConfig,
    *,
    account_id: str,
    container_id: str,
    workspace_id: str,
    variable_types: list[str],
    dry_run: bool = True,
    confirm_destructive: bool = False,
) -> dict[str, Any]:
    """Disable built-in variables in a GTM workspace (Gate 2, safety-guarded)."""
    op_name = "disable_built_in_variables"
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

    parent = (
        f"accounts/{account_id}/containers/{container_id}/workspaces/{workspace_id}"
    )
    request_id = log_attempt(op_name, dry_run=dry_run, container_id=container_id)

    if dry_run:
        log_result(request_id, success=True)
        return {
            "dry_run": True,
            "operation": op_name,
            "would_disable": variable_types,
            "parent": parent,
        }

    success = False
    error_msg: str | None = None
    try:
        response = client.execute(
            config,
            "accounts.containers.workspaces.built_in_variables.delete",
            parent=parent,
            type=variable_types,
        )
        if "error" in response:
            error_msg = response.get("error", "unknown")
            return response
        success = True
        return {
            "dry_run": False,
            "operation": op_name,
            "disabled": variable_types,
            "api_response": response,
        }
    finally:
        log_result(request_id, success=success, error=error_msg)
