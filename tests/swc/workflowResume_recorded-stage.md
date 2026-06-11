# SWC Workflow Resume — Recorded Stage Pickup Scenarios

Covers the orchestrator's resume-from-recorded-progress behaviour and completion recording. Applies to every workflow that runs through `swc:workflow-orchestrator` (deliver, implement, planning) — scenarios use "deliver" for concreteness.

---

## SCENARIO: Fresh session resumes at the recorded stage

**Setup:** Work item 4 is `in-progress`. Its meta contains
`meta.swc.workflowState.deliver = { currentStage: "implement", completed: false }`.
A new session starts; the user says "let's continue on item 4".

**Trigger:** `workflowDeliver` resolves item 4 and hands the full 7-stage definition, including `workItem: "4"`, to the orchestrator.

**Expected:**
- The orchestrator reads the item meta via `mcp__swc-workload__list(ref=4, json=true)` before any stage runs
- The confirm prompt shows requirements/specs/solution-design ticked (✔) and highlights "implement" as the pickup point, offering resume or restart
- On resume: requirements, specs, and solution-design stage skills are NOT invoked and get no banner
- The stage loop starts at "implement": banner emitted, `workflow-recordProgress` called for "implement", then `workflowDeliver_implement` invoked
- Later stages (refine, review, accept) still run in order with gates as normal

---

## SCENARIO: User chooses restart instead of resume

**Setup:** As above — recorded `currentStage` = `"implement"`.

**Trigger:** At the resume prompt, the user chooses to restart from the beginning.

**Expected:**
- The stage loop starts at "requirements"
- Every stage gets its banner, progress record, and gate as a normal fresh run

---

## SCENARIO: Completed workflow is not offered for resume

**Setup:** Work item 3's meta contains
`meta.swc.workflowState.deliver = { currentStage: null, completed: true }`.

**Trigger:** The deliver workflow is started for item 3 (e.g. after the user reopens it).

**Expected:**
- No resume prompt — the orchestrator presents the standard fresh-run confirm-intent prompt
- The stage loop starts at the first stage

---

## SCENARIO: Final stage completion records workflow completion

**Setup:** Work item 4 is active; the deliver workflow is running its final stage ("accept").

**Trigger:** The "accept" stage returns and its gate passes.

**Expected:**
- The final progress banner is emitted with `active=""`
- `workflow-recordProgress` is invoked with `complete=true` (no stage argument)
- `mcp__swc-workload__update` writes `meta.swc` where:
  - `workflowState.deliver.currentStage` = `null`
  - `workflowState.deliver.completed` = `true`
  - a new entry is appended to `workflowEvents`: `{ workflow: "deliver", event: "completed", timestamp: <ISO-UTC> }`
- Existing `workflowEvents` entries and other workflows' state (e.g. `workflowState.implement`) are unchanged

---

## SCENARIO: New pass after a completed run clears the completed marker

**Setup:** Work item 3's meta contains
`meta.swc.workflowState.implement = { currentStage: null, completed: true }` from an earlier implementation pass. The refine loop spawns a fresh implementation agent for item 3.

**Trigger:** The agent's orchestrator run enters the "orient" stage.

**Expected:**
- No resume is offered (completed run → fresh start at "orient")
- The stage-entry meta write sets `workflowState.implement = { currentStage: "orient", completed: false }`

---

## SCENARIO: Recorded stage no longer exists in the workflow definition

**Setup:** Work item 4's meta records `currentStage: "qa"`, but the current deliver definition has no stage named "qa".

**Trigger:** The orchestrator resolves recorded progress.

**Expected:**
- A warning is shown naming the unmatched stage
- The workflow proceeds as a fresh run (standard confirm-intent prompt, first stage)
- No stage skill is invoked before the user confirms

---

## SCENARIO: Meta read fails — workflow proceeds as fresh run

**Setup:** Work item 4 is active, but the `mcp__swc-workload__list` read errors.

**Trigger:** The orchestrator attempts to resolve recorded progress.

**Expected:**
- The user is warned that recorded progress could not be read
- The workflow is not blocked — it proceeds as a fresh run from the first stage
