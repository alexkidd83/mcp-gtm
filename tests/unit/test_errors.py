"""Tests for gtm_mcp.api.errors — translate_api_error."""

from __future__ import annotations

from unittest.mock import MagicMock

from gtm_mcp.api.errors import translate_api_error


def _make_http_error(status: int, reason: str = "error reason") -> MagicMock:
    """Create a mock googleapiclient.errors.HttpError."""
    exc = MagicMock()
    exc.__class__ = type("HttpError", (), {})
    # We need a real HttpError-like object that passes isinstance check.
    # Easier: import HttpError and build one properly.
    from googleapiclient.errors import HttpError

    resp = MagicMock()
    resp.status = status
    resp.reason = reason
    return HttpError(resp=resp, content=b"error body")


def test_translate_401():
    err = _make_http_error(401)
    result = translate_api_error(err)
    assert result["status"] == 401
    assert "Authentication" in result["hint"] or "token" in result["hint"]


def test_translate_403():
    err = _make_http_error(403)
    result = translate_api_error(err)
    assert result["status"] == 403
    assert "Permission" in result["hint"]


def test_translate_404():
    err = _make_http_error(404)
    result = translate_api_error(err)
    assert result["status"] == 404
    assert "not found" in result["hint"].lower()


def test_translate_429():
    err = _make_http_error(429)
    result = translate_api_error(err)
    assert result["status"] == 429
    assert "Rate limit" in result["hint"]


def test_translate_generic_http_error():
    err = _make_http_error(500)
    result = translate_api_error(err)
    assert result["status"] == 500
    assert "Unexpected API error" in result["hint"]


def test_translate_non_http_exception():
    exc = RuntimeError("connection timeout")
    result = translate_api_error(exc)
    assert "error" in result
    assert "connection timeout" in result["error"]
    assert "status" not in result
    assert "Unexpected error" in result["hint"]
