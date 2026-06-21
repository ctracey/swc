# Notes

## Decisions

- **Implement workflow: agent-autonomous, higher bar for stopping.** Judgment calls → make the call, log as Assumption, surface in summary. Hard blockers (3-cycle test failure) still stop the run. The agent self-heals empty context.md rather than prompting the user. "Approach needs revisiting" lands in summary, not as a mid-run interrupt.

- **Plan workflow: 2 changes only.** Most plan workflow confirmation asks are genuine —
  the user is supplying information the agent doesn't have. Only the entry gate and a
  redundant confirmation in `workflowPlan_intent` step 5 are changed. `workflowPlan_solution`
  keeps its report + confirm — solution design is substantive enough to warrant it.

- **Review stage stays conversational.** No friction reduction there — it's the right place to
  slow down and engage. The goal is to get there faster, not to rush through it.

- **No automated tests.** These are prompt text changes. Verification is a manual walkthrough
  of the deliver workflow against a real work item. There's no test harness that can assert
  "the agent declared rather than asked."

- **Content stays, gates go.** Summaries and play-backs are still good interaction. The change
  is removing the confirmation ask at the end of each — state it, write the doc, move on.

## Open questions

- Should workflowImplement stages be assessed for the same pattern?

## Deferred

- workflowImplement interaction assessment
