---
description: Print the SWC plugin version, MCP server version, and CLI version in a single line. Use when the user asks "what version", "show version", "swc version", or invokes /version.
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/version.py *), mcp__swc-workload__version
---

# SWC Version

Emit a single line showing the SWC plugin version, MCP server version, and CLI version.

## Steps

### 1. Run the version script

Run:

```bash
python3 ${CLAUDE_SKILL_DIR}/version.py ${CLAUDE_SKILL_DIR}
```

Parse the JSON output. Extract:
- `swc` → `<swc_version>`
- `mcp_available` → `<mcp_available>`

### 2. Get MCP and CLI versions

If `<mcp_available>` is `false`: set `<mcp_version>` = `N/A` and `<cli_version>` = `N/A`.

If `<mcp_available>` is `true`: invoke `mcp__swc-workload__version` and extract:
- `mcp` field → `<mcp_version>` (use `N/A` if absent or the call fails)
- `cli` field → `<cli_version>` (use `N/A` if null, absent, or the call fails)

### 3. Emit the version line

Print exactly:

```
SWC: <swc_version> | MCP: <mcp_version> | CLI: <cli_version>
```

No preamble, no trailing text.
