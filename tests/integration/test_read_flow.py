"""Integration test: full read chain against real GTM API."""

from __future__ import annotations

import pytest

from gtm_mcp.tools.accounts import list_accounts
from gtm_mcp.tools.containers import list_containers
from gtm_mcp.tools.tags import list_tags
from gtm_mcp.tools.workspaces import list_workspaces
from tests.integration.conftest import skip_no_creds


@skip_no_creds
class TestReadFlow:
    def test_list_accounts_returns_data(self, config):
        """list_accounts returns at least one account."""
        result = list_accounts(config)
        assert "error" not in result
        assert result["total"] > 0
        assert "account_id" in result["accounts"][0]

    def test_list_containers_for_first_account(self, config):
        """list_containers returns containers for the first account."""
        accounts = list_accounts(config)
        assert "error" not in accounts
        account_id = accounts["accounts"][0]["account_id"]

        result = list_containers(config, account_id=account_id)
        assert "error" not in result
        assert result["total"] > 0

    def test_full_navigation_chain(self, config):
        """Navigate: accounts -> containers -> workspaces -> tags."""
        accounts = list_accounts(config)
        assert "error" not in accounts
        account_id = accounts["accounts"][0]["account_id"]

        containers = list_containers(config, account_id=account_id)
        assert "error" not in containers
        container_id = containers["containers"][0]["container_id"]

        workspaces = list_workspaces(
            config, account_id=account_id, container_id=container_id
        )
        assert "error" not in workspaces
        workspace_id = workspaces["workspaces"][0]["workspace_id"]

        tags = list_tags(
            config,
            account_id=account_id,
            container_id=container_id,
            workspace_id=workspace_id,
        )
        assert "error" not in tags
        assert isinstance(tags["total"], int)
