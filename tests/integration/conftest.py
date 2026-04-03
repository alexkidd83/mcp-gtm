"""Integration test fixtures — skip if GTM credentials are not configured."""

from __future__ import annotations

from pathlib import Path

import pytest

from gtm_mcp.config import GtmMcpConfig, load_config


def _credentials_available() -> bool:
    """Check if GTM MCP credentials are configured."""
    config = load_config()
    token_path = Path(config.google.token_path).expanduser()
    creds_path = Path(config.google.credentials_path).expanduser()
    return token_path.exists() or creds_path.exists()


pytestmark = pytest.mark.integration

skip_no_creds = pytest.mark.skipif(
    not _credentials_available(),
    reason="GTM credentials not configured at ~/.gtm-mcp/",
)


@pytest.fixture
def config() -> GtmMcpConfig:
    """Load real config for integration tests."""
    return load_config()
