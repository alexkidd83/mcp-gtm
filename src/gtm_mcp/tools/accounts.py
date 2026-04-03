"""GTM Account tools."""

from __future__ import annotations

from typing import Any

from gtm_mcp.api import client
from gtm_mcp.config import GtmMcpConfig


def list_accounts(config: GtmMcpConfig) -> dict[str, Any]:
    """List all GTM accounts accessible to the authenticated user."""
    response = client.execute(config, "accounts.list")
    if "error" in response:
        return response

    accounts = response.get("account", [])
    return {
        "accounts": [
            {
                "account_id": a.get("accountId", ""),
                "name": a.get("name", ""),
                "share_data": a.get("shareData", False),
                "fingerprint": a.get("fingerprint", ""),
            }
            for a in accounts
        ],
        "total": len(accounts),
    }
