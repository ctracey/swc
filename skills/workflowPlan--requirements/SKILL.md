---
description: BA requirements lens for planning — surface stakeholder, journey, scope, and NFR questions within Intent and Solution stages. Always relevant during workflowPlan stages.
allowed-tools: Read
---

# Requirements Lens — Planning

Apply within the existing planning stages. Not a sequential checklist — a set of gaps to close before design begins.

## Intent stage

If these haven't emerged naturally, surface them:

- **Who** — who uses this, who is affected, who needs to approve?
- **Journey** — is there a flow this sits within? Who does what, in what order, to achieve what outcome?
- **Problem** — what's broken or missing today?
- **Success** — what does good look like? Is there a measurable outcome?
- **Scope edges** — what is explicitly not included?

## Solution stage

Once intent is confirmed, ensure these are addressed before breakdown:

- **NFRs** — performance, security, compliance, accessibility constraints?
- **Assumptions** — what are we treating as given that could be wrong?
- **Dependencies** — what does this touch, and what depends on it?
- **Risks** — what could derail delivery?

## Capture

These belong in `plan.md`, not work items. Per-item requirements are handled during delivery (`workitems/<N>/requirements.md`).

Unanswered items → park explicitly in `plan.md` with enough context to pick up later.
