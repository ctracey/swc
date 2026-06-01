---
description: Silently verify that the `swc-workload-mcp` server is registered and its tools are reachable. On success, return without output. On miss, delegate to the `mcp-install` guide skill. Use at the top of `context-init` and MCP-heavy front-line skills before any MCP tool call.
allowed-tools: Skill
---

# SWC MCP Check

Confirm `swc-workload-mcp` is available before any caller skill attempts an MCP tool call. Designed for silent use — emits no text on the happy path.

## Steps

### 1. Check tool availability

Inspect your currently-available tool list for any tool with a name prefixed by `mcp__swc-workload__` (e.g. `mcp__swc-workload__exists`, `mcp__swc-workload__list`).

- **If at least one such tool is present:** the MCP is registered. Return silently — emit no text, no confirmation. Continue to the next step of the calling skill.
- **If no such tool is present:** the MCP is missing. Continue to step 2.

### 2. Delegate to the install guide

Invoke the `mcp-install` skill. Do not emit your own message — the guide owns all user-facing text.

After the guide returns, return control to the calling skill without further output. The calling skill is responsible for deciding whether to halt or continue.

## Output

- **On success:** none.
- **On miss:** none from this skill; output is delegated to `mcp-install`.

Never emit a "MCP available" confirmation — silence is the success signal.
