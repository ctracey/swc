# Requirements — 1.4.2.9: Add quality baseline to implement stage

## Intent

Add a lightweight pre-flight block to the `swc_workflow_deliver-implement` stage that runs health checks before the agent is spawned. The user sees the current state of the system, decides how to handle any findings, and the decisions are captured in `quality-baseline.md` — which is then included in the agent brief.

The motivation is to prevent the implementation agent from wasting passes diagnosing failures it didn't cause, and to give the user visibility and control over quality issues before committing to implementation.

## Constraints

- Runs in the main session — a human is present for all decisions
- The agent must never encounter an undisclosed pre-existing failure; all known issues and decisions must be in the brief
- `quality-baseline.md` is written by this block and included in the brief assembled by `swc_workflow_deliver-implement`
- Health check commands sourced from `solution.md` (agreed during solution-design) as primary; `architecture.md` as fallback for project-wide harness conventions
- The step is **opt-in** — the user is asked whether to run checks before anything executes; they can skip for simple items where the system state is already known

## Out of scope

- Fixing failures — that is a separate work item or a pre-condition task, decided interactively with the user
- Running the full test suite for unrelated areas; checks should be scoped to the work item area
- A separate stage or stage skill — this lives inside the existing implement stage

## Approach direction

Add a pre-flight block to `swc_workflow_deliver-implement`, before brief assembly and agent spawn:

1. Ask the user: "Want to run a quick health check before spawning the agent?" — skip if no
2. Read `solution.md` for agreed check commands; fall back to `architecture.md`
3. Run the checks
4. Present findings with scope relevance (in-scope vs pre-existing noise)
5. For each failure: user decides — proceed-with-flag or stop (fix first)
6. Write `quality-baseline.md` — commands run, findings, decisions
7. Include `quality-baseline.md` in the agent brief

## Decision log

- **Implement stage, not a separate stage:** a full stage added too much ceremony for what is essentially a pre-flight check. The value is the output (`quality-baseline.md`), not the stage boundary.
- **Opt-in confirmation:** user may already know the system state; forcing checks adds friction for simple items. A single prompt keeps it lightweight.
- **`solution.md` as primary command source:** by the time we reach implement, solution-design has agreed the approach and any relevant check commands. Using those keeps the agent and user on the same playbook.
- **Never fix silently:** if a failure is in scope, the decision is stop (fix first) or proceed-with-flag (user accepts the risk). The agent never patches pre-existing failures without explicit instruction.
- **Commands recorded in `quality-baseline.md`:** so the implementation agent can re-run the same checks during its pass to verify it hasn't introduced new failures.
