# Requirements — 1.4.2.3: Spawn implementation agent — assemble brief and delegate to swc_implement

## Intent

Add an `implement` stage to the deliver workflow that spawns a fresh implementation agent. The stage confirms the work item, spawns the agent, then evaluates exit criteria and reports the result to the user. The implementation workflow (what the agent actually does) is out of scope for this work item — for now the agent is a placeholder that announces itself and completes without doing any work.

## Constraints

- The spawned agent is told the work item number/name only — it does not receive doc paths. The implementation workflow is responsible for discovering docs via naming conventions.
- Exit criteria are always evaluated and reported to the user — the stage does not silently advance if criteria are unmet.
- The `implement` stage is a new stage in the existing `swc_workflow_deliver` workflow definition (after `specs`).

## Out of scope

- The implementation workflow itself — what the agent does once spawned (covered by 1.4.4)
- Brief assembly logic beyond passing the work item identifier
- Multi-pass support, context.md reading, review findings (future work)

## Approach direction

Three files changed:

1. `skills/swc_workflow-orchestrator/SKILL.md` — update stage gate behavior: when exit criteria are not met, present the unmet criteria to the user and ask how to proceed (re-invoke / skip / stop) rather than auto re-invoking.
2. `skills/swc_workflow_deliver-implement/SKILL.md` — new stage skill: spawns placeholder agent with work item identifier, evaluates exit criteria, reports result.
3. `skills/swc_workflow_deliver/SKILL.md` — add `implement` stage to the workflow definition (after `specs`).

## Exit criteria for the implement stage

The stage reports these criteria to the user after the agent completes:

- Agent completed
- Agent documented its progress
- Summary report of implementation progress exists (based on SWC docs created by the agent)
- Work item implementation is ready for review

Until the implementation workflow is built, none of these will be met. The stage surfaces this explicitly.

## Parked

- Full brief format (work item + approved spec + plan.md + architecture.md + context.md from prior passes + review findings) — defined in notes.md under "Implementation workflow brief format". The placeholder agent ignores this; the real implementation workflow will use it.
- Multi-pass support: `context.md` is append-only across passes — each agent adds a `## Pass N` section. Relevant when the quality loop (1.4.2.4) is built.
