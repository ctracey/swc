# Plan — Migrate workload management to swc-workload-mcp

## Goal

Replace the plugin's in‑process workload artefact management with calls to an external MCP service (`swc-workload-mcp`), so the plugin no longer owns the workload file format, parsing, rendering, or status mechanics.

## Background

Today the plugin owns both *where* the workload lives (branch → folder resolution, `_meta.json`) and *what's inside it* (markdown checkboxes, parent rollup rules, render script, status updates). The new MCP narrows that — it manages a single workload artefact at a given path. The artefact is being renamed `workload.md` → `workload.json`.

This frees the plugin to focus on its remaining responsibilities: branch→folder resolution, workflow orchestration, and the narrative docs that live alongside the workload.

## Approach

A single PR, worked in phases that each leave the plugin in a working state:

1. **Plumbing** — register the MCP, allowlist its tools, document installation
2. **Delete superseded skills** — the four artefact‑mechanics skills go entirely
3. **Adapt scaffolding** — `context-init` no longer stubs the workload file; calls MCP `init` instead
4. **Reframe `context-lookup`** — output speaks in terms of *context* + *workload presence*, not workload paths
5. **Rewrite workflow touchpoints** — every workflow skill that read or wrote `workload.md` now calls MCP tools
6. **Update spawned‑agent prompts** — implementation agents interface with the MCP, not the workload file
7. **Update narrative docs** — README, plugin‑design, file‑structure docs
8. **Tests** — remove dead tests, decide MCP test strategy

## Out of scope

- Any change to the other narrative docs (`plan.md`, `architecture.md`, `notes.md`, `changelog.md`, `pipeline.md`) — these stay plugin‑owned
- `_meta.json` and branch→folder mapping — these stay plugin‑owned
- `pipeline.md` artefact — stays plugin‑owned (sits alongside the workload but is unrelated to it)
- Changes to the MCP service itself — assumed complete and stable

## Delivery shape

- One PR, eight work items
- Phases sequenced so each leaves the plugin functional
- Plumbing first (item 1) so subsequent rewrites can actually call the MCP
- Deletes (item 2) before rewrites (items 3–6) to avoid maintaining dead code mid‑refactor
- Docs and tests last (items 7–8) once the behaviour has settled

## Open questions

None outstanding — scope, boundary, and approach all confirmed in planning conversation. See `notes.md` for the agreed MCP boundary and naming decisions.
