---
description: Clarify requirements for a work item before implementation — intent, constraints, and high-level solution direction. First phase of the delivery conversation. Use when clarifying what needs to be built, or when invoked via /workflowDeliver_requirements.
allowed-tools: Read, Write, Glob, Grep, Bash, Skill, mcp__swc-workload__list
---

# Deliver Requirements

Establish intent and high-level solution direction before specs or implementation begin. This stage covers *what and why* plus rough approach. Technical design detail belongs in specs.

## Steps

### 1. Load SWC context

Locate the active context folder via `context-lookup`, then in parallel:
- Read `plan.md`
- Read `architecture.md`
- Read `notes.md`
- Invoke `mcp__swc-workload__list` with `ref=<N>` and `json=true` against the resolved context's `absolute_path` to fetch the specific work item

Also check for existing task-specific docs at `.swc/<folder>/workitems/<N>/`. `<N>` is the **full work item number** — e.g. `1.1`, `2.3`, not just the top-level number. If files exist there (e.g. a prior `requirements.md`), read them. This is a resumption — summarise what was previously captured and ask the user whether to continue from it or start fresh.

### 2. Load codebase context

Use the work item title and description to identify relevant codebase areas. Run targeted searches:
- Grep for symbols, file names, or concepts mentioned in the work item
- Read files that are clearly in scope

This is a focused read, not a full scan. Load enough to ground the conversation — not everything.

If no codebase is present (docs-only or new project), skip this step.

### 3. Open the conversation

State what you understand about the intent from the docs so far — one short paragraph covering what the work item is, why it exists, and any constraints already documented. Declare your reading directly rather than inviting disagreement up front.

If the work item description is genuinely thin (a single line with no context), flag it:
> "The work item entry is brief — I've got [title] but not much else. Want to give me more context before we dig in, or is keeping it simple intentional?"

### 4. Clarify intent

Declare what's already clear from the docs, then ask only genuine branch-point questions in a single pass — things the user must answer before the direction is settled. Do not loop one question at a time or play back before moving on.

Target a clear picture of:
- **What** is being built and for whom
- **Why** it's needed — the problem or outcome it addresses
- **Constraints** — things that must hold true regardless of approach
- **Out of scope** — anything explicitly not included

Calibrate depth to complexity: simple/standard items may need no questions at all. Stay in the problem space. If the user raises implementation specifics, note them and park:
> "Good to know — I'll capture that. Let's make sure we've got the intent solid first."

### 5. Summarise intent and proceed

Play back the intent picture before shifting to solution:

> "So: [what], for [who/context], because [why]. The key outcome is [what changes or is achieved]. Constraints: [list if any]."

Then proceed to solution direction. If the user has corrections they will say so.

### 6. Explore high-level solution direction

Shift to approach. If there is an obvious approach given the codebase context loaded in step 2, state it:
> "Given how [existing pattern/file/skill] works, the natural approach would be [X]."

Ask only if the direction is genuinely unclear:
> "How are you thinking of approaching it?"

This is approach confirmation, not design: what kind of thing are we building, what are the major constraints, are there obvious alternatives to rule out? Keep it high-level.

### 7. Write requirements doc

Write to `.swc/<folder>/workitems/<N>/requirements.md`:

```markdown
# Requirements — [work item number]: [work item name]

## Intent

[One paragraph: what this is, why it exists, for whom]

## Constraints

[Bulleted list — things that must hold true regardless of approach. Omit section if none.]

## Out of scope

[Bulleted list — explicitly excluded. Omit section if none.]

## Approach direction

[One or two sentences: what kind of thing we're building, major approach constraints. Not a design — just enough to ground the specs conversation.]

## Parked

[Notes from the conversation that were deferred — implementation details, open questions, things to revisit in specs. Omit section if nothing was parked.]
```

Create the `workitems/<N>/` directory if it doesn't exist.

### 8. Confirm and hand off

Show the user the requirements doc path and its contents, then ask:
> "Does that capture it? Happy to move to specs."

Wait for confirmation. Address any corrections, then proceed.

## Exit criteria

**Done when:**
- SWC and codebase context loaded
- Intent confirmed by the user
- Approach direction agreed
- `requirements.md` written to `.swc/<folder>/workitems/<N>/`

**Return control to the calling skill.**
