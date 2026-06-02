---
description: Scaffold a new .swc/<folder>/ with stub planning docs and initialise the MCP-owned workload artefact. Use when starting a fresh piece of work after the folder has been located by context-lookup.
allowed-tools: Read, Write, Bash, Skill, mcp__swc-workload__init
---

# SWC Init

Create the stub planning docs for a new context folder. Called by `workflow_plan-context` after `context-lookup` has confirmed the folder path.

## Arguments

Receives the resolved context (including `absolute_path`), e.g. `/Users/.../project/.swc/feature_my-work`.

## Steps

### 0. Verify MCP dependency

Follow the `mcp-check` skill. If the MCP is missing, the check delegates to `mcp-install` which surfaces the guide — stop and return control to the caller. Do not proceed to scaffolding when the MCP is not registered.

### 1. Confirm context location

Determine whether `.swc/` already exists in the current working directory.

- **If `.swc/` exists** — SWC has been initialised in this project before. Skip this step silently and proceed to step 2.

- **If `.swc/` does NOT exist** — this is the first SWC context being created here. Pause and confirm with the user before scaffolding anywhere.

  Resolve two paths:
  - `<cwd>` — the current working directory
  - `<repo_root>` — run `git rev-parse --show-toplevel` (empty if not a git repo)

  Show the user:

  > "SWC stores its context docs in a `.swc/` folder. This is the first time you're using SWC in this project — `.swc/` will be created at:
  >
  >   `<cwd>`
  >
  > [Include the next two lines only if `<repo_root>` is non-empty AND `<cwd>` != `<repo_root>`:]
  > This is not the repository root. The repo root is `<repo_root>`. SWC context usually lives at the repo root so it travels with the project — consider switching there before continuing.
  >
  > Proceed and create `.swc/` here? (y/n)"

  Wait for the user's answer.

  - **Yes** — proceed to step 2.
  - **No** — stop and return control to the caller. Do not create `.swc/` or any files. The user is expected to change directory and re-invoke the workflow.

### 2. Create stub files

Write the following files into `.swc/<folder>/`. Each file gets a title and section headers only — no content.

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

### 3. Initialise the workload via MCP

Invoke `mcp__swc-workload__init` against the resolved context's `absolute_path` so the workload artefact is created at `.swc/<folder>/workload.json`. The MCP owns the artefact's shape and location — this skill does not write or read it directly.

If the MCP call fails, surface the error to the calling skill and stop. The stub files written in step 1 stay in place — the caller decides whether to retry or clean up.

### 4. Return

Return the folder path to the calling skill. Print nothing — the calling skill handles confirmation.

## Exit criteria

**Done when** the five narrative stubs (`plan.md`, `architecture.md`, `notes.md`, `changelog.md`, `pipeline.md`) exist at `.swc/<folder>/` AND `mcp__swc-workload__init` has succeeded for that folder.
