"""Integration test: OAuth flow completes and token refreshes."""

from __future__ import annotations

import pytest

from gtm_mcp.auth import get_credentials
from tests.integration.conftest import skip_no_creds


@skip_no_creds
class TestAuth:
    def test_credentials_load_successfully(self, config):
        """OAuth credentials can be loaded or refreshed."""
        creds = get_credentials(config)
        assert creds is not None
        assert creds.valid

    def test_credentials_have_gtm_scope(self, config):
        """Loaded credentials include the GTM readonly scope."""
        creds = get_credentials(config)
        assert "tagmanager" in str(creds.scopes or "")
