---
description: Understand the intent behind a piece of work — why it exists, for whom, and what success looks like. Second phase of the planning conversation. Use when exploring motivation and goals, or when invoked via /workflowPlan_intent.
allowed-tools: Read, Write, Edit, Glob
---

# Plan Intent

Understand why this work exists before discussing how to do it. Intent and solution are separate conversations.

## Scope boundary

**Stay in the problem space. Do not drift into tech decisions.**

If the user mentions approach, technology, or implementation details, acknowledge the point and note it — then steer back:
> "Good to know — I'll make note of that. Before we get into how, I want to make sure we've got the 'why' solid first."

Capture any tech mentions as a brief note in `notes.md` under `## Parked (intent phase)` so nothing is lost. But don't pull on the thread — that conversation belongs in `workflowPlan_solution`. Intent is done when you can articulate what success looks like and why it matters, not how it will be built.

## Steps

### 1. Open

> "Before we get into what we're building — what's driving this? What outcome or change are you trying to create?"

### 2. Explore

Calibrate depth to the complexity of the work. For small work items, one or two exchanges is enough. Draw from these selectively — not as a checklist:

- What problem are we solving, and for whom?
- What's the motivation — what's happening now that makes this needed?
- What does success look like? What would be different when this is done?
- Who are the users or personas affected? What are their goals or pain points?
- Are there specific scenarios or user journeys we need to support?
- Are there non-negotiable outcomes — things that must hold true regardless of approach?

### 3. Play back

> "So if I've got this right: [goal], for [who], because [why]. The key outcome is [what changes]. Does that capture it, or is there anything you'd like to clarify or go deeper on?"

Correct and re-confirm if needed. If their answers have been short and direct, move on. If they're elaborating, follow deeper before transitioning.

### 4. Capture

Write to `plan.md`:
- `## Goal / Why` — one paragraph: what this accomplishes and the motivation

If users, personas, or scenarios were discussed, add `## Users and scenarios`.

If constraints were raised, add `## Constraints` to `notes.md`.

### 5. Present and check

Run `swc-report-plan` to show the current state of the plan doc. Then ask:

> "Does that capture what you're going for? Anything to adjust before we move to the solution?"

Wait for confirmation or corrections before transitioning.

Transition: *"Good — now let's talk about how you're thinking of approaching it."*

## Exit criteria

**Done when:**
- `plan.md` has `## Goal / Why` written
- User confirmed the playback is correct

**Return control to `workflowPlan`.**
