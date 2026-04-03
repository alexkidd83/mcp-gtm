"""Startup/import smoke tests for gtm_mcp."""

from __future__ import annotations

import importlib
import sys


def test_server_module_imports_without_errors(monkeypatch, tmp_path):
    """Importing gtm_mcp.server should work in the test runtime."""
    # Avoid reading any user-local config while importing module globals.
    monkeypatch.setenv("GTM_MCP_CONFIG", str(tmp_path / "missing-config.yaml"))

    # Force a fresh import path so startup-level import errors are surfaced.
    sys.modules.pop("gtm_mcp.server", None)

    module = importlib.import_module("gtm_mcp.server")
    assert module.mcp is not None


def test_server_registers_initial_gate2_tag_tools(monkeypatch, tmp_path):
    """Gate 2 bootstrap tools should be importable from server module."""
    monkeypatch.setenv("GTM_MCP_CONFIG", str(tmp_path / "missing-config.yaml"))
    sys.modules.pop("gtm_mcp.server", None)
    module = importlib.import_module("gtm_mcp.server")
    assert callable(module.create_tag)
    assert callable(module.update_tag)
    assert callable(module.delete_tag)
