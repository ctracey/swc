# Requirements — 1.4.2.8: Add solution design stage to deliver workflow

## Intent

The deliver workflow currently has three stages: requirements → specs → implement. The implementation agent is fully autonomous once spawned and cannot ask the user anything mid-run. Any unresolved implementation-level question becomes either a silent deviation or a stuck agent. This work item adds a `solution-design` stage between specs and implement. Before the brief is sealed, the skill reads requirements + specs, thinks forward through what the agent will encounter for this specific work item, and surfaces any targeted technical questions or challenges — new patterns to decide on, integration decision points, architectural ambiguities. The user resolves those. The outcome is captured in `solution.md` and referenced in the agent brief.

## Constraints

- Stage must scale to complexity — if no questions surface, the stage should be fast (confirm and move on)
- Do not over-elaborate: this is targeted foresight, not a design session
- The agent brief references `solution.md` by path only — does not inline its contents
- Even when no blockers are found, `solution.md` must be written (signals the stage was considered, keeps brief reference consistent)

## Out of scope

- General approach agreement (that belongs in requirements)
- Acceptance criteria (that belongs in specs)
- Deep technical design sessions unless the user explicitly wants to go there

## Approach direction

New skill `swc_workflow_deliver-solution-design/SKILL.md` following the existing `swc_workflow_deliver-*` naming pattern. Update the workflow JSON in `swc_workflow_deliver/SKILL.md` to insert the new stage between specs and implement. Add `solution.md` as a path reference in the brief assembly section of `swc_workflow_deliver-implement/SKILL.md`.

## Parked

- Gentle depth offer: the stage should invite the user to go deeper on tech specifics, but default to directional if they don't push back — implement as a soft "want to go deeper?" rather than a forced conversation
