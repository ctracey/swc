# Requirements — 1.4.2.5: Gate 3 — human review handoff

## Intent

Build the `review` stage of the delivery workflow — the final human review handoff that completes the delivery loop. After the refine stage clears quality, the review stage presents the full implementation picture so the human can answer "Did we build the right thing?" This is distinct from code quality (handled by refine) — it's a correctness and satisfaction check. The stage surfaces the implementation summary, QA evidence as reported by the implementation agent, and an offer to run the dev server if the project defines one. The human either accepts the work (advancing to commit/push) or provides feedback that triggers a seamless replay of the delivery workflow from requirements.

## Constraints

- Surface QA evidence as reported by the implementation agent — do not re-run tests, builds, or pipeline checks
- The feedback loop must be seamless — the user gives feedback inline and the workflow re-launches automatically, no manual re-invocation
- Feedback from the user is written to `feedback.md` before the workflow re-launches, so the requirements stage can pick it up as existing context on re-entry

## Out of scope

- Commit and push (1.4.2.6)
- Work item status updates during delivery (1.4.2.7)
- Re-running tests, pipeline, or build commands

## Approach direction

New skill `swc_workflow_deliver-review`, added as the 6th stage in `swc_workflow_deliver`'s stage list (after `refine`). On feedback, the skill writes a `feedback.md` artifact to the work item folder and re-invokes `swc_workflow_deliver` with the work item as argument. The requirements stage already checks for existing task docs and will surface `feedback.md` naturally on re-entry. Dev server offer is driven by reading `pipeline.md`.

## Parked

- Whether the "offer to run dev server" should run the server inline (blocking) or give the user a command to run in a separate terminal — to resolve in solution-design
- Whether `feedback.md` is cumulative (appends across feedback rounds) or replaced each time — to resolve in specs
