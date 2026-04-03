"""Shared fixtures for GTM MCP tests."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from gtm_mcp.config import GtmMcpConfig


@pytest.fixture()
def config() -> GtmMcpConfig:
    """Return a default GtmMcpConfig (all defaults, no file)."""
    return GtmMcpConfig()


@pytest.fixture()
def mock_execute():
    """Patch gtm_mcp.api.client.execute and yield the mock.

    All tool modules import ``client`` (the module) and call ``client.execute()``,
    so patching the function on the module object intercepts every call.
    """
    with patch("gtm_mcp.api.client.execute") as m:
        yield m
