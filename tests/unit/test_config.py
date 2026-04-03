"""Tests for gtm_mcp.config — loading, defaults, YAML parsing."""

from __future__ import annotations

import textwrap

from gtm_mcp.config import (
    DefaultsConfig,
    GoogleConfig,
    GtmMcpConfig,
    SafetyConfig,
    load_config,
)


def test_defaults_when_no_file(tmp_path):
    """load_config returns all defaults when the file does not exist."""
    cfg = load_config(str(tmp_path / "nonexistent.yaml"))
    assert cfg == GtmMcpConfig()
    assert cfg.google.credentials_path == "~/.gtm-mcp/credentials.json"
    assert cfg.safety.require_dry_run is True
    assert cfg.defaults.account_id == ""


def test_load_from_yaml(tmp_path):
    """load_config parses a well-formed YAML file."""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(
        textwrap.dedent("""\
            google:
              credentials_path: /custom/creds.json
              token_path: /custom/token.json
            safety:
              allowed_container_ids:
                - "GTM-ABC"
              blocked_operations:
                - delete_tag
              require_dry_run: false
            defaults:
              account_id: "123"
              container_id: "456"
        """)
    )
    cfg = load_config(str(yaml_file))
    assert cfg.google.credentials_path == "/custom/creds.json"
    assert cfg.google.token_path == "/custom/token.json"
    assert cfg.safety.allowed_container_ids == ["GTM-ABC"]
    assert cfg.safety.blocked_operations == ["delete_tag"]
    assert cfg.safety.require_dry_run is False
    assert cfg.defaults.account_id == "123"
    assert cfg.defaults.container_id == "456"


def test_missing_sections_use_defaults(tmp_path):
    """Sections absent from YAML fall back to dataclass defaults."""
    yaml_file = tmp_path / "partial.yaml"
    yaml_file.write_text("defaults:\n  account_id: '99'\n")
    cfg = load_config(str(yaml_file))
    # google and safety sections are missing -> defaults
    assert cfg.google == GoogleConfig()
    assert cfg.safety == SafetyConfig()
    assert cfg.defaults.account_id == "99"
    assert cfg.defaults.container_id == ""


def test_empty_yaml_returns_defaults(tmp_path):
    """An empty YAML file (parsed as None) returns all defaults."""
    yaml_file = tmp_path / "empty.yaml"
    yaml_file.write_text("")
    cfg = load_config(str(yaml_file))
    assert cfg == GtmMcpConfig()


def test_dataclass_field_types():
    """Sanity-check that dataclass defaults have the expected types."""
    cfg = GtmMcpConfig()
    assert isinstance(cfg.google, GoogleConfig)
    assert isinstance(cfg.safety, SafetyConfig)
    assert isinstance(cfg.defaults, DefaultsConfig)
    assert isinstance(cfg.safety.allowed_container_ids, list)
    assert isinstance(cfg.safety.blocked_operations, list)
