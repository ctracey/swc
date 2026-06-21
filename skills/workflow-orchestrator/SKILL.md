---
description: Generic workflow orchestrator — drives a user through a sequence of stages defined by the calling workflow skill. Manages progress banner, stage gates, skill invocation, and resume from recorded progress. Use when a workflow skill hands off a workflow definition to run, or when invoked via /workflow-orchestrator.
allowed-tools: Bash, Read, Write, Edit, Glob, Skill, mcp__swc-workload__list
---

# Workflow Orchestrator

Generic engine for running a multi-stage workflow. Does not contain workflow-specific logic — it drives whatever workflow definition it receives.

## Input

Called by a workflow skill with a JSON workflow definition conforming to this schema:

```json
{
  "type": "object",
  "required": ["title", "stages"],
  "properties": {
    "title": {
      "type": "string",
      "description": "Workflow name displayed in the progress banner (e.g. 'planning', 'execution')"
    },
    "purpose": {
      "type": "string",
      "description": "One-sentence description of what the workflow produces, shown in the confirm-intent prompt (optional)"
    },
    "workItem": {
      "type": "string",
      "description": "Work item ref this run is delivering — plain (`2`) or dotted (`1.4.4.1`) notation. Enables progress recording and resume. Entry skills that know the item MUST pass it (optional only for workflows not tied to an item, e.g. planning)"
    },
    "stages": {
      "type": "array",
      "description": "Ordered list of stages to run",
      "items": {
        "type": "object",
        "required": ["name", "skill"],
        "properties": {
          "name":  { "type": "string", "description": "Stage label used in the progress banner" },
          "skill": { "type": "string", "description": "Skill name to invoke via the Skill tool" },
          "args":  { "type": "string", "description": "Argument string passed to the skill", "default": "" }
        }
      }
    },
    "on_complete": {
      "type": "string",
      "description": "Message emitted to the user after all stages finish (optional)"
    }
  }
}
```

## Behaviour

### 0. Parse the workflow definition

Read the JSON argument and validate it against the input schema. If it is malformed or fails validation, stop and report the specific violation — do not attempt to run.

### 1. Resolve work item and recorded progress

The work item comes from the `workItem` field of the workflow definition — this is the contract; do not rely on inferring it from conversation history. Only if the field is absent, fall back to a work item number explicitly established in session context by the calling entry skill, and say which item you picked up.

If no work item can be resolved either way, emit once (not per stage):
> "Warning: no work item is active for this run — stage progress will not be recorded to the MCP."

Then treat this as a fresh run with no recorded progress and continue to step 2.

If a work item is present:

1. Resolve the workload path via `context-lookup`. This gives the `absolute_path` used for all meta reads and writes in this run. Resolve once; reuse for every stage.
2. Read the item's meta: invoke `mcp__swc-workload__list` with `ref=<workItem>`, `json=true`, and `workload=<absolute_path>`. Extract `items[0].meta.swc.workflowState["<title>"]` — treat as absent if any level is missing.
3. Determine the **resume candidate**:
   - `currentStage` is a non-null stage name → this is an interrupted run; that stage is the resume candidate.
   - `currentStage` is null, the key is absent, or `completed` is true → no resume candidate; this is a fresh run.
4. **Validate the candidate**: if the recorded `currentStage` does not match any `name` in `stages` (e.g. the workflow definition changed since it was recorded), warn the user:
   > "Recorded progress for **[title]** points at stage **'<currentStage>'**, which is not in the current workflow definition. Starting from the beginning unless you tell me otherwise."

   Then treat as a fresh run.

If the meta read fails, warn the user that recorded progress could not be read and treat as a fresh run — do not block the workflow on a read failure.

### 2. Resolve starting stage

**Fresh run** (no resume candidate): render the stage list as a statement and proceed — do not ask for confirmation. For each stage, render its `name` as a bullet with a one-line description of what that stage covers (inferred from the name and your knowledge of the workflow).

> "Running **[title]**[purpose sentence, preceded by a space, if provided]. It covers [N] stages:
> - [stage name] — [one-line description]
> - [stage name] — [one-line description]
> …"

