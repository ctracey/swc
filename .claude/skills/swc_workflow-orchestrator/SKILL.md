---
name: swc_workflow-orchestrator
description: Generic workflow orchestrator — drives a user through a sequence of stages defined by the calling workflow skill. Manages progress banner, stage gates, and skill invocation. Use when a workflow skill hands off a workflow definition to run, or when invoked via /swc-workflow-orchestrator.
allowed-tools: Bash, Read, Write, Edit, Glob, Skill
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

### 1. Parse the workflow definition

Read the JSON argument and validate it against the input schema. If it is malformed or fails validation, stop and report the specific violation — do not attempt to run.

### 2. Run stages in order

For each stage in `stages`:

1. **Emit progress banner** — invoke `swc_workflow-progress` with:
   - `title` = workflow title
   - `stages` = comma-separated list of all stage names
   - `active` = current stage name

2. **Invoke the stage skill** — call the skill named in `skill`, passing `args` if provided. Wait for it to return.

3. **Stage gate** — before advancing, evaluate whether the stage skill's own exit criteria have been met by inspecting its behaviour: check that expected outputs are present (e.g. docs written, decisions captured, playback confirmed). Prefer to derive the answer from what the stage skill did — only involve the user if the criteria cannot be determined without their input.

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

4. **Advance** — move to the next stage and repeat.

### 3. Complete

After the final stage returns:

1. Emit a final progress banner with `active=""` (all stages done).
2. If `on_complete` is set, emit that message.
3. Return control to the caller.

## Constraints

- **No workflow logic here.** Stage-specific questions, decisions, and doc writes belong in the stage skills, not this orchestrator.
- **Skipping.** Follow the user's lead — if they indicate a stage can be skipped, surface the stage's exit criteria in a single concise message and confirm they are comfortable proceeding without them. Once confirmed, move on without further challenge.
- **No retrying.** If a stage skill fails, surface the error and stop. The caller decides how to recover.
- **Sequential only.** Stages run one at a time in the order defined.
