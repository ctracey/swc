# Specs — 6: Add version skill to the swc plugin

## Acceptance criteria

- Invoking the skill emits a single line showing all three versions, pipe-delimited: `SWC: <version> | MCP: <version> | CLI: <version>`
- SWC version is read from `.claude-plugin/plugin.json` (field: `version`)
- MCP and CLI versions are read from `mcp__swc-workload__version` (fields: `mcp`, `cli`)

## Error cases

- If any version value cannot be determined (file missing, field absent, MCP unavailable), the corresponding entry shows `MISSING` rather than failing outright
