# Tech Debt

## [work item 6] — F-01: Python used to parse plugin JSON — 2026-06-11

**Severity:** warn
**Location:** `skills/version/SKILL.md:17-24`
**Description:** Inline `python3 -c` block contradicts the "No Python helpers" requirement. A `jq` one-liner would satisfy the intent without Python.
**Accepted because:** accepted during delivery of 6

## [work item 6] — F-02: python3 call not in settings.json allowlist — 2026-06-11

**Severity:** warn
**Location:** `skills/version/SKILL.md:17` / `.claude/settings.json`
**Description:** The `python3 -c "import json, sys..."` invocation is not in the project-level `settings.json` allowlist. Fresh installers relying on `settings.json` alone will hit a permission prompt.
**Accepted because:** accepted during delivery of 6

## [work item 6] — F-03: context.md missing Python rationale — 2026-06-11

**Severity:** info
**Location:** `context.md`
**Description:** Pass section does not record why Python was used despite the "no Python helpers" requirement — no audit trail for future reviewers.
**Accepted because:** accepted during delivery of 6

## [work item 4] — contexts predating context-initWorkflowManifest have no workflow-manifest.json — 2026-06-11

**Severity:** info
**Location:** `.swc/feature_swc-workflow-progress/` (and any context initialised before work item 3 shipped)
**Description:** `context-initWorkflowManifest` only runs from `context-init`, so existing context folders never get a manifest. Harmless today — the orchestrator's resume path does not read the manifest — but any future consumer (reporting, generic resume) needs a backfill story or a manual re-run of the skill.
**Accepted because:** manifest deliberately kept out of the resume path during work item 4 design

## [work item 3] — F-02: stale manifest recovery not cross-referenced in context-init — 2026-06-11

**Severity:** info
**Location:** `skills/context-init/SKILL.md` step 3
**Description:** The stale-manifest recovery path (re-run the skill manually) is documented only inside `context-initWorkflowManifest`, not visible to callers or users who encounter a mismatch.
**Accepted because:** noted, no action — low impact edge case
