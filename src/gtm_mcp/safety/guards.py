"""Safety guards — container allowlist and read-only enforcement."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from gtm_mcp.config import GtmMcpConfig, SafetyConfig


class SafetyViolation(Exception):
    """Raised when a proposed action violates safety constraints."""


def check_read_only() -> dict[str, Any] | None:
    """Return an error dict if the server is in read-only mode, else None."""
    import gtm_mcp

    if gtm_mcp._read_only:
        return {
            "error": "Server is in read-only mode (Gate 1).",
            "hint": "Write operations are disabled. This is expected for Gate 1.",
        }
    return None


def check_container_allowed(container_id: str, config: SafetyConfig) -> None:
    """Reject if container_id is not in the configured allowlist.

    When ``allowed_container_ids`` is empty, all containers are permitted.
    """
    if not config.allowed_container_ids:
        return
    if container_id not in config.allowed_container_ids:
        raise SafetyViolation(
            f"Container ID {container_id} is not in the allowed list. "
            "Add it to config.yaml under safety.allowed_container_ids"
        )


def check_blocked_operation(operation: str, config: SafetyConfig) -> None:
    """Reject if operation is in the blocked list."""
    if operation in config.blocked_operations:
        raise SafetyViolation(f"Operation '{operation}' is blocked by configuration")


def check_write_safety(
    config: GtmMcpConfig,
    *,
    container_id: str,
    operation: str,
    dry_run: bool,
) -> dict[str, Any] | None:
    """Consolidated write-safety gate.

    Checks read-only mode, container allowlist, blocked operations, and
    require_dry_run policy.  Returns an error dict on failure, None on success.
    """
    read_only_error = check_read_only()
    if read_only_error is not None:
        return read_only_error

    try:
        check_container_allowed(container_id, config.safety)
        check_blocked_operation(operation, config.safety)
    except SafetyViolation as exc:
        return {
            "error": str(exc),
            "hint": "Update safety config to allow this operation, then retry.",
        }

    if config.safety.require_dry_run and not dry_run:
        return {
            "error": (
                "Live write blocked: safety.require_dry_run is enabled for this server."
            ),
            "hint": "Use dry_run=true or set safety.require_dry_run=false in config.",
        }

    return None


def check_destructive(confirm_destructive: bool) -> dict[str, Any] | None:
    """Fail-closed guard for destructive operations.

    Returns an error dict when *confirm_destructive* is ``False``, signalling
    the caller must first preview via ``dry_run=True`` and then explicitly
    confirm.
    """
    if not confirm_destructive:
        return {
            "error": "Destructive operation requires explicit confirmation.",
            "hint": "Set confirm_destructive=True after reviewing a dry_run=True preview.",
        }
    return None
