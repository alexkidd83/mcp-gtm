"""GTM Template tools."""

from __future__ import annotations

from typing import Any

from gtm_mcp.api import client
from gtm_mcp.config import GtmMcpConfig


def list_templates(
    config: GtmMcpConfig,
    *,
    account_id: str,
    container_id: str,
    workspace_id: str,
) -> dict[str, Any]:
    """List all custom templates in a GTM workspace."""
    parent = (
        f"accounts/{account_id}/containers/{container_id}/workspaces/{workspace_id}"
    )
    response = client.execute(
        config, "accounts.containers.workspaces.templates.list", parent=parent
    )
    if "error" in response:
        return response

    templates = response.get("template", [])
    return {
        "templates": [
            {
                "template_id": t.get("templateId", ""),
                "name": t.get("name", ""),
                "gallery_reference": t.get("galleryReference", {}),
            }
            for t in templates
        ],
        "total": len(templates),
    }


def get_template(
    config: GtmMcpConfig,
    *,
    account_id: str,
    container_id: str,
    workspace_id: str,
    template_id: str,
) -> dict[str, Any]:
    """Get full details for a single custom template."""
    path = (
        f"accounts/{account_id}/containers/{container_id}"
        f"/workspaces/{workspace_id}/templates/{template_id}"
    )
    response = client.execute(
        config, "accounts.containers.workspaces.templates.get", path=path
    )
    if "error" in response:
        return response

    return {
        "template_id": response.get("templateId", ""),
        "name": response.get("name", ""),
        "template_data": response.get("templateData", ""),
        "gallery_reference": response.get("galleryReference", {}),
    }
