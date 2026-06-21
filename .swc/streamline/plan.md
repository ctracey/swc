# Plan

## Goal

Streamline the SWC deliver workflow's interaction model — reduce conversation friction while
preserving stage structure and governance output.

## Why

The current workflow is process-centric. Agents treat each stage as a ritual to perform in
sequence with uniform thoroughness, regardless of the complexity or obviousness of the work.
This creates friction on simple/standard paths where the answers are obvious — the agent asks
for confirmation rather than acting, and the user has to say "yes" to things they've already
implied by invoking the workflow.

The desired model is outcome-centric: pace calibrates to complexity, interpretation is declared
rather than confirmed for obvious things, and the workflow reaches the review stage quickly so
meaningful feedback happens on real output rather than process.

## Approach

Targeted rewrites of the interaction text in 5 deliver stage SKILL.md files. The core pattern:

- **Confirmations for obvious things become statements** — "Want to go ahead?" → "Starting…"
  Content stays; confirmation asks go.
- **Complexity sets pace** — simple/standard paths move fast; complex/novel paths slow down
  and engage properly. The skill reads the situation and calibrates.
- **State interpretation, don't seek it** — declare assumptions and move on; only ask where
  the answer genuinely branches (testing yes/no, docs angle, non-standard constraints).
- **Reuse-first in solution design** — scan for existing templates, frameworks, in-repo patterns
  before designing anything new. State what's being reused. Design from scratch only when
  nothing fits.

No structural changes, no new skills, no new tools. Pure prompt text changes.

## Core pattern

| Before | After |
|---|---|
| "Want to go ahead?" | "Starting workflow with these stages: …" |
| "Ready to pick up from here?" | "Picking up from here." |
| "Does that capture it?" (after play-back) | *(write the doc and move on)* |
| "Anything else you'd want to clarify?" | *(omit — user will push back if needed)* |
| "Ready to proceed to implementation?" | *(omit — just proceed)* |

**Confirmations for obvious things become reports. Content stays. Gates go.**

Only ask a question where the answer genuinely branches — testing yes/no, docs angle,
non-standard constraints. Everything else: state it and proceed.

## Pace calibration

Complexity determines pace, not the workflow stage.

- **Simple / standard path** — declare assumptions, ask only genuine branch-points, move fast
- **Complex / novel path** — slow down, engage properly, work through the detail

The skill reads the situation and calibrates. It does not apply uniform thoroughness regardless
of what's in front of it.

## Features

### Deliver workflow
1. `workflowDeliver` entry — remove confirmation gates
2. `workflowDeliver_requirements` — declare not confirm; single-pass branch-point questions
3. `workflowDeliver_specs` — remove play-back confirmations; combine lightweight questions
4. `workflowDeliver_solutionDesign` — reuse-first scan; remove depth invite and proceed gate
5. `workflowDeliver_review` — streamline feedback play-back

### Plan workflow
6. `workflowPlan` entry — "Want to go ahead?" → statement
7. `workflowPlan_intent` — remove redundant step 5 confirmation; run report and proceed

### Implement workflow
8. `workflowImplement_implement` — explicit judgment-call guidance (make the call, log as Assumption, keep going); flag assumptions for summary
9. `workflowImplement_summarise` — agent self-heals empty context.md; "approach needs revisiting" lands in summary not as interactive prompt; add Judgment calls section to summary template

## Out of scope

- Stage order and structure — all stages still run in the same sequence
- Governance artifacts — all docs still produced (requirements.md, specs.md, solution.md, etc.)
- The review/accept stage conversation — intentionally stays conversational; it's the right gate
- `workflowPlan_solution`, `workflowPlan_delivery`, `workflowPlan_breakdown`, `workflowPlan_finalise` — assessed and found well-calibrated; no changes needed
- `workflowImplement`, `workflowImplement_orient` — assessed and found clean; no changes needed

## Delivery shape

5 work items, one per skill file. Sequential is fine — each is independent.
