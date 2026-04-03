"""GTM Tag tools."""

from __future__ import annotations

from typing import Any

from gtm_mcp.api import client
from gtm_mcp.config import GtmMcpConfig
from gtm_mcp.safety.audit import log_attempt, log_result
from gtm_mcp.safety.guards import check_destructive, check_write_safety


def _workspace_parent(account_id: str, container_id: str, workspace_id: str) -> str:
    return f"accounts/{account_id}/containers/{container_id}/workspaces/{workspace_id}"


def _tag_path(account_id: str, container_id: str, workspace_id: str, tag_id: str) -> str:
    return f"{_workspace_parent(account_id, container_id, workspace_id)}/tags/{tag_id}"


def _normalise_tag(tag: dict[str, Any]) -> dict[str, Any]:
    return {
        "tag_id": tag.get("tagId", ""),
        "name": tag.get("name", ""),
        "type": tag.get("type", ""),
        "parameter": tag.get("parameter", []),
        "firing_trigger_id": tag.get("firingTriggerId", []),
        "blocking_trigger_id": tag.get("blockingTriggerId", []),
        "tag_firing_option": tag.get("tagFiringOption", ""),
        "paused": tag.get("paused", False),
        "notes": tag.get("notes", ""),
        "setup_tag": tag.get("setupTag", []),
        "teardown_tag": tag.get("teardownTag", []),
        "fingerprint": tag.get("fingerprint", ""),
    }


def list_tags(
    config: GtmMcpConfig,
    *,
    account_id: str,
    container_id: str,
    workspace_id: str,
) -> dict[str, Any]:
    """List all tags in a GTM workspace."""
    parent = _workspace_parent(account_id, container_id, workspace_id)
    response = client.execute(config, "accounts.containers.workspaces.tags.list", parent=parent)
    if "error" in response:
        return response

    tags = response.get("tag", [])
    return {
        "tags": [
            {
                "tag_id": t.get("tagId", ""),
                "name": t.get("name", ""),
                "type": t.get("type", ""),
                "firing_trigger_id": t.get("firingTriggerId", []),
                "blocking_trigger_id": t.get("blockingTriggerId", []),
                "paused": t.get("paused", False),
            }
            for t in tags
        ],
        "total": len(tags),
    }


def get_tag(
    config: GtmMcpConfig,
    *,
    account_id: str,
    container_id: str,
    workspace_id: str,
    tag_id: str,
) -> dict[str, Any]:
    """Get full details for a single tag, including parameters."""
    path = _tag_path(account_id, container_id, workspace_id, tag_id)
    response = client.execute(config, "accounts.containers.workspaces.tags.get", path=path)
    if "error" in response:
        return response

    return _normalise_tag(response)


def create_tag(
    config: GtmMcpConfig,
    *,
    account_id: str,
    container_id: str,
    workspace_id: str,
    tag: dict[str, Any],
    dry_run: bool = True,
) -> dict[str, Any]:
    """Create a tag in a GTM workspace (Gate 2, guarded)."""
    op_name = "create_tag"
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
            "would_call": "accounts.containers.workspaces.tags.create",
            "parent": parent,
            "tag_preview": _normalise_tag(tag),
        }

    success = False
    error_msg: str | None = None
    try:
        response = client.execute(
            config,
            "accounts.containers.workspaces.tags.create",
            parent=parent,
            body=tag,
        )
        if "error" in response:
            error_msg = response.get("error", "unknown")
            return response
        success = True
        return {"dry_run": False, "operation": op_name, "tag": _normalise_tag(response)}
    finally:
        log_result(request_id, success=success, error=error_msg)


def update_tag(
    config: GtmMcpConfig,
    *,
    account_id: str,
    container_id: str,
    workspace_id: str,
    tag_id: str,
    tag: dict[str, Any],
    dry_run: bool = True,
) -> dict[str, Any]:
    """Update an existing GTM tag in a workspace (Gate 2, guarded)."""
    op_name = "update_tag"
    guard_error = check_write_safety(
        config,
        container_id=container_id,
        operation=op_name,
        dry_run=dry_run,
    )
    if guard_error is not None:
        return guard_error

    path = _tag_path(account_id, container_id, workspace_id, tag_id)
    request_id = log_attempt(op_name, dry_run=dry_run, container_id=container_id)

    if dry_run:
        log_result(request_id, success=True)
        return {
            "dry_run": True,
            "operation": op_name,
            "would_call": "accounts.containers.workspaces.tags.update",
            "path": path,
            "tag_preview": _normalise_tag(tag),
        }

    success = False
    error_msg: str | None = None
    try:
        response = client.execute(
            config,
            "accounts.containers.workspaces.tags.update",
            path=path,
            body=tag,
        )
        if "error" in response:
            error_msg = response.get("error", "unknown")
            return response
        success = True
        return {"dry_run": False, "operation": op_name, "tag": _normalise_tag(response)}
    finally:
        log_result(request_id, success=success, error=error_msg)


def delete_tag(
    config: GtmMcpConfig,
    *,
    account_id: str,
    container_id: str,
    workspace_id: str,
    tag_id: str,
    dry_run: bool = True,
    confirm_destructive: bool = False,
) -> dict[str, Any]:
    """Delete a GTM tag from a workspace (Gate 2, guarded)."""
    op_name = "delete_tag"
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

    path = _tag_path(account_id, container_id, workspace_id, tag_id)
    request_id = log_attempt(op_name, dry_run=dry_run, container_id=container_id)

    if dry_run:
        log_result(request_id, success=True)
        return {
            "dry_run": True,
            "operation": op_name,
            "would_call": "accounts.containers.workspaces.tags.delete",
            "path": path,
        }

    success = False
    error_msg: str | None = None
    try:
        response = client.execute(
            config,
            "accounts.containers.workspaces.tags.delete",
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
            "tag_id": tag_id,
            "api_response": response,
        }
    finally:
        log_result(request_id, success=success, error=error_msg)
