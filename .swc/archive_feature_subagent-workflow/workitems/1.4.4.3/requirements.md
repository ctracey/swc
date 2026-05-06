# Requirements — 1.4.4.3: Define the rich summary artifact format

## Intent

Define two artifact formats that together make it easy for the human to accept or reject work at Gate 3:

1. **`pipeline.md`** — a project-level doc agreed during planning that captures what verification looks like for this project: passing build, working dev environment, and what the human needs to see. Agreed once per project; not reinvented per work item.

2. **`summary.md`** — the implementation agent's per-pass handoff artifact. Reports against whatever the pipeline artifact defines. Contains: summary of changes, what was tested, test results, build confidence, and pipeline verification result. Designed for human acceptance — easy to read and act on at Gate 3.

The formats are captured as canonical definitions in `notes.md` (same pattern as the context.md format definition). The summarise stage skill will implement against these definitions in 1.4.4.4.

## Constraints

- Not web-app biased — `pipeline.md` captures project-specific verification so `summary.md` stays generic
- `pipeline.md` is project-level only — no per-work-item overrides
- `summary.md` travels intact from the implementation agent to the deliver workflow — the agent does not editorially filter it
- Format definitions are docs, not code — output is `notes.md` entries and a `pipeline.md` stub template

## Out of scope

- Building the summarise stage skill (1.4.4.4)
- Updating `swc_workflow_plan-solution` to prompt for `pipeline.md` (follow-on)
- Per-work-item pipeline overrides

## Approach direction

Define both formats as canonical entries in `notes.md`. For `pipeline.md`: define the template and note it lives in `.swc/<folder>/` alongside `plan.md`, stubbed by `swc_init`, filled during `swc_workflow_plan-solution`. For `summary.md`: define the template and note it lives in `.swc/<folder>/workitems/<N>/`, written by the summarise stage.

## Parked

- `swc_init` needs updating to stub `pipeline.md` — out of scope here, flagged for follow-on
- `swc_workflow_plan-solution` needs a prompt to fill in `pipeline.md` during planning — out of scope here, flagged for follow-on
- Dev server lifecycle (start/stop around Gate 3) — the pipeline artifact defines *what* to run; the deliver workflow behaviour around running it is a separate concern not addressed here
