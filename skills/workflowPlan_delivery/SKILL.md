---
description: Understand the delivery shape — phases, milestones, and priorities. What lands first and why. Fourth phase of the planning conversation. Use when discussing rollout, sequencing, or priorities, or when invoked via /workflowPlan_delivery.
allowed-tools: Read, Write, Edit, Glob, Bash
---

# Plan Delivery

Get a sense of the high-level shape before breaking into work items. Brief — a couple of questions at most.

## Steps

### 1. Open

> "Before we break this into work items — how do you see this unfolding? Are there phases, milestones, or a particular order you have in mind?"

### 2. Listen for the shape

Probe gently for the pattern the user has in mind:

| Shape | What it sounds like |
|---|---|
| Feature maturity | "Get the basics working, then add X, then polish" |
| Learning-driven | "Validate X before committing to Y" |
| Staged rollout | "MVP first, then layer in the full thing" |
| Dependency-ordered | "Can't do B until A is in place" |
| Priority-first | "The most important thing is X — everything else can wait" |

Don't categorise it — just understand what the user considers high priority and whether there are natural phases.

### 3. Play back

> "So the shape looks like: [summary]. The most important thing to land first is [X]. That right?"

### 4. Capture

Add `## Delivery shape` to `plan.md` with 2–4 bullets summarising phases and priorities.

Write a skeleton workload to `.swc/<folder>/workload.md` — one top-level work item per phase or priority area identified, no sub-items yet. This gives a starting shape for the detailed breakdown.

### 5. Present and check

Run `swc-list` to show the skeleton. Then ask:

> "Here's the rough shape as work items. Does this ordering and grouping look right before we break it down further?"

Wait for confirmation or adjustments.

Transition: *"Good — let's figure out how to break it down."*

## Exit criteria

**Done when:**
- `plan.md` has `## Delivery shape`
- Skeleton workload written to `.swc/<folder>/workload.md`
- User confirmed the ordering and grouping

**Return control to `workflowPlan`.**
