# GTM MCP Gate 2 Acceptance Checklist

Gate 2 scope: workspace-level CRUD only. No version creation or publish flows.

## Safety Controls

- [x] Write mode defaults to OFF (`GTM_MCP_READ_ONLY=true`).
- [x] Every write tool supports `dry_run=true` preview.
- [x] Live writes are blocked when `safety.require_dry_run=true`.
- [x] Container allowlist is enforced (`safety.allowed_container_ids`).
- [x] Blocked operations are enforced (`safety.blocked_operations`).
- [x] `check_write_safety()` extracted to `guards.py` (shared by all write tools).
- [x] `check_destructive()` fail-closed guard — requires `confirm_destructive=True` for all deletes.
- [x] Two-phase audit logging: `log_attempt()` pre-call, `log_result()` in `try/finally`.
- [x] Durable audit sink: append-only `~/.gtm-mcp/audit.jsonl`.

## Tag CRUD

- [x] `create_tag` tool implemented and unit-tested.
- [x] `update_tag` tool implemented and unit-tested.
- [x] `delete_tag` tool implemented and unit-tested (with `confirm_destructive` guard).
- [x] Server registers all three tools with non-read-only annotations.

## Trigger CRUD

- [x] `create_trigger` tool implemented and unit-tested.
- [x] `update_trigger` tool implemented and unit-tested.
- [x] `delete_trigger` tool implemented and unit-tested (with `confirm_destructive` guard).
- [x] Server registers all three tools with correct annotations.

## Variable CRUD

- [x] `create_variable` tool implemented and unit-tested.
- [x] `update_variable` tool implemented and unit-tested.
- [x] `delete_variable` tool implemented and unit-tested (with `confirm_destructive` guard).
- [x] Server registers all three tools with correct annotations.

## Built-In Variables

- [x] `enable_built_in_variables` tool implemented and unit-tested.
- [x] `disable_built_in_variables` tool implemented and unit-tested (with `confirm_destructive` guard).
- [x] Server registers both tools with correct annotations.

## Workspace

- [x] `create_workspace` tool implemented and unit-tested.
- [x] Server registers tool with `_WRITE` annotation.

## Audit Log

- [x] `get_audit_log` read tool implemented and unit-tested.
- [x] Server registers tool with `_READONLY` annotation.

## Test & Runtime Gates

- [x] Unit tests pass locally (101/101).
- [x] Startup smoke test passes (`python -m gtm_mcp` imports cleanly).
- [x] Integration tests still pass in read-only mode.

## Deferred to Gate 3

- [ ] Version creation/publish tools.
- [ ] Workspace sync and conflict resolution flows.
- [ ] Multi-step rollback for live mutations.
- [ ] `SafetyConfig.mode` refactor (replace `_read_only` env var with config-driven mode).
