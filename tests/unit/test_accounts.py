"""Tests for gtm_mcp.tools.accounts — list_accounts."""

from __future__ import annotations

from gtm_mcp.tools.accounts import list_accounts


def test_list_accounts_success(config, mock_execute):
    mock_execute.return_value = {
        "account": [
            {
                "accountId": "111",
                "name": "MotoExpert",
                "shareData": True,
                "fingerprint": "fp1",
            },
            {
                "accountId": "222",
                "name": "Second",
                "shareData": False,
                "fingerprint": "fp2",
            },
        ]
    }
    result = list_accounts(config)
    assert result["total"] == 2
    assert result["accounts"][0]["account_id"] == "111"
    assert result["accounts"][0]["name"] == "MotoExpert"
    assert result["accounts"][1]["share_data"] is False
    mock_execute.assert_called_once_with(config, "accounts.list")


def test_list_accounts_empty(config, mock_execute):
    mock_execute.return_value = {"account": []}
    result = list_accounts(config)
    assert result["total"] == 0
    assert result["accounts"] == []


def test_list_accounts_api_error(config, mock_execute):
    mock_execute.return_value = {"error": "Auth failed", "status": 401, "hint": "Re-auth"}
    result = list_accounts(config)
    assert "error" in result
    assert result["error"] == "Auth failed"


def test_list_accounts_missing_fields(config, mock_execute):
    """Accounts with missing optional fields still produce valid output."""
    mock_execute.return_value = {"account": [{"accountId": "333"}]}
    result = list_accounts(config)
    assert result["total"] == 1
    assert result["accounts"][0]["name"] == ""
    assert result["accounts"][0]["share_data"] is False
