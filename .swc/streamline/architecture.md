# Architecture — Streamline Deliver Workflow

## What this change touches

Pure prompt engineering — no code, no new skills, no new tools, no MCP changes.

Nine SKILL.md files in `skills/`:

```
skills/workflowDeliver/SKILL.md
skills/workflowDeliver_requirements/SKILL.md
skills/workflowDeliver_specs/SKILL.md
skills/workflowDeliver_solutionDesign/SKILL.md
skills/workflowDeliver_review/SKILL.md
skills/workflowPlan/SKILL.md
skills/workflowPlan_intent/SKILL.md
skills/workflowImplement_implement/SKILL.md
skills/workflowImplement_summarise/SKILL.md
```

## Constraint

Each file must retain the same stage exit criteria and produce the same governance artifacts.
Only the interaction style changes — what the agent says, when it asks, and whether it waits
for confirmation.

## Change pattern per file

### workflowDeliver/SKILL.md

Three gates → statements:
- Step 2 "Want to go ahead?" → state the stage list and proceed
- `in-progress` "Ready to pick up from here?" → "Picking up from here."
- `not-started` "is that right?" → "Starting work on [N]: [name]."

### workflowDeliver_requirements/SKILL.md

- Step 3: state interpretation, don't invite disagreement up front
- Step 4: declare what's clear; ask branch-point questions in one pass, not one-at-a-time loops
- Step 5: remove standalone confirmation gate — summarise, write doc, proceed
- Step 6: if approach is obvious from context, state it rather than ask "how are you thinking?"
- Step 7: remove second play-back confirmation — write requirements.md, show path, move on

### workflowDeliver_specs/SKILL.md

- Step 1: don't summarise requirements back after loading — proceed straight to calibration
- Lightweight path: combine L1 + L2 into one question
- Full path F6: remove play-back confirmation before writing — write specs.md, show path, move on

### workflowDeliver_solutionDesign/SKILL.md

- New step 2a — reuse-first scan: check existing templates, frameworks, in-repo patterns before
  any forward thinking; state what's reused
- Step 4: remove "Anything else you'd want to clarify?" depth invite
- Step 6: remove "Ready to proceed?" gate — write solution.md, show path, proceed

### workflowDeliver_review/SKILL.md

- Step 7 feedback path: state interpretation of feedback directly; only loop if user corrects it
  (remove "Is that captured correctly?" as a default ask)

### workflowPlan/SKILL.md

- Step 1: remove "Want to go ahead?" — state the stage list and proceed

### workflowPlan_intent/SKILL.md

- Step 5: remove confirmation ask after running swc-report-plan — run the report and proceed;
  step 3 already confirmed intent is right

### workflowImplement_implement/SKILL.md

- Add judgment-call guidance: spec ambiguity or approach choices → make the call, log as
  `- **Assumption:** [what was assumed, should be verified]` in context.md, keep going.
  Do not interrupt the user. These are aggregated in the summary for review.

### workflowImplement_summarise/SKILL.md

- Step 2: if context.md pass section has no entries, agent writes a brief entry itself and
  continues — does not gate on user input
- Step 6: "Approach needs revisiting" → include prominently in summary.md, not as an
  interactive prompt before returning
- Add `### Judgment calls` section to summary.md template — aggregates Assumption entries
  from context.md so they are easy to review at the review stage
