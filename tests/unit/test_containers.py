"""Tests for gtm_mcp.tools.containers — list_containers, get_container."""

from __future__ import annotations

from gtm_mcp.tools.containers import get_container, list_containers


def test_list_containers_success(config, mock_execute):
    mock_execute.return_value = {
        "container": [
            {
                "containerId": "C1",
                "name": "Web",
                "publicId": "GTM-ABC",
                "usageContext": ["web"],
                "domainName": ["example.com"],
                "notes": "prod",
            }
        ]
    }
    result = list_containers(config, account_id="111")
    assert result["total"] == 1
    assert result["containers"][0]["container_id"] == "C1"
    assert result["containers"][0]["public_id"] == "GTM-ABC"
    mock_execute.assert_called_once_with(config, "accounts.containers.list", parent="accounts/111")


def test_list_containers_api_error(config, mock_execute):
    mock_execute.return_value = {"error": "Not found", "status": 404}
    result = list_containers(config, account_id="999")
    assert "error" in result


def test_get_container_success(config, mock_execute):
    mock_execute.return_value = {
        "containerId": "C1",
        "name": "Web",
        "publicId": "GTM-ABC",
        "usageContext": ["web"],
        "domainName": ["example.com"],
        "notes": "prod",
        "tagManagerUrl": "https://tagmanager.google.com/#/container/accounts/111/containers/C1",
    }
    result = get_container(config, account_id="111", container_id="C1")
    assert result["container_id"] == "C1"
    assert result["tag_manager_url"].startswith("https://")
    mock_execute.assert_called_once_with(
        config,
        "accounts.containers.get",
        path="accounts/111/containers/C1",
    )


def test_get_container_api_error(config, mock_execute):
    mock_execute.return_value = {"error": "Forbidden", "status": 403}
    result = get_container(config, account_id="111", container_id="C1")
    assert result["error"] == "Forbidden"


def test_get_container_missing_fields(config, mock_execute):
    """Missing optional fields fall back to defaults."""
    mock_execute.return_value = {"containerId": "C2"}
    result = get_container(config, account_id="111", container_id="C2")
    assert result["container_id"] == "C2"
    assert result["name"] == ""
    assert result["domain_name"] == []
