"""GTM MCP Server — Gate 1 read + Gate 2 guarded writes."""

from __future__ import annotations

from fastmcp import FastMCP

try:
    # fastmcp<=3.1 exported ToolAnnotations from fastmcp.tools.
    from fastmcp.tools import ToolAnnotations
except ImportError:  # pragma: no cover - depends on installed fastmcp version
    # fastmcp>=3.2 uses the MCP SDK type directly.
    from mcp.types import ToolAnnotations

from gtm_mcp.config import GtmMcpConfig, load_config

mcp = FastMCP(
    "GTM",
    instructions=(
        "Google Tag Manager MCP server (Gate 1 read + Gate 2 guarded writes). "
        "Provides tools to inspect GTM accounts, containers, workspaces, "
        "tags, triggers, variables, templates, versions, and folders. "
        "Tag write tools are available with dry-run previews and safety checks. "
        "Server starts in read-only mode by default."
    ),
)

_config: GtmMcpConfig = load_config()

_READONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False)
_WRITE = ToolAnnotations(readOnlyHint=False, destructiveHint=False)
_DESTRUCTIVE = ToolAnnotations(readOnlyHint=False, destructiveHint=True)


# ---------------------------------------------------------------------------
# Accounts
# ---------------------------------------------------------------------------


@mcp.tool(annotations=_READONLY)
def list_accounts() -> dict:
    """List all GTM accounts accessible to the authenticated user."""
    from gtm_mcp.tools.accounts import list_accounts as _impl

    return _impl(_config)


# ---------------------------------------------------------------------------
# Containers
# ---------------------------------------------------------------------------


@mcp.tool(annotations=_READONLY)
def list_containers(account_id: str) -> dict:
    """List all containers in a GTM account."""
    from gtm_mcp.tools.containers import list_containers as _impl

    return _impl(_config, account_id=account_id)


@mcp.tool(annotations=_READONLY)
def get_container(account_id: str, container_id: str) -> dict:
    """Get details for a single GTM container."""
    from gtm_mcp.tools.containers import get_container as _impl

    return _impl(_config, account_id=account_id, container_id=container_id)


# ---------------------------------------------------------------------------
# Workspaces
# ---------------------------------------------------------------------------


@mcp.tool(annotations=_READONLY)
def list_workspaces(account_id: str, container_id: str) -> dict:
    """List all workspaces in a GTM container."""
    from gtm_mcp.tools.workspaces import list_workspaces as _impl

    return _impl(_config, account_id=account_id, container_id=container_id)


@mcp.tool(annotations=_READONLY)
def get_workspace_status(account_id: str, container_id: str, workspace_id: str) -> dict:
    """Get pending changes and conflicts for a workspace."""
    from gtm_mcp.tools.workspaces import get_workspace_status as _impl

    return _impl(
        _config,
        account_id=account_id,
        container_id=container_id,
        workspace_id=workspace_id,
    )


@mcp.tool(annotations=_WRITE)
def create_workspace(
    account_id: str,
    container_id: str,
    name: str,
    description: str = "",
    dry_run: bool = True,
) -> dict:
    """Create a new workspace in a GTM container (Gate 2, safety-guarded)."""
    from gtm_mcp.tools.workspaces import create_workspace as _impl

    return _impl(
        _config,
        account_id=account_id,
        container_id=container_id,
        name=name,
        description=description,
        dry_run=dry_run,
    )


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------


@mcp.tool(annotations=_READONLY)
def list_tags(account_id: str, container_id: str, workspace_id: str) -> dict:
    """List all tags in a GTM workspace."""
    from gtm_mcp.tools.tags import list_tags as _impl

    return _impl(
        _config,
        account_id=account_id,
        container_id=container_id,
        workspace_id=workspace_id,
    )


@mcp.tool(annotations=_READONLY)
def get_tag(
    account_id: str, container_id: str, workspace_id: str, tag_id: str
) -> dict:
    """Get full details for a single tag, including parameters and firing triggers."""
    from gtm_mcp.tools.tags import get_tag as _impl

    return _impl(
        _config,
        account_id=account_id,
        container_id=container_id,
        workspace_id=workspace_id,
        tag_id=tag_id,
    )


@mcp.tool(annotations=_WRITE)
def create_tag(
    account_id: str,
    container_id: str,
    workspace_id: str,
    tag: dict,
    dry_run: bool = True,
) -> dict:
    """Create a new GTM tag in a workspace (Gate 2, safety-guarded)."""
    from gtm_mcp.tools.tags import create_tag as _impl

    return _impl(
        _config,
        account_id=account_id,
        container_id=container_id,
        workspace_id=workspace_id,
        tag=tag,
        dry_run=dry_run,
    )


@mcp.tool(annotations=_WRITE)
def update_tag(
    account_id: str,
    container_id: str,
    workspace_id: str,
    tag_id: str,
    tag: dict,
    dry_run: bool = True,
) -> dict:
    """Update an existing GTM tag in a workspace (Gate 2, safety-guarded)."""
    from gtm_mcp.tools.tags import update_tag as _impl

    return _impl(
        _config,
        account_id=account_id,
        container_id=container_id,
        workspace_id=workspace_id,
        tag_id=tag_id,
        tag=tag,
        dry_run=dry_run,
    )


