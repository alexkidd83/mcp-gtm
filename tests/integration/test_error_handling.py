"""Integration test: real API errors return structured error dicts."""

from __future__ import annotations

import pytest

from gtm_mcp.tools.containers import list_containers
from gtm_mcp.tools.tags import get_tag
from tests.integration.conftest import skip_no_creds


@skip_no_creds
class TestErrorHandling:
    def test_invalid_account_id_returns_error(self, config):
        """A nonexistent account ID returns a structured error, not a crash."""
        result = list_containers(config, account_id="999999999")
        assert "error" in result

    def test_invalid_tag_id_returns_error(self, config):
        """A nonexistent tag ID returns a structured error."""
        result = get_tag(
            config,
            account_id="1",
            container_id="1",
            workspace_id="1",
            tag_id="99999",
        )
        assert "error" in result
