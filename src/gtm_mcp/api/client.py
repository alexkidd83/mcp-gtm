"""GTM API v2 client — thin wrapper around googleapiclient."""

from __future__ import annotations

from typing import Any

from googleapiclient.discovery import build

from gtm_mcp.api.errors import translate_api_error
from gtm_mcp.auth import get_credentials
from gtm_mcp.config import GtmMcpConfig

# Lazy singleton — initialized on first call.
_service: Any = None
_config: GtmMcpConfig | None = None


def _get_service(config: GtmMcpConfig) -> Any:
    """Return the GTM API v2 service, creating it on first call."""
    global _service, _config  # noqa: PLW0603
    if _service is None or _config is not config:
        creds = get_credentials(config)
        _service = build("tagmanager", "v2", credentials=creds)
        _config = config
    return _service


def execute(config: GtmMcpConfig, method_chain: str, **kwargs: Any) -> Any:
    """Execute a GTM API call and return the response.

    ``method_chain`` is a dot-separated path like ``accounts.list``
    or ``accounts.containers.workspaces.tags.list``.

    Example::

        execute(config, "accounts.list")
        execute(config, "accounts.containers.list", parent="accounts/123")
    """
    service = _get_service(config)

    # Walk the method chain: "accounts.containers.list" -> service.accounts().containers().list()
    obj = service
    parts = method_chain.split(".")
    for part in parts[:-1]:
        obj = getattr(obj, part)()
    method = getattr(obj, parts[-1])

    try:
        return method(**kwargs).execute()
    except Exception as exc:
        return translate_api_error(exc)
