# Requirements — 3: Find a way to persist a workflow stage definition

## Intent

Provide a durable, session-independent source of workflow stage definitions so a fresh session can reconstruct the full stage list for any workflow without hardcoding or MCP meta inspection. A new `context-initWorkflowManifest` skill generates `workflow-manifest.json` in the active context folder by having the model produce the JSON from its knowledge of available workflows and their stages. `context-init` delegates to this skill as a final step.

## Constraints

- `context-init` must not be significantly changed — delegation only (one added step).
- The manifest is a snapshot at init time; staleness from workflow changes after init is an accepted edge case.
- The manifest is written to the context folder (`.swc/<folder>/`), not to MCP meta.

## Approach direction

The skill prompts the model to generate a JSON object with a `workflows` collection — each entry has a `name` and a `stages` array of stage names. The output is written to `workflow-manifest.json`. No file scanning or sidecar files required.
