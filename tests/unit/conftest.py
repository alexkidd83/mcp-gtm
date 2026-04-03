"""Shared fixtures for unit tests — mocked API, no credentials needed."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from gtm_mcp.config import GtmMcpConfig
from gtm_mcp.safety import audit as _audit_module


@pytest.fixture()
def config() -> GtmMcpConfig:
    """Return a default GtmMcpConfig (all defaults, no file)."""
    return GtmMcpConfig()


@pytest.fixture()
def mock_execute():
    """Patch gtm_mcp.api.client.execute so tool functions use the mock.

    Since tool modules import `from gtm_mcp.api import client` and call
    `client.execute(...)`, patching the function on the module object works.
    """
    with patch("gtm_mcp.api.client.execute") as m:
        yield m


@pytest.fixture(autouse=True)
def _audit_tmp_path(tmp_path):
    """Redirect audit log to a temp directory so tests never write to ~/.gtm-mcp/."""
    original = _audit_module._AUDIT_PATH
    _audit_module._AUDIT_PATH = tmp_path / "audit.jsonl"
    yield
    _audit_module._AUDIT_PATH = original
