"""Load and validate GTM MCP configuration from ~/.gtm-mcp/config.yaml."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class GoogleConfig:
    credentials_path: str = "~/.gtm-mcp/credentials.json"
    token_path: str = "~/.gtm-mcp/token.json"


@dataclass
class SafetyConfig:
    allowed_container_ids: list[str] = field(default_factory=list)
    blocked_operations: list[str] = field(default_factory=list)
    require_dry_run: bool = True


@dataclass
class DefaultsConfig:
    account_id: str = ""
    container_id: str = ""


@dataclass
class GtmMcpConfig:
    google: GoogleConfig = field(default_factory=GoogleConfig)
    safety: SafetyConfig = field(default_factory=SafetyConfig)
    defaults: DefaultsConfig = field(default_factory=DefaultsConfig)


def _resolve_path(path_str: str) -> Path:
    """Expand ~ and env vars in a path string."""
    return Path(os.path.expandvars(os.path.expanduser(path_str)))


def load_config(config_path: str | None = None) -> GtmMcpConfig:
    """Load configuration from YAML file.

    Resolution order:
    1. Explicit ``config_path`` argument
    2. ``GTM_MCP_CONFIG`` environment variable
    3. ``~/.gtm-mcp/config.yaml`` default
    """
    if config_path is None:
        config_path = os.environ.get("GTM_MCP_CONFIG", "~/.gtm-mcp/config.yaml")

    path = _resolve_path(config_path)

    if not path.exists():
        return GtmMcpConfig()

    with open(path) as f:
        raw = yaml.safe_load(f) or {}

    google_raw = raw.get("google", {})
    safety_raw = raw.get("safety", {})
    defaults_raw = raw.get("defaults", {})

    return GtmMcpConfig(
        google=GoogleConfig(
            credentials_path=google_raw.get("credentials_path", "~/.gtm-mcp/credentials.json"),
            token_path=google_raw.get("token_path", "~/.gtm-mcp/token.json"),
        ),
        safety=SafetyConfig(
            allowed_container_ids=safety_raw.get("allowed_container_ids", []),
            blocked_operations=safety_raw.get("blocked_operations", []),
            require_dry_run=safety_raw.get("require_dry_run", True),
        ),
        defaults=DefaultsConfig(
            account_id=defaults_raw.get("account_id", ""),
            container_id=defaults_raw.get("container_id", ""),
        ),
    )
