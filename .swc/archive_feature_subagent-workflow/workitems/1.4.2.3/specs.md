# Specs — 1.4.2.3: Spawn implementation agent — assemble brief and delegate to swc_implement

## Spec type

Acceptance checklist — verified by walkthrough (skill authoring task, no automated test harness).

## Acceptance criteria

### Orchestrator — stage gate behavior when exit criteria not met

- [ ] Unmet criteria are presented to the user clearly (not just a generic "criteria not met" message)
- [ ] User is offered three options: re-invoke the stage, skip it, or stop the workflow
- [ ] Choosing re-invoke: stage skill is called again with a note identifying what is outstanding
- [ ] Choosing skip: orchestrator advances to the next stage (consistent with existing skip behavior)
- [ ] Choosing stop: workflow halts and a clear stop message is shown to the user
- [ ] When criteria ARE met, existing behavior is unchanged — orchestrator advances without prompting

### Implement stage skill (swc_workflow_deliver-implement)

- [ ] Stage spawns a fresh general-purpose agent with the work item number and name only (no doc paths)
- [ ] The placeholder agent announces it is a placeholder and completes without implementing anything
- [ ] After the agent completes, the stage evaluates and displays all four exit criteria with pass/fail status:
  - Agent completed
  - Agent documented its progress
  - Summary report of implementation progress exists
  - Work item implementation is ready for review
- [ ] All four criteria are reported as unmet (placeholder agent produces no outputs)
- [ ] Stage returns control with unmet status — does not attempt to self-advance

### Deliver workflow definition

- [ ] `swc_workflow_deliver` workflow JSON includes `implement` as a third stage after `specs`
- [ ] Progress banner correctly shows three stages: `requirements → specs → implement`
