---
description: Scaffold a new .swc/<folder>/ with stub planning docs and initialise the MCP-owned workload artefact. Use when starting a fresh piece of work after the folder has been located by context-lookup.
allowed-tools: Write, Skill, mcp__swc-workload__init
---

# SWC Init

Create the stub planning docs for a new context folder. Called by `workflow_plan-context` after `context-lookup` has confirmed the folder path.

## Arguments

Receives the resolved context (including `absolute_path`), e.g. `/Users/.../project/.swc/feature_my-work`.

## Steps

### 0. Verify MCP dependency

Follow the `mcp-check` skill. If the MCP is missing, the check delegates to `mcp-install` which surfaces the guide — stop and return control to the caller. Do not proceed to scaffolding when the MCP is not registered.

> **Location is already confirmed.** `context-lookup --create` runs before this skill and prompts the user when `.swc/` doesn't yet exist. By the time `context-init` runs, the location has been accepted and `.swc/` exists.

### 1. Create stub files

Write the following files into `.swc/<folder>/`. Each file gets a title and section headers only — no content.

**Use the `Write` tool.** It creates parent directories (including `.swc/<folder>/`) as needed. **Do not run `mkdir` explicitly** — `Write(.swc/**)` is already allowlisted, but a bare `mkdir` will fire an extra permission prompt.

The workload artefact is owned by the `swc-workload` MCP and is created in step 2 below — do not write `workload.md` (or `workload.json`) from this skill.

**`plan.md`**
```markdown
# Plan

## Goal

## Background

## Approach

## Open Questions

```

**`architecture.md`**
```markdown
# Architecture

## Context

## Design

## Decisions

## Constraints

```

**`notes.md`**
```markdown
# Notes

## Decisions

## Risks

## References

```

**`changelog.md`**
```markdown
# Changelog

```

**`pipeline.md`**
```markdown
# Pipeline

## Build

**Command:** `<command to run>`
**Expected outcome:** <what a passing build looks like — exit code, key output, artefact produced>

## Dev environment

**Start command:** `<command to start>`
**Health check:** <URL, port, signal, or "not applicable">
**Stop command:** `<command to stop cleanly, or "ctrl-c">`

## Acceptance

<What the human needs to see to accept the work. Not automated — narrative. Or "Not applicable — verified by test suite only.">
```

### 2. Initialise the workload via MCP

Invoke `mcp__swc-workload__init` against the resolved context's `absolute_path` so the workload artefact is created at `.swc/<folder>/workload.json`. The MCP owns the artefact's shape and location — this skill does not write or read it directly.

If the MCP call fails, surface the error to the calling skill and stop. The stub files written in step 1 stay in place — the caller decides whether to retry or clean up.

### 3. Return

Return the folder path to the calling skill. Print nothing — the calling skill handles confirmation.

## Exit criteria

**Done when** the five narrative stubs (`plan.md`, `architecture.md`, `notes.md`, `changelog.md`, `pipeline.md`) exist at `.swc/<folder>/` AND `mcp__swc-workload__init` has succeeded for that folder.
