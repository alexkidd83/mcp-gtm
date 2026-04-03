"""Google OAuth 2.0 authentication for the GTM API v2."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import TYPE_CHECKING

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

if TYPE_CHECKING:
    from gtm_mcp.config import GtmMcpConfig

# Gate 1 scope — read-only. Gates 2-3 add edit and publish scopes.
SCOPES_READONLY = ["https://www.googleapis.com/auth/tagmanager.readonly"]
SCOPES_EDIT = [
    "https://www.googleapis.com/auth/tagmanager.readonly",
    "https://www.googleapis.com/auth/tagmanager.edit.containers",
]
SCOPES_PUBLISH = [
    "https://www.googleapis.com/auth/tagmanager.readonly",
    "https://www.googleapis.com/auth/tagmanager.edit.containers",
    "https://www.googleapis.com/auth/tagmanager.publish",
]


def _requested_scopes_from_env() -> list[str]:
    """Return OAuth scopes for the configured gate level.

    Gate is selected via ``GTM_MCP_GATE``:
    - Gate 1: ``1`` / ``gate1`` / ``readonly`` (default)
    - Gate 2: ``2`` / ``gate2`` / ``edit``
    - Gate 3: ``3`` / ``gate3`` / ``publish``
    """
    gate = os.environ.get("GTM_MCP_GATE", "1").strip().lower()
    if gate in {"1", "gate1", "readonly", "read"}:
        return SCOPES_READONLY
    if gate in {"2", "gate2", "edit"}:
        return SCOPES_EDIT
    if gate in {"3", "gate3", "publish"}:
        return SCOPES_PUBLISH
    raise ValueError(
        "Invalid GTM_MCP_GATE value. Use one of: 1|gate1|readonly, "
        "2|gate2|edit, 3|gate3|publish."
    )


def _read_scopes_from_token_file(token_path: Path) -> set[str]:
    """Read granted scopes from a token file when available."""
    try:
        raw = json.loads(token_path.read_text())
    except Exception:
        return set()

    scopes = raw.get("scopes", [])
    if isinstance(scopes, str):
        return set(scopes.split())
    if isinstance(scopes, list):
        return {str(s) for s in scopes}
    return set()


def _token_has_required_scopes(token_path: Path, required_scopes: list[str]) -> bool:
    """Return whether a token file includes all required scopes."""
    granted = _read_scopes_from_token_file(token_path)
    if not granted:
        return False
    return set(required_scopes).issubset(granted)


def _archive_incompatible_token(token_path: Path) -> Path:
    """Move incompatible token to a timestamped backup path."""
    backup_path = token_path.with_name(
        f"{token_path.name}.bak.{int(time.time())}"
    )
    token_path.rename(backup_path)
    return backup_path


def get_credentials(config: GtmMcpConfig) -> Credentials:
    """Load or create OAuth credentials for the GTM API.

    If a valid token exists at ``config.google.token_path``, it is loaded
    and refreshed if expired. Otherwise, the OAuth consent flow runs using
    the client secrets at ``config.google.credentials_path``.
    """
    token_path = Path(config.google.token_path).expanduser()
    creds_path = Path(config.google.credentials_path).expanduser()
    requested_scopes = _requested_scopes_from_env()

    creds: Credentials | None = None

    if token_path.exists():
        if not _token_has_required_scopes(token_path, requested_scopes):
            # Explicit token migration behavior: preserve old token and force reauth
            # when scope set changes between gates.
            _archive_incompatible_token(token_path)
        else:
            creds = Credentials.from_authorized_user_file(
                str(token_path), requested_scopes
            )

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            _save_token(creds, token_path)
            return creds
        except Exception as exc:
            token_path.unlink(missing_ok=True)
            raise RuntimeError(
                "OAuth token refresh failed. Token was cleared; re-authentication "
                "is required."
            ) from exc

    if not creds_path.exists():
        raise FileNotFoundError(
            f"OAuth client secrets not found at {creds_path}. "
            "Download from console.cloud.google.com > APIs & Services > Credentials."
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), requested_scopes)
    creds = flow.run_local_server(port=0)
    _save_token(creds, token_path)
    return creds


def _save_token(creds: Credentials, token_path: Path) -> None:
    """Persist the OAuth token to disk."""
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(creds.to_json())
