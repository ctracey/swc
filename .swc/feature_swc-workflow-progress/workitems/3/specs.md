# Specs — 3: Find a way to persist a workflow stage definition

## Acceptance criteria

- Running `context-init` results in `workflow-manifest.json` being written to the active context folder (`.swc/<folder>/workflow-manifest.json`)
- `workflow-manifest.json` contains a `workflows` array; each entry has a `name` field and a `stages` array of stage name strings
- All known SWC workflows (deliver, implement, plan) are represented