@mcp.tool(annotations=_DESTRUCTIVE)
def delete_tag(
    account_id: str,
    container_id: str,
    workspace_id: str,
    tag_id: str,
    dry_run: bool = True,
) -> dict:
    """Delete a GTM tag from a workspace (Gate 2, safety-guarded)."""
    from gtm_mcp.tools.tags import delete_tag as _impl

    return _impl(
        _config,
        account_id=account_id,
        container_id=container_id,
        workspace_id=workspace_id,
        tag_id=tag_id,
        dry_run=dry_run,
    )


# ---------------------------------------------------------------------------
# Triggers
# ---------------------------------------------------------------------------


@mcp.tool(annotations=_READONLY)
def list_triggers(account_id: str, container_id: str, workspace_id: str) -> dict:
    """List all triggers in a GTM workspace."""
    from gtm_mcp.tools.triggers import list_triggers as _impl

    return _impl(
        _config,
        account_id=account_id,
        container_id=container_id,
        workspace_id=workspace_id,
    )


@mcp.tool(annotations=_READONLY)
def get_trigger(
    account_id: str, container_id: str, workspace_id: str, trigger_id: str
) -> dict:
    """Get full details for a single trigger, including filter conditions."""
    from gtm_mcp.tools.triggers import get_trigger as _impl

    return _impl(
        _config,
        account_id=account_id,
        container_id=container_id,
        workspace_id=workspace_id,
        trigger_id=trigger_id,
    )


@mcp.tool(annotations=_WRITE)
def create_trigger(
    account_id: str,
    container_id: str,
    workspace_id: str,
    trigger: dict,
    dry_run: bool = True,
) -> dict:
    """Create a new GTM trigger in a workspace (Gate 2, safety-guarded)."""
    from gtm_mcp.tools.triggers import create_trigger as _impl

    return _impl(
        _config,
        account_id=account_id,
        container_id=container_id,
        workspace_id=workspace_id,
        trigger=trigger,
        dry_run=dry_run,
    )


@mcp.tool(annotations=_WRITE)
def update_trigger(
    account_id: str,
    container_id: str,
    workspace_id: str,
    trigger_id: str,
    trigger: dict,
    dry_run: bool = True,
) -> dict:
    """Update an existing GTM trigger in a workspace (Gate 2, safety-guarded)."""
    from gtm_mcp.tools.triggers import update_trigger as _impl

    return _impl(
        _config,
        account_id=account_id,
        container_id=container_id,
        workspace_id=workspace_id,
        trigger_id=trigger_id,
        trigger=trigger,
        dry_run=dry_run,
    )


@mcp.tool(annotations=_DESTRUCTIVE)
def delete_trigger(
    account_id: str,
    container_id: str,
    workspace_id: str,
    trigger_id: str,
    dry_run: bool = True,
    confirm_destructive: bool = False,
) -> dict:
    """Delete a GTM trigger from a workspace (Gate 2, safety-guarded)."""
    from gtm_mcp.tools.triggers import delete_trigger as _impl

    return _impl(
        _config,
        account_id=account_id,
        container_id=container_id,
        workspace_id=workspace_id,
        trigger_id=trigger_id,
        dry_run=dry_run,
        confirm_destructive=confirm_destructive,
    )


# ---------------------------------------------------------------------------
# Variables
# ---------------------------------------------------------------------------


@mcp.tool(annotations=_READONLY)
def list_variables(account_id: str, container_id: str, workspace_id: str) -> dict:
    """List all user-defined variables in a GTM workspace."""
    from gtm_mcp.tools.variables import list_variables as _impl

    return _impl(
        _config,
        account_id=account_id,
        container_id=container_id,
        workspace_id=workspace_id,
    )


@mcp.tool(annotations=_READONLY)
def get_variable(
    account_id: str, container_id: str, workspace_id: str, variable_id: str
) -> dict:
    """Get full details for a single variable, including parameters."""
    from gtm_mcp.tools.variables import get_variable as _impl

    return _impl(
        _config,
        account_id=account_id,
        container_id=container_id,
        workspace_id=workspace_id,
        variable_id=variable_id,
    )


@mcp.tool(annotations=_WRITE)
def create_variable(
    account_id: str,
    container_id: str,
    workspace_id: str,
    variable: dict,
    dry_run: bool = True,
) -> dict:
    """Create a new GTM variable in a workspace (Gate 2, safety-guarded)."""
    from gtm_mcp.tools.variables import create_variable as _impl

    return _impl(
        _config,
        account_id=account_id,
        container_id=container_id,
        workspace_id=workspace_id,
        variable=variable,
        dry_run=dry_run,
    )


