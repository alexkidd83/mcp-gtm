"""GTM Workspace tools."""

from __future__ import annotations

from typing import Any

from gtm_mcp.api import client
from gtm_mcp.config import GtmMcpConfig
from gtm_mcp.safety.guards import check_write_safety

try:
    from gtm_mcp.safety.audit import log_attempt, log_result
except ImportError:  # pragma: no cover

    def log_attempt(*a: Any, **kw: Any) -> str:  # type: ignore[misc]
        return "no-audit"

    def log_result(*a: Any, **kw: Any) -> None:  # type: ignore[misc]
        pass


def list_workspaces(
    config: GtmMcpConfig, *, account_id: str, container_id: str
) -> dict[str, Any]:
    """List all workspaces in a GTM container."""
    parent = f"accounts/{account_id}/containers/{container_id}"
    response = client.execute(config, "accounts.containers.workspaces.list", parent=parent)
    if "error" in response:
        return response

    workspaces = response.get("workspace", [])
    return {
        "workspaces": [
            {
                "workspace_id": w.get("workspaceId", ""),
                "name": w.get("name", ""),
                "description": w.get("description", ""),
            }
            for w in workspaces
        ],
        "total": len(workspaces),
    }


def get_workspace_status(
    config: GtmMcpConfig, *, account_id: str, container_id: str, workspace_id: str
) -> dict[str, Any]:
    """Get the status of a workspace — pending changes, conflicts, etc."""
    path = (
        f"accounts/{account_id}/containers/{container_id}/workspaces/{workspace_id}"
    )
    response = client.execute(config, "accounts.containers.workspaces.getStatus", path=path)
    if "error" in response:
        return response

    return {
        "workspace_change": response.get("workspaceChange", []),
        "merge_conflict": response.get("mergeConflict", []),
    }


def create_workspace(
    config: GtmMcpConfig,
    *,
    account_id: str,
    container_id: str,
    name: str,
    description: str = "",
    dry_run: bool = True,
) -> dict[str, Any]:
    """Create a new workspace in a GTM container (Gate 2, safety-guarded)."""
    op_name = "create_workspace"
    guard_error = check_write_safety(
        config,
        container_id=container_id,
        operation=op_name,
        dry_run=dry_run,
    )
    if guard_error is not None:
        return guard_error

    parent = f"accounts/{account_id}/containers/{container_id}"
    request_id = log_attempt(op_name, dry_run=dry_run, container_id=container_id)

    if dry_run:
        log_result(request_id, success=True)
        return {
            "dry_run": True,
            "operation": op_name,
            "parent": parent,
            "workspace_preview": {"name": name, "description": description},
        }

    success = False
    error_msg: str | None = None
    try:
        response = client.execute(
            config,
            "accounts.containers.workspaces.create",
            parent=parent,
            body={"name": name, "description": description},
        )
        if "error" in response:
            error_msg = response.get("error", "unknown")
            return response
        success = True
        return {
            "dry_run": False,
            "operation": op_name,
            "workspace": {
                "workspace_id": response.get("workspaceId", ""),
                "name": response.get("name", ""),
                "description": response.get("description", ""),
            },
        }
    finally:
        log_result(request_id, success=success, error=error_msg)
