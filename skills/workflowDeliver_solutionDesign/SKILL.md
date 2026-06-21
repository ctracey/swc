---
description: Resolve implementation-level questions before the agent brief is sealed. Third phase of the delivery conversation. Use when preparing the agent brief, surfacing technical challenges, or when invoked via /workflowDeliver_solutionDesign.
allowed-tools: Read, Write, Glob, Grep
---

# Deliver — Solution Design Stage

Surface and resolve implementation-level questions specific to this work item before the agent brief is sealed. The agent is fully autonomous once spawned — this stage ensures it proceeds with confidence, not guesswork.

## Steps

### 1. Load context

Read in parallel:
- `.swc/<folder>/workitems/<N>/requirements.md`
- `.swc/<folder>/workitems/<N>/specs.md`
- `.swc/<folder>/plan.md`
- `.swc/<folder>/architecture.md`
- `.swc/<folder>/notes.md`

`<N>` is the full work item number (e.g. `1.4.2.8`). Resolve `<folder>` via `context-lookup`.

If `requirements.md` or `specs.md` is missing, note the gap but continue with what's available.

### 2. Reuse-first scan

Before thinking forward, check what already exists in the codebase:
- Templates, boilerplate, or scaffold patterns that apply
- Frameworks or conventions already in use for this kind of feature
- In-repo patterns established by similar prior work

State what's being reused and why. Only design from scratch when nothing fits — and if so, note that too.

### 3. Think forward

With context loaded, think through what an implementation agent will encounter for this specific work item:

- Are there existing patterns in the codebase it needs to follow or deviate from?
- Are there integration points where a design call is needed?
- Are there ambiguities in the spec that would require guessing?
- Does this introduce something new (pattern, dependency, architectural concept) not yet settled?
- Are there constraints in `architecture.md` or `notes.md` that create a tension here?

This thinking is internal — do not present it as a list to the user. Use it to determine what, if anything, needs to surface.

### 4. Confirm test approach

TDD is the default: for each scenario in specs.md, the agent writes the test first, implements until it passes, then updates docs before moving to the next scenario.

Assess the work item's complexity. If it's simple (e.g. a small doc update, a single-function change, a config tweak), flag this explicitly:

> "The default approach is scenario-driven TDD — write test, implement, update docs for each scenario. For a work item this size, that may be more ceremony than needed. Do you want to keep the full TDD loop, or would you prefer the agent just implement directly against the spec checklist?"

If the work item is clearly substantial, skip this prompt and record TDD as confirmed without asking.

Options to offer when the work item is simple:
- **Full TDD** — write test per scenario, implement, update docs (default)
- **Lightweight** — implement directly against the spec checklist, no automated test file

Capture the agreed approach — it travels to the agent via solution.md.

### 5. Present findings

**If specific questions or challenges surface:**

Present them concisely — one paragraph or a short bulleted list. Keep it targeted to this work item:

> "Before we seal the brief, a couple of things specific to this work item worth confirming: [questions or challenges]. Want to resolve these now, or are you comfortable leaving it to the agent's judgement?"

Work through each question the user wants to resolve. One at a time. Then move on.

**If no questions surface:**

> "Nothing unresolved on my end — requirements and spec give the agent a clear path."

Then move on.

### 6. Write solution.md

Write to `.swc/<folder>/workitems/<N>/solution.md`:

```markdown
# Solution Design — [work item number]: [work item name]

## Approach

[One paragraph: confirmed approach direction for this work item]

## Test approach

[One of: "Full TDD — write test per scenario, implement, update docs" or "Lightweight — implement directly against spec checklist, no automated test file"]

## Technical decisions

[Bulleted list of questions surfaced and their resolutions. Omit section if none surfaced.]

## Deferred

[Anything explicitly parked — named with enough context to pick up later. Omit section if none.]

## Notes

[Additional guidance for the agent — gotchas, patterns to follow, things to watch for. Omit section if none.]
```

If no questions were surfaced and the user added nothing, keep it minimal:

```markdown
# Solution Design — [work item number]: [work item name]

## Approach

[Confirmed approach direction]

## Test approach

Full TDD — write test per scenario, implement, update docs.

## Technical decisions

No blockers identified. Approach is clear from requirements and specs.
```

### 7. Confirm and proceed

Show the file path and its contents, then ask:
> "Does that capture it? Happy to move to implementation."

Wait for confirmation. Address any corrections, then return control to the calling skill.

## Exit criteria

**Done when:**
- `requirements.md` and `specs.md` loaded
- Technical questions identified (even if the answer is "none found")
- Any surfaced questions resolved or explicitly deferred with reasoning
- `solution.md` written to `.swc/<folder>/workitems/<N>/`
- User confirmed ready to proceed

**Return control to the calling skill.**
