# Code Review Findings — 6: Add version skill to the swc plugin — 2026-06-11

## Summary

The implementation is a small, well-structured skill file that satisfies all four acceptance criteria from specs.md: the pipe-delimited output format is correct, both version sources are read as specified, and error handling falls back to `MISSING` per source independently. The file is concise and within all complexity limits. One meaningful concern is present: the implementation uses an inline `python3 -c` block, which contradicts the explicit "No Python helpers" instruction in requirements.md. This also means the specific `python3 -c` invocation is not covered by the project-level `settings.json` allowlist, meaning first-run users without a wildcard local override will face a permission prompt. The deviation is not documented in context.md.

## Findings

### F-01 — WARN: Inline python3 contradicts explicit "No Python helpers" requirement

**Severity:** warn
**Location:** `skills/version/SKILL.md:17-24`
**Description:** requirements.md states "No Python helpers — two calls, one output." The implementation uses an inline `python3 -c` block to parse `plugin.json`. While "Python helpers" most likely refers to separate `.py` files (like the one in `skills/workflow-progress/`), the phrase is unambiguous enough that any Python use warrants justification. The context.md pass section does not acknowledge or explain the deviation. A jq-based approach (`jq -r '.version // "MISSING"' "${CLAUDE_SKILL_DIR}/../../.claude-plugin/plugin.json" 2>/dev/null || echo "MISSING"`) would satisfy the requirement literally and is available on the host (`/usr/bin/jq`).
**Suggestion:** Either replace the `python3 -c` block with a `jq` one-liner to align with the requirement, or add a note to context.md explaining why inline Python is acceptable here (e.g., "No Python helpers means no external .py files; inline -c is acceptable for portability"). If the jq path is taken, add a `|| echo "MISSING"` guard for the case where `jq` is unavailable.

### F-02 — WARN: python3 -c command not covered by project settings.json allowlist

**Severity:** warn
**Location:** `skills/version/SKILL.md:17` / `.claude/settings.json`
**Description:** The project `settings.json` allows only two `python3` invocation patterns: scripts under the installed plugin path, and one specific `python3 -c "import sys,json; ..."` command. The `python3 -c "import json, sys\ntry: ..."` block in the new skill matches neither. The user's `settings.local.json` has a blanket `Bash(python3 *)` permission that covers it in practice, but any user who installs this plugin using only `settings.json` (the documented, project-scoped file) will receive a permission prompt on first use of the skill.
**Suggestion:** If the inline Python approach is kept, add a corresponding `Bash(python3 -c *)` entry to `settings.json` — or add the specific invocation as a documented permission in `setup-permissions` so users are guided to allow it during setup.

### F-03 — INFO: context.md does not document the Python approach deviation

**Severity:** info
**Location:** `.swc/feature_swc-workflow-progress/workitems/6/context.md`
**Description:** The three decisions recorded in context.md cover path resolution, null-cli handling, and the lightweight test approach. The choice to use `python3 -c` — which deviates from the requirement wording — is not noted or justified. This makes it harder for a future reviewer to understand why the Python approach was chosen.
**Suggestion:** Add a decision entry such as: "Decision: Used inline `python3 -c` rather than `jq` for JSON parsing — `python3` is always available in the Claude Code environment (macOS/Linux); `jq` requires verification. 'No Python helpers' interpreted as no external .py files."

## Verdict

**WARN**

Two `warn`-level findings: the implementation deviates from the "No Python helpers" requirement without documenting the reason, and the resulting `python3 -c` invocation is not covered by the project-level permissions allowlist.
