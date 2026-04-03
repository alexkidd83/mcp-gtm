"""GTM Version tools."""

from __future__ import annotations

from typing import Any

from gtm_mcp.api import client
from gtm_mcp.config import GtmMcpConfig


def list_versions(
    config: GtmMcpConfig,
    *,
    account_id: str,
    container_id: str,
) -> dict[str, Any]:
    """List all published versions for a GTM container."""
    parent = f"accounts/{account_id}/containers/{container_id}"
    response = client.execute(
        config, "accounts.containers.version_headers.list", parent=parent
    )
    if "error" in response:
        return response

    headers = response.get("containerVersionHeader", [])
    return {
        "versions": [
            {
                "version_id": h.get("containerVersionId", ""),
                "name": h.get("name", ""),
                "description": h.get("description", ""),
                "deleted": h.get("deleted", False),
                "num_tags": h.get("numTags", "0"),
                "num_triggers": h.get("numTriggers", "0"),
                "num_variables": h.get("numVariables", "0"),
            }
            for h in headers
        ],
        "total": len(headers),
    }
