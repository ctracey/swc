---
description: Define acceptance scenarios and criteria for a work item — document what must be true, not how to test it. Second phase of the delivery conversation. Use when defining acceptance criteria, capturing test scenarios, or when invoked via /workflowDeliver_specs.
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Deliver Specs

Define how the work item will be verified before any implementation begins.

**This stage captures scenarios only — it does not write test code.** The output is a `specs.md` doc describing what must be true. The implementation agent reads this doc and writes the tests.

This stage has two paths — **lightweight** and **full** — chosen based on the complexity of the work item.

---

## Step 1 — Load context

Read from the active context folder:
- `requirements.md` for this work item (`.swc/<folder>/workitems/<N>/requirements.md`) — `<N>` is the **full work item number**, e.g. `1.1`, `2.3`, not just the top-level number
- `plan.md` and `architecture.md` for broader context

Then move to the calibration step.

---

## Step 2 — Calibrate depth

Read the requirements doc for complexity signals. If signals are ambiguous, ask one question:
> "Is this a straightforward change, or are there multiple user paths and edge cases to cover?"

**Choose lightweight path when all of these hold:**
- Single clear path with no meaningful variations
- No input validation or business rule logic
- No state-dependent behaviour
- Outcome is binary — it either works or it doesn't

**Choose full path when any of these apply:**
- More than one valid user path
- Non-obvious error conditions or failure modes
- Input validation or data constraint logic
- State-dependent behaviour
- Implementation is done by an AI agent unsupervised *(almost always true — default to full unless the item is clearly trivial)*

State your choice briefly:
> "This looks [straightforward / complex enough to warrant full specs] — I'll [use a lightweight spec / map out journeys and write EARS requirements]."

If the user pushes back on your choice, adjust without debate.

---

## Lightweight path

For simple, single-path work items.

### L1/L2 — Confirm success and failure cases

Ask one question:
> "What does done look like — what would you check to know this works? And is there anything that should explicitly not happen?"

If no failure cases are raised, skip them.

### L3 — Write lightweight specs doc

Write to `.swc/<folder>/workitems/<N>/specs.md`:

```markdown
# Specs — [work item number]: [work item name]

## Acceptance criteria

- [bullet per verifiable outcome]

## Error cases

- [bullet per explicit failure or non-behaviour — omit section if none]
```

Show the user the file path and its contents, then ask:
> "Does that capture it? Happy to move to solution design."

Wait for confirmation. Address any corrections, then return control to the calling skill.

**Return control to the calling skill.**

---

## Full path

For work items with multiple user paths, validation logic, or non-obvious error conditions.

### F1 — Establish personas

Check whether personas emerged in the requirements conversation. If they did:
> "From requirements, the users involved are: [list]. Does that cover everyone, or are there others?"

If not captured:
> "Who are the users of this feature? For each, what are they trying to achieve?"

For each persona: who they are, their goal, any preconditions. One question at a time.

### F2 — Map user journeys

Walk through paths through the feature. Start with the happy path:
> "Walk me through the primary success scenario — what does the user do, step by step, and what does the system do?"

Once the happy path is captured, probe for other paths:
- **Alternative paths** — other valid routes to the same outcome
- **Non-happy paths** — valid journeys that end without the primary goal (e.g. user cancels)
- **Error paths** — what happens when something goes wrong or input is invalid

For each error path, ask explicitly: "What should the system do when that happens?" Do not let error paths be implicit.

Play back:
> "So we have [N] paths: [list by name]. Does that cover it, or are there edge cases we haven't named?"

### F3 — Write EARS requirements

For each meaningful behaviour in the journeys, write one EARS requirement. Choose the pattern that matches the behaviour:

| Pattern | Keyword | Use when |
|---|---|---|
| Event-driven | `WHEN` | Triggered by a user action or system event |
| State-driven | `WHILE` | Must hold while a condition persists |
| Unwanted behaviour | `IF … THEN` | Error, failure, or invalid input |
| Optional feature | `WHERE` | Behaviour tied to configuration |
| Ubiquitous | (none) | True system-wide invariant — use sparingly |

**For every event-driven or state-driven requirement, write at least one corresponding unwanted behaviour requirement.** Error paths are the most commonly omitted layer.

Each requirement gets a unique ID: REQ-01, REQ-02, etc.

Read them back as a numbered list:
> "Here are the requirements I've derived: [list]."

If anything looks uncertain or incomplete, pause and check. Otherwise proceed to scenarios.

### F4 — Write acceptance scenarios (Gherkin)

For each EARS requirement, write one or more Gherkin scenarios:

```gherkin
# REQ-NN
Scenario: [descriptive name]
  Given [precondition or system state]
  When [trigger or user action]
  Then [expected system response]
  And [additional expected outcomes]
```

Coverage rules:
- Each event-driven requirement → at least one success scenario
- Each unwanted behaviour requirement → one scenario per distinct error condition
- Each validation rule (from F5) → boundary scenarios (just inside valid, just outside)
- One requirement per scenario — do not combine

### F5 — Validation rules (conditional)

Only ask if the work item involves input validation, data constraints, or business rules:
> "Are there rules governing the data or inputs — formats, lengths, allowed values, business logic?"

For each field or input, capture type, required/optional, min/max, business rules.

Each rule implies: one scenario just inside the valid range, one just outside.

Skip this section if no validation logic is present.

### F6 — Write full specs doc

Write to `.swc/<folder>/workitems/<N>/specs.md`:

```markdown
# Specs — [work item number]: [work item name]

## Users and Personas

[For each persona: who they are, their goal, preconditions]

## User Journeys

### Happy path — [name]
[steps]

### [Other path name]
[steps]

## Requirements

REQ-01: [EARS requirement]
REQ-02: [EARS requirement]
…

## Acceptance Scenarios

[Gherkin scenarios grouped by requirement ID]

## Validation Rules

[Table of fields with type, required, rules — omit section if not applicable]

[Business rules as bulleted list — omit if none]
```

Create the `workitems/<N>/` directory if it doesn't exist.

Show the user the file path and its contents, then ask:
> "Does that capture it? Happy to move to solution design."

Wait for confirmation. Address any corrections, then proceed.

**Return control to the calling skill.**

---

## Exit criteria

**Done when:**
- Depth calibrated and path chosen
- `specs.md` written to `.swc/<folder>/workitems/<N>/` via the appropriate path

**Return control to the calling skill.**
