"""Tests for gtm_mcp.tools.versions — list_versions."""

from __future__ import annotations

from gtm_mcp.tools.versions import list_versions


def test_list_versions_success(config, mock_execute):
    mock_execute.return_value = {
        "containerVersionHeader": [
            {
                "containerVersionId": "10",
                "name": "v10 - prod deploy",
                "description": "Added GA4 config tag",
                "deleted": False,
                "numTags": "5",
                "numTriggers": "3",
                "numVariables": "7",
            },
            {
                "containerVersionId": "9",
                "name": "v9",
                "description": "",
                "deleted": True,
                "numTags": "4",
                "numTriggers": "2",
                "numVariables": "6",
            },
        ]
    }
    result = list_versions(config, account_id="1", container_id="2")
    assert result["total"] == 2
    assert result["versions"][0]["version_id"] == "10"
    assert result["versions"][0]["num_tags"] == "5"
    assert result["versions"][1]["deleted"] is True
    mock_execute.assert_called_once_with(
        config,
        "accounts.containers.version_headers.list",
        parent="accounts/1/containers/2",
    )


def test_list_versions_api_error(config, mock_execute):
    mock_execute.return_value = {"error": "Forbidden", "status": 403}
    result = list_versions(config, account_id="1", container_id="2")
    assert "error" in result


def test_list_versions_empty(config, mock_execute):
    mock_execute.return_value = {"containerVersionHeader": []}
    result = list_versions(config, account_id="1", container_id="2")
    assert result["total"] == 0
    assert result["versions"] == []


def test_list_versions_missing_fields(config, mock_execute):
    """Version headers with missing optional fields use defaults."""
    mock_execute.return_value = {
        "containerVersionHeader": [{"containerVersionId": "1"}]
    }
    result = list_versions(config, account_id="1", container_id="2")
    assert result["versions"][0]["name"] == ""
    assert result["versions"][0]["num_tags"] == "0"
    assert result["versions"][0]["deleted"] is False
