---
description: Guide the user through installing the required `swc-workload-mcp` server when it is missing. Points the user at the MCP repo's usage docs for setup. Use when `mcp-check` reports the MCP is missing, or when the user asks how to install it.
---

# SWC MCP Install Guide

Surface the missing `swc-workload-mcp` dependency to the user. The plugin does not install the MCP — the user follows the upstream repo's usage docs.

## Steps

### 1. Tell the user the MCP is missing

Print exactly:

```
swc: required MCP `swc-workload-mcp` is not registered.

The SWC plugin depends on this external MCP server to manage workload state.
Without it, workflows that read or write work items cannot run.

To install and register it, follow the usage docs in the swc-workload-mcp repo:

  https://github.com/ctracey/swc-workload-mcp/blob/main/docs/usage.md

Once registered, restart this Claude Code session so the new MCP tools are loaded.
```

### 2. Stop

Do not attempt further work. Return control to the calling skill — the caller decides whether to halt the workflow.
