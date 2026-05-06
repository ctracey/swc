# Specs — 1.4.2.5: Gate 3 — human review handoff

## Users and Personas

**Developer** — the person running the delivery workflow for a work item they want to ship. Goal: review what was built and either accept it or provide feedback for a change. Precondition: refine stage has completed and `summary.md` exists.

## User Journeys

### Happy path — developer accepts the work
1. Review stage opens — loads `summary.md`, `code-review-findings.md`, `pipeline.md`
2. Presents: implementation changes, QA evidence (as reported by agent), review findings (resolved + deferred)
3. If `pipeline.md` defines a dev server, offers to run it
4. Developer indicates satisfaction
5. Stage returns control — orchestrator advances to commit/push

### Feedback path — developer wants a change
1. Same presentation as happy path
2. Developer provides feedback describing what needs to change
3. Stage plays back the feedback, confirms with developer
4. Writes `feedback.md` to work item folder (replacing any existing file)
5. Re-launches delivery workflow for same work item — requirements stage opens with feedback as pre-loaded context

### Precondition failure — summary.md missing
1. Review stage opens — `summary.md` not found
2. Stage surfaces the missing precondition and stops

### Dev server declined
1. Dev server is offered (pipeline.md defines one)
2. Developer skips the offer
3. Stage proceeds to the review decision without running the server

## Requirements

REQ-01: WHEN the review stage starts, the system SHALL load `summary.md` (latest pass), `code-review-findings.md`, and `pipeline.md` from the active work item folder.

REQ-02: IF `summary.md` does not exist at the expected path, THEN the system SHALL surface the missing precondition and stop without presenting the review.

REQ-03: WHEN presenting the review handoff, the system SHALL display implementation changes, QA evidence as reported by the implementation agent (test results, scenarios covered, build and server status, new tests added), and code review findings (resolved and deferred).

REQ-04: The system SHALL NOT re-run tests, builds, or pipeline checks — all QA evidence is sourced from agent-reported artifacts only.

REQ-05: WHEN `pipeline.md` defines a `Dev environment` section with a start command, the system SHALL offer to run the dev server before the developer makes their review decision.

REQ-06: WHEN the developer indicates satisfaction, the system SHALL return control to the orchestrator to advance to the next stage.

REQ-07: WHEN the developer provides feedback requesting a change, the system SHALL play back the feedback and ask the developer to confirm it is captured correctly.

REQ-08: WHEN the developer confirms their feedback, the system SHALL write the feedback to `feedback.md` in the work item folder (replacing any existing file) and re-launch the delivery workflow for the same work item starting at the requirements stage.

## Acceptance Scenarios

```gherkin
# REQ-01
Scenario: Review stage loads all required artifacts
  Given the review stage has been invoked for work item N
  And summary.md exists at .swc/<folder>/workitems/N/summary.md
  When the review stage starts
  Then it reads summary.md (latest pass), code-review-findings.md, and pipeline.md

# REQ-02
Scenario: Missing summary.md stops the review
  Given the review stage has been invoked for work item N
  And summary.md does not exist at .swc/<folder>/workitems/N/
  When the review stage starts
  Then the system surfaces the missing precondition clearly
  And stops without presenting any review content

# REQ-03
Scenario: Review handoff presents full evidence
  Given the review stage has loaded all artifacts
  When the handoff is presented to the developer
  Then the system displays implementation changes from the latest summary pass
  And QA evidence as reported by the agent (test results, scenarios covered, build and server status, new tests added)
  And code review findings showing what was resolved and what was deferred to tech-debt

# REQ-04
Scenario: Review stage does not re-run pipeline
  Given the review stage is presenting the handoff
  When QA evidence is displayed
  Then the evidence is sourced from agent-reported artifacts only
  And no test, build, or pipeline commands are executed

# REQ-05
Scenario: Dev server offered when pipeline.md defines one
  Given pipeline.md exists with a Dev environment section containing a start command
  When the review handoff is presented
  Then the system offers to run the dev server before asking for the review decision

Scenario: Dev server not offered when pipeline.md has no Dev environment
  Given pipeline.md does not define a Dev environment section
  When the review handoff is presented
  Then no dev server offer is made

Scenario: Dev server not offered when pipeline.md is absent
  Given pipeline.md does not exist in the workload folder
  When the review handoff is presented
  Then no dev server offer is made

Scenario: Developer declines dev server offer
  Given the system has offered to run the dev server
  When the developer declines
  Then the system proceeds to the review decision without running the server

# REQ-06
Scenario: Developer accepts the work
  Given the review handoff has been presented
  When the developer indicates satisfaction
  Then the system returns control to the orchestrator
  And the orchestrator advances to the next stage

# REQ-07
Scenario: Developer provides feedback — playback and confirmation
  Given the review handoff has been presented
  When the developer provides feedback requesting a change
  Then the system plays back the feedback in a clear summary
  And asks the developer to confirm it is captured correctly

Scenario: Developer corrects the playback
  Given the system has played back feedback
  When the developer indicates the playback is incorrect
  Then the system accepts the correction and updates the feedback
  And plays back the updated feedback for confirmation

# REQ-08
Scenario: Confirmed feedback triggers write and re-launch
  Given the developer has confirmed the feedback is correct
  When the system processes the confirmed feedback
  Then it writes the feedback to feedback.md in the work item folder
  And any existing feedback.md is replaced
  And the delivery workflow is re-launched for the same work item
  And the delivery workflow opens at the requirements stage
```
