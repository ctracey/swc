# Solution Design — 1.4.4.3: Define the rich summary artifact format

## Approach

Define two artifact formats as canonical entries in `notes.md`: `summary.md` (per work item, written by the implementation agent's Summarise stage) and `pipeline.md` (project-level, agreed during planning). Update the work item artifacts directory listing in notes.md to include both files.

## Technical decisions

- **"Approach needs revisiting" as a named field** — not deferred. It was already identified in notes.md as a signal that should trigger Gate 1; making it an explicit field in the template ensures it's always surfaced rather than buried in prose.
- **Review findings as own section** — not folded into test results. The deliver workflow quality gate reads these distinctly; a separate section keeps them parseable.
- **pipeline.md as a separate file** (not a section in architecture.md) — more visible, easier for the agent to reference as a discrete input to the brief.
- **pipeline.md is project-level only** — no per-work-item overrides. If a work item needs something different, that is a project-level change.
- **Absent pipeline.md is handled gracefully** — agent skips the Pipeline section in summary.md and notes its absence; deliver workflow does not attempt to run checks.

## Deferred

- Updating `swc_init` to stub `pipeline.md` — needs a follow-on
- Updating `swc_workflow_plan-solution` to prompt for `pipeline.md` during planning — needs a follow-on
- Dev server lifecycle management around Gate 3 (start/stop behaviour in the deliver workflow) — separate concern not addressed here
