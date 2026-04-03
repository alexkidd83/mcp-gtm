"""GTM Container tools."""

from __future__ import annotations

from typing import Any

from gtm_mcp.api import client
from gtm_mcp.config import GtmMcpConfig


def list_containers(config: GtmMcpConfig, *, account_id: str) -> dict[str, Any]:
    """List all containers in a GTM account."""
    parent = f"accounts/{account_id}"
    response = client.execute(config, "accounts.containers.list", parent=parent)
    if "error" in response:
        return response

    containers = response.get("container", [])
    return {
        "containers": [
            {
                "container_id": c.get("containerId", ""),
                "name": c.get("name", ""),
                "public_id": c.get("publicId", ""),
                "usage_context": c.get("usageContext", []),
                "domain_name": c.get("domainName", []),
                "notes": c.get("notes", ""),
            }
            for c in containers
        ],
        "total": len(containers),
    }


def get_container(config: GtmMcpConfig, *, account_id: str, container_id: str) -> dict[str, Any]:
    """Get details for a single GTM container."""
    path = f"accounts/{account_id}/containers/{container_id}"
    response = client.execute(config, "accounts.containers.get", path=path)
    if "error" in response:
        return response

    return {
        "container_id": response.get("containerId", ""),
        "name": response.get("name", ""),
        "public_id": response.get("publicId", ""),
        "usage_context": response.get("usageContext", []),
        "domain_name": response.get("domainName", []),
        "notes": response.get("notes", ""),
        "tag_manager_url": response.get("tagManagerUrl", ""),
    }
