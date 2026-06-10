# Code Review Findings — 2: Store workflow stage progress via MCP — 2026-06-10

## Summary

The implementation is structurally sound: the new `workflowProgress-record` skill cleanly encapsulates the read-modify-write logic, the orchestrator changes are additive, and all five acceptance scenarios are addressed in the test file. However, two significant gaps prevent the feature from working end-to-end in practice. First, no entry-point workflow (`workflowDeliver`, `workflowImplement`) passes `workItem` to the orchestrator, so the meta write will never fire in real use — the feature is built but not connected. Second, the stop-signal protocol between `workflowProgress-record` and the orchestrator is implicit and undocumented: REQ-04b depends on the orchestrator detecting a halt from a skill's prose output rather than a defined return contract, which is fragile and may silently fail to halt the workflow.

## Findings

### F-01 — error: Entry-point workflows do not pass `workItem` — feature is never triggered

**Severity:** error
**Location:** `skills/workflowDeliver/SKILL.md:92-109`, `skills/workflowImplement/SKILL.md:30-40`
**Description:** Both `workflowDeliver` and `workflowImplement` pass a hardcoded JSON definition to `workflow-orchestrator`. Neither definition includes the `workItem` field added to the orchestrator's schema. As a result the orchestrator will always take the "no work item" branch, emit a warning, and skip every meta write. The feature exists in isolation but cannot be reached from any workflow entry point. The work item number is already resolved and available in both entry-point skills at the point they invoke the orchestrator.
**Suggestion:** Update the JSON definition in `workflowDeliver` step 4 and `workflowImplement` step 2 to include `"workItem": <resolved_item_number>`. For `workflowDeliver` the work item is resolved in step 1; for `workflowImplement` it is extracted in step 1. Both have the value in scope when they construct the orchestrator args.

---

### F-02 — error: Stop-signal contract between skill and orchestrator is undefined

**Severity:** error
**Location:** `skills/workflowProgress-record/SKILL.md:74`, `skills/workflow-orchestrator/SKILL.md:95`
**Description:** The orchestrator says "if `workflowProgress-record` signals a stop, halt the workflow." The skill says emit `"Workflow halted — meta write failed on stage '<stage>'."` and "return control to the orchestrator with a stop signal." There is no defined protocol for what a stop signal is in the Skill invocation model — no return value, no structured output, no named sentinel. The orchestrator must infer halt intent from the skill's prose output. If the model paraphrases the halt message, or if the orchestrator fails to detect it, execution continues into the stage skill in violation of REQ-04b. This is a silent correctness failure — the user will believe the workflow has halted but the stage skill will run anyway.
**Suggestion:** Define an explicit sentinel string that the skill always emits when signalling a stop — for example `WORKFLOW_HALT`. Document this in both the skill and the orchestrator. The orchestrator should explicitly check for that sentinel after the `workflowProgress-record` invocation before proceeding to the stage skill, and note that the sentinel must be emitted verbatim (not paraphrased).

---

### F-03 — warn: `workflowProgress-record` skill name deviates from naming convention

**Severity:** warn
**Location:** `skills/workflowProgress-record/SKILL.md` (folder name)
**Description:** Per `skill--naming`, camelCase encodes a "typed object" (is-a relationship), and `-` encodes an action on that object. `workflowProgress` is not a recognised workflow type in this codebase — the existing banner skill is `workflow-progress` (lower-kebab). The name `workflowProgress-record` implies "record action on workflowProgress typed object," but there is no `workflowProgress` type hierarchy. A more consistent name following the pattern of other utility skills would be `workflow-progress-record` (action chain on the workflow-progress object) or placed as a sub-skill of the object it writes to (`workload-meta-write` or similar).
**Suggestion:** Rename to `workflow-progress-record` to align with the `workflow-progress` banner skill's naming and avoid implying a non-existent typed object hierarchy. This would also make the skill discoverable alongside its peer in a sorted listing.

---

### F-04 — warn: `workItem` field type mismatch between orchestrator schema and actual usage

**Severity:** warn
**Location:** `skills/workflow-orchestrator/SKILL.md:27-30`
**Description:** The orchestrator schema declares `workItem` as `"type": "integer"`. Work item numbers in this codebase are dotted strings like `1.4.4.1` (visible throughout `workflowDeliver`). If a sub-item number is ever passed, the integer constraint will reject it at validation. The orchestrator step 1 validates the definition — a dotted work item number would cause a schema failure and halt the workflow before any stage runs.
**Suggestion:** Change `"type": "integer"` to `"type": ["integer", "string"]` or simply `"type": "string"` with a note that simple item ordinals (e.g. `2`) are passed as strings. Alternatively, document that only top-level integer ordinals are supported by this feature and that sub-item tracking is out of scope.

---

### F-05 — warn: No guard against Python absence in timestamp generation

**Severity:** warn
**Location:** `skills/workflowProgress-record/SKILL.md:47-51`
**Description:** The skill generates the ISO-8601 timestamp by calling `python3` via Bash. If Python is not available in the environment (e.g. a stripped CI container, or Windows without Python on PATH), the Bash call fails silently or produces no output, and the timestamp field in the written meta will be empty or missing. There is no fallback and no error handling at this step.
**Suggestion:** Add a fallback: first attempt `python3`, and if that exits non-zero or produces no output, fall back to the shell `date` command (`date -u +"%Y-%m-%dT%H:%M:%SZ"` on macOS/Linux). Alternatively, since the skill already has `Bash` in allowed-tools, document the assumption that Python is available as an explicit constraint so the failure mode is visible.

---

### F-06 — info: REQ-03 uses "Note:" in output but specs.md specifies a "warning"

**Severity:** info
**Location:** `skills/workflow-orchestrator/SKILL.md:75-77`
**Description:** The orchestrator emits `"Note: no work item is being tracked..."` but specs.md REQ-03 says "a warning is displayed." The distinction matters to the user — a note reads as informational, a warning reads as something that may affect correctness. When no work item is tracked, stage progress is silently dropped and not recoverable, which is closer to a warning-level condition.
**Suggestion:** Change the prefix from `"Note:"` to `"Warning:"` to align with the spec language and signal the appropriate severity to the user.

---

### F-07 — info: Test file scenarios do not cover the read-before-write failure path

**Severity:** info
**Location:** `tests/swc/workflowProgress_meta-write.md`
**Description:** The test scenarios cover five of the five Gherkin acceptance scenarios but do not address the case where the `mcp__swc-workload__list` read (step 1 of `workflowProgress-record`) itself fails. If the read fails, the skill has no current meta to merge against, and proceeding to the write would overwrite existing meta with only the new entry. The failure handling (step 4) only covers the `update` call.
**Suggestion:** Add a scenario: "Meta read fails — skill handles gracefully." Expected: the skill either (a) treats the failed read as empty meta and proceeds (with a visible warning), or (b) applies the same ignore/stop offer as for the write failure. Document the intended behaviour in the skill steps as well.

## Verdict

**BLOCK**

Two error findings: the feature is never reachable from any entry-point workflow (F-01) and the REQ-04b stop-halt mechanism is fragile and undefined (F-02).
