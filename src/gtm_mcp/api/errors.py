"""Translate GTM API errors into structured dicts with actionable hints."""

from __future__ import annotations

from typing import Any

from googleapiclient.errors import HttpError


def translate_api_error(exc: Exception) -> dict[str, Any]:
    """Convert an API exception to a structured error dict.

    Returns ``{"error": ..., "hint": ..., "status": ...}`` so the LLM
    can present a useful message instead of a raw traceback.
    """
    if isinstance(exc, HttpError):
        status = exc.resp.status
        reason = exc.reason if hasattr(exc, "reason") else str(exc)

        hints = {
            401: (
                "Authentication failed. Run the OAuth flow again or check that "
                "your token at ~/.gtm-mcp/token.json is still valid."
            ),
            403: (
                "Permission denied. Ensure your Google account has access to "
                "this GTM container and the correct OAuth scopes are granted."
            ),
            404: "Resource not found. Check the account, container, and workspace IDs.",
            429: "Rate limit exceeded. Wait a moment and try again.",
        }

        return {
            "error": reason,
            "status": status,
            "hint": hints.get(status, "Unexpected API error. Check the error message above."),
        }

    return {
        "error": str(exc),
        "hint": "Unexpected error. This may be a network issue or a bug.",
    }
