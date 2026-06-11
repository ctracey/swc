# Requirements — 6: Add version skill to the swc plugin

## Intent

A `/version` skill for the SWC plugin that surfaces three version numbers in a single readout: the SWC plugin version, the MCP server version, and the SWC CLI version. Exists so any user can quickly confirm what they're running without digging into files or MCP internals.

## Approach direction

Read the SWC version from `.claude-plugin/plugin.json` via Bash, call `mcp__swc-workload__version` for the MCP server and CLI versions, and render all three cleanly. No Python helpers — two calls, one output.