The starting stage is the first stage.

**Resume** (resume candidate found):

Render stages before the candidate with a ✔ prefix and highlight the candidate as the pickup point:

> "**[title]** for work item **[workItem]** has recorded progress — it was last active at stage **'<currentStage>'**:
> - ✔ [earlier stage 1]
> - ✔ [earlier stage 2]
> - ▶ [candidate stage] ← pick up here
> - [later stage] …
>
> Resume at **'<currentStage>'**, or restart from the beginning?"

- **Resume:** the starting stage is the candidate stage.
- **Restart:** the starting stage is the first stage.
- Anything else (e.g. the user names a different stage): follow their lead — set the starting stage accordingly and confirm in one line.

### 3. Run stages in order

Run the stage loop from the starting stage chosen in step 2 to the final stage. Stages before the starting stage are not invoked and get no banner — the recorded progress already covers them.

For each stage:

1. **Emit progress banner** — invoke `workflow-progress` with:
   - `title` = workflow title
   - `stages` = comma-separated list of all stage names
   - `active` = current stage name

2. **Record stage entry** — if `workItem` is present, invoke the `workflow-recordProgress` skill with:
   - `workflow` = workflow title
   - `stage` = current stage name
   - `workItem` = work item ordinal
   - `workload` = resolved workload absolute path

   If the skill's output contains `##WORKFLOW_HALT##`, halt immediately — do not invoke the stage skill.

3. **Invoke the stage skill** — call the skill named in `skill`, passing `args` if provided. Wait for it to return.

4. **Stage gate** — before advancing, evaluate whether the stage skill's own exit criteria have been met by inspecting its behaviour: check that expected outputs are present (e.g. docs written, decisions captured, playback confirmed). Prefer to derive the answer from what the stage skill did — only involve the user if the criteria cannot be determined without their input.

   **If criteria ARE met:** emit a confirmation message in the format `✔ Stage('<stage name>'): <exit criteria met>`. The next stage must not begin until this message has been emitted.

   **If criteria are NOT met:** present the unmet criteria clearly to the user and offer three options:
   > "The following criteria were not met for stage **'<stage name>'**:
   > - [unmet criterion 1]
   > - [unmet criterion 2]
   >
   > How would you like to proceed?
   > 1. **Re-invoke** — run the stage again with a note on what is outstanding
   > 2. **Skip** — advance to the next stage without clearing these criteria
   > 3. **Stop** — halt the workflow here"

   - **Re-invoke:** call the stage skill again, passing a note identifying the outstanding criteria. Evaluate the gate again afterward.
   - **Skip:** treat as user-confirmed skip (see Skipping constraint below) and advance.
   - **Stop:** emit a clear stop message and halt — do not advance to the next stage.

5. **Advance** — move to the next stage and repeat.

### 4. Complete

After the final stage returns:

1. Emit a final progress banner with `active=""` (all stages done).
2. **Record completion** — if `workItem` is present, invoke the `workflow-recordProgress` skill with:
   - `workflow` = workflow title
   - `workItem` = work item ordinal
   - `workload` = resolved workload absolute path
   - `complete` = `true`

   This sets `currentStage` to null and `completed` to true on the workflow's state, so a future session does not mistake a finished run for an interrupted one.
3. If `on_complete` is set, emit that message.
4. Return control to the caller.

## Constraints

- **No workflow logic here.** Stage-specific questions, decisions, and doc writes belong in the stage skills, not this orchestrator.
- **Resume runs through the loop.** Resuming never invokes a stage skill directly outside the stage loop — the starting stage simply moves; banners, progress recording, and gates apply to every stage that runs.
- **Skipping.** Follow the user's lead — if they indicate a stage can be skipped, surface the stage's exit criteria in a single concise message and confirm they are comfortable proceeding without them. Once confirmed, move on without further challenge.
- **No retrying.** If a stage skill fails, surface the error and stop. The caller decides how to recover.
- **Sequential only.** Stages run one at a time in the order defined.
