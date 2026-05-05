---
description: Understand the solution direction for a piece of work — tech approach, constraints, open questions, and deferred decisions. Third phase of the planning conversation. Use when exploring how to build something, or when invoked via /workflowPlan_solution.
allowed-tools: Read, Write, Edit, Glob
---

# Plan Solution

Explore how to achieve the intent. This is a separate conversation from why — don't conflate goals with approach.

**Do not implement anything in this phase.** This is a design conversation only — no code, no file changes, no commands. Capture decisions in the docs and move on.

## Steps

### 1. Open

> "Now that we know what we're after — do you have a direction in mind for the solution, or would you like to explore options?"

### 2. Explore direction

Depending on the work, cover what's relevant — not all of these:

**Product / UX**
- What does the experience look like? Any sketches, references, or analogies?
- What's the simplest version that delivers the outcome?

**Technical**
- Architectural constraints or preferences?
- Existing patterns in the codebase to follow or avoid?
- Dependencies, integrations, or APIs involved?
- Performance, security, or scalability considerations?

### 3. Surface open questions and deferred decisions

Two distinct categories — name them differently in the docs:

- **Open question** — unresolved; we need to figure this out
- **Deferred decision** — intentionally parked; acknowledged and named, with enough context for a future conversation to pick it up

### 4. Play back

> "So the approach is [direction]. Key constraints are [X]. Still open: [questions]. Sound right?"

### 5. Capture

Write to `architecture.md`:
- `## Tech stack`, `## Folder structure`, `## Constraints`

Write to `notes.md`:
- `## Solution decisions` — key choices made and why
- `## Open questions` — unresolved items
- `## Deferred decisions` — intentionally parked, with context

Update `plan.md`:
- `## Features` — what we're building
- `## Out of scope` — what we're not doing

### 5a. Define the verification pipeline

Ask the user what verification looks like for this project:

> "Before we move on — what does a passing build look like for this project? And is there a dev environment that needs to be running to verify changes? This goes into `pipeline.md` so the implementation agent knows what to run."

Cover:
- **Build** — command to run, what a passing outcome looks like
- **Dev environment** — start command, how to confirm it's up, stop command (or "not applicable")
- **Acceptance** — what the human needs to see to accept the work (can be "test suite only" for non-UI work)

Write the answers to `.swc/<folder>/pipeline.md`. The stub is already there from `context-init` — fill it in with what was agreed. If the user wants to skip or fill it in later, leave the stub as-is and note it as a deferred decision.

### 6. Present and check

Run `swc-report-plan` and `swc-report-notes` to show the current state of the plan and decisions. Then ask:

> "Does that reflect the approach we've agreed? Anything missing or off before we move on?"

Wait for confirmation or corrections.

Transition: *"Good — before we get into individual work items, let's talk about how you see this unfolding."*

## Exit criteria

**Done when:**
- `architecture.md` has Tech stack, Folder structure, Constraints
- `notes.md` has Solution decisions, Open questions, Deferred decisions
- `plan.md` has Features and Out of scope
- `pipeline.md` filled in or deferred decision recorded
- User confirmed the playback is correct

**Return control to `workflowPlan`.**
