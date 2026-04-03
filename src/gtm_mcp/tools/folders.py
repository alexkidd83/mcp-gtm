"""GTM Folder tools."""

from __future__ import annotations

from typing import Any

from gtm_mcp.api import client
from gtm_mcp.config import GtmMcpConfig


def list_folders(
    config: GtmMcpConfig,
    *,
    account_id: str,
    container_id: str,
    workspace_id: str,
) -> dict[str, Any]:
    """List all organizational folders in a GTM workspace."""
    parent = (
        f"accounts/{account_id}/containers/{container_id}/workspaces/{workspace_id}"
    )
    response = client.execute(
        config, "accounts.containers.workspaces.folders.list", parent=parent
    )
    if "error" in response:
        return response

    folders = response.get("folder", [])
    return {
        "folders": [
            {
                "folder_id": f.get("folderId", ""),
                "name": f.get("name", ""),
                "notes": f.get("notes", ""),
            }
            for f in folders
        ],
        "total": len(folders),
    }


def get_folder_entities(
    config: GtmMcpConfig,
    *,
    account_id: str,
    container_id: str,
    workspace_id: str,
    folder_id: str,
) -> dict[str, Any]:
    """Get all tags, triggers, and variables inside a folder."""
    path = (
        f"accounts/{account_id}/containers/{container_id}"
        f"/workspaces/{workspace_id}/folders/{folder_id}"
    )
    response = client.execute(
        config, "accounts.containers.workspaces.folders.entities", path=path
    )
    if "error" in response:
        return response

    return {
        "tags": [t.get("name", "") for t in response.get("tag", [])],
        "triggers": [t.get("name", "") for t in response.get("trigger", [])],
        "variables": [v.get("name", "") for v in response.get("variable", [])],
    }
