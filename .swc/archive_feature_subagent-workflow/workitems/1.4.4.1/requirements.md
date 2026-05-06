# Requirements — 1.4.4.1: Define the implementation workflow

## Intent

Define the step-by-step workflow the implementation agent follows autonomously inside its own session. The design is largely captured in notes.md and plan.md; this work item consolidates it, fills any gaps, and produces an agreed design document that serves as the foundation for 1.4.4.2 (context.md format), 1.4.4.3 (summary artifact format), and 1.4.4.4 (building the SKILL.md). Output is a design document in this workitem folder — not the skill itself.

## Constraints

- The agent is fully autonomous — no mid-execution user interaction is possible
- Spec-driven: agent implements against an approved spec; done = spec passes
- context.md is append-only across passes — never overwritten
- The agent stops only when genuinely blocked (no reasonable forward path within the agreed brief)
- The agent starts with a clean quality picture — pre-existing failures and scope decisions are captured in `quality-baseline.md` (written by the deliver workflow) and included in the brief; the agent does not make its own judgements about pre-existing issues
- One work item per agent run — the agent executes it fully and stops; it does not proceed to the next item
- The summary artifact travels intact to the deliver workflow — the agent does not assess its own output beyond what Refine covers

## Out of scope

- Building the SKILL.md (that is 1.4.4.4)
- Detailed context.md section format (that is 1.4.4.2)
- Detailed summary artifact format (that is 1.4.4.3)
- The quality baseline stage itself (that is 1.4.2.9) — it runs in the deliver workflow before the agent is spawned

## Approach direction

Consolidate the workflow design already documented in notes.md and plan.md, surface any gaps or unresolved questions, and confirm the agreed design with the user. Output is captured as a design doc in `.swc/<folder>/workitems/1.4.4.1/`.

The implementation workflow follows the same orchestrator pattern as the deliver workflow: a top-level entry skill (`swc_workflow_implement`) defines the stage list and delegates to `swc_workflow-orchestrator`. Each stage has its own skill file. The agent discovers its own context — `swc_workflow_deliver-implement` passes only the work item number and workload folder path.

## Agreed stages

The implementation workflow has four stages:

1. **Orient** — read the full brief (work item, requirements.md, specs.md, solution.md, quality-baseline.md, prior context.md passes, review findings); understand the starting point and what this pass needs to accomplish; open a new pass section in context.md

2. **Implement** — work against the approved spec; document decisions in context.md as work happens (not batched at the end); flag scope observations as they arise; inner loop: implement → run spec → fix → repeat until spec passes or genuinely blocked

3. **Refine** — spawn `code-reviewer` subagent once; receive structured findings; apply fixes; re-run spec to confirm still passing; surface any remaining findings in the summary artifact for the deliver workflow quality gate

4. **Summarise** — complete the context.md pass section (scope flags, open questions, remaining review findings); write the summary artifact; return to the calling skill

## Decision log

- **No baseline stage in implementation workflow:** quality baseline moved to the deliver workflow (1.4.2.9) so a human is present when failures are found. The implementation agent receives decisions already made — it does not diagnose or decide on pre-existing failures.
- **Orient before implement:** orient gives the agent full context before any work begins, including quality-baseline.md decisions.
- **Execute and verify collapsed into Implement:** a tight inner loop — the agent does not "implement everything, then verify." The exit condition for Implement is spec passes.
- **Refine spawns code-reviewer subagent:** self-review alone is insufficient; a fresh subagent provides independent quality assessment. Refine runs the reviewer once — remaining findings surface in the summary rather than looping internally. The deliver workflow quality loop handles second-pass remediation.
- **Summarise is a distinct stage:** writing context.md and the summary artifact is a named commitment, not an afterthought. This enforces the R3 resolution — the agent cannot return without completing this stage.
- **One work item per run:** from swc_execute — the agent executes a single work item fully and stops. It does not proceed autonomously to the next item.
- **Summary artifact travels intact:** the agent does not editorially assess its own output. What the Refine stage surfaces is what the deliver workflow sees.
- **Orchestrator pattern for implementation workflow:** the implementation workflow uses the same `swc_workflow-orchestrator` + per-stage skill structure as the deliver workflow. This gives consistent progress banners, stage gates, and skip/stop options. Stage skills are independently invocable.
- **Agent discovers its own context:** `swc_workflow_deliver-implement` passes only the work item number and workload folder path. The agent (via `swc_workflow_implement`) reads all docs itself. This keeps the spawning skill simple and makes the implementation workflow self-contained.
