# Solution Design — 6: Add version skill to the swc plugin

## Approach

Create a `skills/version/SKILL.md` skill that reads the SWC plugin version from `.claude-plugin/plugin.json` via Bash, calls `mcp__swc-workload__version` for MCP server and CLI versions, and emits a single pipe-delimited line. Any value that cannot be resolved shows `MISSING`.

## Test approach

Lightweight — implement directly against the spec checklist, no automated test file.

## Technical decisions

- **Locating `plugin.json`**: use `${CLAUDE_SKILL_DIR}/../../.claude-plugin/plugin.json` — this resolves correctly from `skills/version/` to the plugin root regardless of the user's working directory.
- **Missing value handling**: catch failures per source independently so one missing value does not suppress the others.
