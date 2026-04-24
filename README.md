# gtm-mcp

MCP server for Google Tag Manager. Read GTM accounts, containers, workspaces, tags, triggers, variables, templates, versions, and folders — and, with explicit opt-in, create/update/delete them through guarded write tools.

Built with [FastMCP](https://github.com/jlowin/fastmcp). Safety-first: read-only by default, dry-run previews on every write, destructive-op confirmation guard, two-phase audit log, container allowlist.

## Status

Released in gates — each gate is a scope + a set of required safety controls. Completed work:

| Gate | Scope | Status |
|---|---|---|
| **Gate 1** | Read-only tools across all GTM resources | ✅ complete |
| **Gate 2** | Workspace-level CRUD for tags, triggers, variables (+ built-in variable enable/disable, workspace create) | ✅ complete |
| **Gate 3+** | Version creation and container publish flows | 🚧 not started |

Safety controls below apply in every gate and cannot be bypassed by the agent.

## Install

```bash
uv sync
```

## Authentication

Place Google OAuth credentials at `~/.gtm-mcp/credentials.json`. The first run opens a browser for consent; the refresh token is saved to `~/.gtm-mcp/token.json`. Service-account JSON is also accepted at the same `credentials_path`.

Required scope: `https://www.googleapis.com/auth/tagmanager.edit.containers` (write-capable; read-only scopes work for Gate 1 tools).

## Configuration

`~/.gtm-mcp/config.yaml` (all fields optional — defaults shown):

```yaml
google:
  credentials_path: "~/.gtm-mcp/credentials.json"
  token_path: "~/.gtm-mcp/token.json"

safety:
  # When true, every write tool runs as dry_run regardless of caller arg.
  require_dry_run: true
  # If non-empty, write tools refuse any container_id not in the list.
  allowed_container_ids: []
  # Operation names to block outright (e.g. "delete_tag").
  blocked_operations: []

defaults:
  account_id: ""
  container_id: ""
```

### Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `GTM_MCP_READ_ONLY` | `true` | When `true`, all write tools refuse execution regardless of config. Flip to `false` to unlock Gate 2 writes. |
| `GTM_MCP_CONFIG` | `~/.gtm-mcp/config.yaml` | Override the config file location. |

## Running

```bash
# Read-only (Gate 1 tools only)
uv run gtm-mcp

# Write-capable (Gate 2 tools active, still with dry-run/safety guards)
GTM_MCP_READ_ONLY=false uv run gtm-mcp
```

Wire into your MCP host (Claude Desktop, Claude Code, Cursor) via `.mcp.json` or its equivalent.

## Safety model

1. **Read-only default** — `GTM_MCP_READ_ONLY=true` at startup blocks all mutations.
2. **Dry-run preview on every write** — `dry_run=true` shows the resource payload that *would* be sent to GTM without calling the API. Default is true.
3. **`require_dry_run` config override** — even if the agent passes `dry_run=false`, the server forces `dry_run=true` when this flag is set.
4. **Container allowlist** — if `safety.allowed_container_ids` is non-empty, writes to any other container are rejected pre-flight.
5. **Operation blocklist** — named operations in `safety.blocked_operations` are refused.
6. **Destructive-op confirmation** — every delete tool requires an explicit `confirm_destructive=true` argument in addition to `dry_run=false`. No way to delete-by-accident.
7. **Two-phase audit log** — `log_attempt()` before the call, `log_result()` in a `finally` block. Durable append-only sink at `~/.gtm-mcp/audit.jsonl`. Includes dry-runs.

## Tools

Read (Gate 1):

- **Accounts** — `list_accounts`
- **Containers** — `list_containers`, `get_container`
- **Workspaces** — `list_workspaces`, `get_workspace_status`
- **Tags** — `list_tags`, `get_tag`
- **Triggers** — `list_triggers`, `get_trigger`
- **Variables** — `list_variables`, `get_variable`
- **Built-in variables** — `list_built_in_variables`
- **Templates** — `list_templates`, `get_template`
- **Versions** — `list_versions`
- **Folders** — `list_folders`, `get_folder_entities`
- **Audit** — `get_audit_log`

Write (Gate 2, guarded):

- **Workspaces** — `create_workspace`
- **Tags** — `create_tag`, `update_tag`, `delete_tag`
- **Triggers** — `create_trigger`, `update_trigger`, `delete_trigger`
- **Variables** — `create_variable`, `update_variable`, `delete_variable`
- **Built-in variables** — `enable_built_in_variables`, `disable_built_in_variables`

## Development

```bash
uv sync
uv run pytest                    # all tests
uv run pytest -m 'not integration'  # unit tests only (no credentials needed)
uv run ruff check .
uv run mypy src
```

Integration tests require `~/.gtm-mcp/credentials.json` and `~/.gtm-mcp/config.yaml` pointing to a GTM account you can write to. They are skipped automatically if credentials are missing.

## License

MIT.
