"""Unit tests for gate-based auth scope selection and token migration."""

from __future__ import annotations

import json

import pytest

from gtm_mcp.auth import (
    SCOPES_EDIT,
    SCOPES_PUBLISH,
    SCOPES_READONLY,
    _requested_scopes_from_env,
    _token_has_required_scopes,
    get_credentials,
)


def test_requested_scopes_default_gate1(monkeypatch):
    monkeypatch.delenv("GTM_MCP_GATE", raising=False)
    assert _requested_scopes_from_env() == SCOPES_READONLY


def test_requested_scopes_gate2(monkeypatch):
    monkeypatch.setenv("GTM_MCP_GATE", "2")
    assert _requested_scopes_from_env() == SCOPES_EDIT


def test_requested_scopes_gate3(monkeypatch):
    monkeypatch.setenv("GTM_MCP_GATE", "publish")
    assert _requested_scopes_from_env() == SCOPES_PUBLISH


def test_requested_scopes_invalid(monkeypatch):
    monkeypatch.setenv("GTM_MCP_GATE", "banana")
    with pytest.raises(ValueError, match="Invalid GTM_MCP_GATE"):
        _requested_scopes_from_env()


def test_token_has_required_scopes(tmp_path):
    token_path = tmp_path / "token.json"
    token_path.write_text(json.dumps({"scopes": SCOPES_READONLY}))
    assert _token_has_required_scopes(token_path, SCOPES_READONLY) is True
    assert _token_has_required_scopes(token_path, SCOPES_EDIT) is False


def test_get_credentials_archives_incompatible_token_and_reauths(monkeypatch, config, tmp_path):
    token_path = tmp_path / "token.json"
    creds_path = tmp_path / "credentials.json"
    config.google.token_path = str(token_path)
    config.google.credentials_path = str(creds_path)

    token_path.write_text(json.dumps({"scopes": SCOPES_READONLY}))
    creds_path.write_text(json.dumps({"installed": {}}))
    monkeypatch.setenv("GTM_MCP_GATE", "2")

    class DummyCreds:
        valid = True
        expired = False
        refresh_token = None

        def to_json(self):
            return json.dumps({"scopes": SCOPES_EDIT})

    class DummyFlow:
        def run_local_server(self, port: int = 0):  # noqa: ARG002
            return DummyCreds()

    monkeypatch.setattr(
        "gtm_mcp.auth.InstalledAppFlow.from_client_secrets_file",
        lambda _path, _scopes: DummyFlow(),
    )

    creds = get_credentials(config)
    assert isinstance(creds, DummyCreds)
    assert token_path.exists()
    backups = list(tmp_path.glob("token.json.bak.*"))
    assert len(backups) == 1
