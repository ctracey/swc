# Architecture

## Context

The SWC plugin is structured around three pillars: workload, workflows, context. This change reshapes the *workload* pillar by externalising its mechanics to an MCP service, while leaving workflows and context unchanged in shape.

## Design

```
┌──────────────────────────────────────────────────────────────┐
│  swc plugin (Claude Code)                                    │
│                                                              │
│  ┌────────────────────────────┐                              │
│  │ context-lookup             │  resolves branch → folder    │
│  │  - reads _meta.json        │                              │
│  │  - asks MCP `exists`       │                              │
│  └─────────┬──────────────────┘                              │
│            │                                                 │
│  ┌─────────▼──────────────────┐                              │
│  │ workflow skills            │  Plan / Deliver / Implement  │
│  │  - hand <folder> to MCP    │                              │
│  │  - drive conversation      │                              │
│  └─────────┬──────────────────┘                              │
│            │                                                 │
│            │ MCP tool calls                                  │
│            ▼                                                 │
└──────────────────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│  swc-workload-mcp                                            │
│   - manages workload.json at a given path                    │
│   - tools: init, exists, list, find, get, add, set_status    │
└──────────────────────────────────────────────────────────────┘
```

## Decisions

- **Single PR, phased internally** — deletes and plumbing first, then rewrites, then docs/tests. Each phase leaves the plugin in a working state.
- **`workload.json` not `workload.md`** — JSON is the natural shape for the MCP's structured tool surface. Noisier PR diffs accepted.
- **Plugin keeps `_meta.json`** — branch→folder mapping is a plugin concern; MCP only sees a single path.
- **`context-init` calls MCP `init`** — single scaffold call site, fired when the rest of the narrative docs are stubbed.
- **Spawned agents use MCP, not file reads** — implementation agents get their work item details via MCP `get`, not by parsing `workload.md`.

## Constraints

- The MCP must be installable at project level alongside the plugin (matches existing plugin install pattern)
- Spawned implementation agents must inherit MCP access — no per‑spawn registration prompts
- Plugin must remain functional at each phase boundary so the PR can be reviewed incrementally
