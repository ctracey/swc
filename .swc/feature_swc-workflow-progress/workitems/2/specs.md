# Specs — 2: Store workflow stage progress via MCP

## User Journeys

### Happy path — stage advance
Orchestrator advances to a new stage. Work item is active in session context. Meta is updated with the current workflow and stage, and a history entry is appended. Stage skill is then invoked as normal.

### Loopback — re-entry of earlier stage
A feedback loop causes the orchestrator to re-enter a stage that was previously active. The meta write fires again, updating `currentStage` and appending a new history entry. Prior entries in the history are preserved.

### No active work item
Orchestrator is running without a work item in session context (e.g. a demo or standalone workflow). A warning is displayed to the user. Stage skill is invoked as normal — no meta write attempted.

### Meta write failure
The MCP call to write meta fails. The user is informed and offered a choice: ignore and continue, or stop to fix.

---

## Requirements

REQ-01: WHEN the orchestrator advances to a new stage AND a work item is active in session context, the system SHALL update `meta["swc-workflow-status"]` with the current workflow name and stage name, and append an entry to the stage history.

REQ-02: WHEN the orchestrator re-enters an earlier stage following a loopback AND a work item is active in session context, the system SHALL update `meta["swc-workflow-status"]` with the current stage and append a new history entry, preserving all prior entries.

REQ-03: IF no work item is active in session context WHEN a stage starts, THEN the orchestrator SHALL display a warning and invoke the stage skill as normal.

REQ-04: IF the MCP meta write fails WHEN a stage starts, THEN the orchestrator SHALL inform the user and offer: (1) ignore and continue, or (2) stop to fix.

---

## Acceptance Scenarios

```gherkin
# REQ-01
Scenario: Stage advance records workflow, stage, and history entry
  Given a work item is active in session context
  And the workflow "deliver" is running
  When the orchestrator advances to stage "specs"
  Then meta["swc-workflow-status"]["workflow"] is set to "deliver"
  And meta["swc-workflow-status"]["currentStage"] is set to "specs"
  And a history entry for stage "specs" is appended to meta["swc-workflow-status"]["history"]
  And the stage skill is invoked after the meta write

# REQ-02
Scenario: Loopback to earlier stage appends new history entry without losing prior entries
  Given a work item is active in session context
  And the workflow has previously advanced through "requirements" and "specs"
  And meta["swc-workflow-status"]["history"] contains entries for both prior stages
  When the orchestrator re-enters stage "requirements" following a loopback
  Then meta["swc-workflow-status"]["currentStage"] is set to "requirements"
  And a new history entry for "requirements" is appended
  And the prior history entries for "requirements" and "specs" are preserved

# REQ-03
Scenario: No active work item — warning shown, workflow continues
  Given no work item is active in session context
  When the orchestrator advances to any stage
  Then a warning is displayed indicating no work item is being tracked
  And the stage skill is invoked as normal
  And no MCP call is made

# REQ-04a
Scenario: Meta write fails — user ignores and continues
  Given a work item is active in session context
  When the MCP meta write fails
  Then the user is informed of the failure
  And offered the choice to ignore and continue or stop to fix
  And if the user chooses ignore, the stage skill is invoked as normal

# REQ-04b
Scenario: Meta write fails — user stops to fix
  Given a work item is active in session context
  When the MCP meta write fails
  Then the user is informed of the failure
  And offered the choice to ignore and continue or stop to fix
  And if the user chooses stop, the workflow halts and does not invoke the stage skill
```