@mcp.tool(annotations=_WRITE)
def update_variable(
    account_id: str,
    container_id: str,
    workspace_id: str,
    variable_id: str,
    variable: dict,
    dry_run: bool = True,
) -> dict:
    """Update an existing GTM variable in a workspace (Gate 2, safety-guarded)."""
    from gtm_mcp.tools.variables import update_variable as _impl

    return _impl(
        _config,
        account_id=account_id,
        container_id=container_id,
        workspace_id=workspace_id,
        variable_id=variable_id,
        variable=variable,
        dry_run=dry_run,
    )


@mcp.tool(annotations=_DESTRUCTIVE)
def delete_variable(
    account_id: str,
    container_id: str,
    workspace_id: str,
    variable_id: str,
    dry_run: bool = True,
    confirm_destructive: bool = False,
) -> dict:
    """Delete a GTM variable from a workspace (Gate 2, safety-guarded)."""
    from gtm_mcp.tools.variables import delete_variable as _impl

    return _impl(
        _config,
        account_id=account_id,
        container_id=container_id,
        workspace_id=workspace_id,
        variable_id=variable_id,
        dry_run=dry_run,
        confirm_destructive=confirm_destructive,
    )


# ---------------------------------------------------------------------------
# Built-In Variables
# ---------------------------------------------------------------------------


@mcp.tool(annotations=_READONLY)
def list_built_in_variables(
    account_id: str, container_id: str, workspace_id: str
) -> dict:
    """List all enabled built-in variables in a GTM workspace."""
    from gtm_mcp.tools.built_in_vars import list_built_in_variables as _impl

    return _impl(
        _config,
        account_id=account_id,
        container_id=container_id,
        workspace_id=workspace_id,
    )


@mcp.tool(annotations=_WRITE)
def enable_built_in_variables(
    account_id: str,
    container_id: str,
    workspace_id: str,
    variable_types: list[str],
    dry_run: bool = True,
) -> dict:
    """Enable built-in variables in a GTM workspace (Gate 2, safety-guarded)."""
    from gtm_mcp.tools.built_in_vars import enable_built_in_variables as _impl

    return _impl(
        _config,
        account_id=account_id,
        container_id=container_id,
        workspace_id=workspace_id,
        variable_types=variable_types,
        dry_run=dry_run,
    )


@mcp.tool(annotations=_DESTRUCTIVE)
def disable_built_in_variables(
    account_id: str,
    container_id: str,
    workspace_id: str,
    variable_types: list[str],
    dry_run: bool = True,
    confirm_destructive: bool = False,
) -> dict:
    """Disable built-in variables in a GTM workspace (Gate 2, safety-guarded)."""
    from gtm_mcp.tools.built_in_vars import disable_built_in_variables as _impl

    return _impl(
        _config,
        account_id=account_id,
        container_id=container_id,
        workspace_id=workspace_id,
        variable_types=variable_types,
        dry_run=dry_run,
        confirm_destructive=confirm_destructive,
    )


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------


@mcp.tool(annotations=_READONLY)
def list_templates(account_id: str, container_id: str, workspace_id: str) -> dict:
    """List all custom templates in a GTM workspace."""
    from gtm_mcp.tools.templates import list_templates as _impl

    return _impl(
        _config,
        account_id=account_id,
        container_id=container_id,
        workspace_id=workspace_id,
    )


@mcp.tool(annotations=_READONLY)
def get_template(
    account_id: str, container_id: str, workspace_id: str, template_id: str
) -> dict:
    """Get full details for a single custom template."""
    from gtm_mcp.tools.templates import get_template as _impl

    return _impl(
        _config,
        account_id=account_id,
        container_id=container_id,
        workspace_id=workspace_id,
        template_id=template_id,
    )


# ---------------------------------------------------------------------------
# Audit Log
# ---------------------------------------------------------------------------


@mcp.tool(annotations=_READONLY)
def get_audit_log(limit: int = 50) -> dict:
    """Read recent mutation audit entries from the server's local audit trail."""
    from gtm_mcp.tools.audit_log import get_audit_log as _impl

    return _impl(limit=limit)


# ---------------------------------------------------------------------------
# Versions
# ---------------------------------------------------------------------------


@mcp.tool(annotations=_READONLY)
def list_versions(account_id: str, container_id: str) -> dict:
    """List all published versions for a GTM container."""
    from gtm_mcp.tools.versions import list_versions as _impl

    return _impl(_config, account_id=account_id, container_id=container_id)


# ---------------------------------------------------------------------------
# Folders
# ---------------------------------------------------------------------------


@mcp.tool(annotations=_READONLY)
def list_folders(account_id: str, container_id: str, workspace_id: str) -> dict:
    """List all organizational folders in a GTM workspace."""
    from gtm_mcp.tools.folders import list_folders as _impl

    return _impl(
        _config,
        account_id=account_id,
        container_id=container_id,
        workspace_id=workspace_id,
    )


@mcp.tool(annotations=_READONLY)
def get_folder_entities(
    account_id: str, container_id: str, workspace_id: str, folder_id: str
) -> dict:
    """Get all tags, triggers, and variables inside a folder."""
    from gtm_mcp.tools.folders import get_folder_entities as _impl

    return _impl(
        _config,
        account_id=account_id,
        container_id=container_id,
        workspace_id=workspace_id,
        folder_id=folder_id,
    )
