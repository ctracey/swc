# Summary — 6: Add version skill to the swc plugin

## Pass 1 — 2026-06-11

### Changes

- Created `skills/version/SKILL.md` — new `/version` skill that reads the SWC plugin version from `.claude-plugin/plugin.json` via Bash, calls `mcp__swc-workload__version` for MCP and CLI versions, and emits a single pipe-delimited line `SWC: <v> | MCP: <v> | CLI: <v>`. Any unresolvable value shows `MISSING`.

### Testing

No automated tests — Lightweight approach. Verified by checklist against all acceptance criteria in specs.md:
- Pipe-delimited output format specified in Step 3 of SKILL.md
- SWC version read from `.claude-plugin/plugin.json` field `version` via `${CLAUDE_SKILL_DIR}/../../.claude-plugin/plugin.json`
- MCP and CLI versions from `mcp__swc-workload__version` fields `mcp` and `cli`
- MISSING fallback on any read failure — both Bash path and MCP path guarded
- Path verified by manual Bash run with CLAUDE_SKILL_DIR set to skills/version/ — returned 1.1.0

### Test results

No automated tests — verified by acceptance checklist. All 4 criteria satisfied. Path resolution verified by manual Bash run (exit 0, output 1.1.0).

### Pipeline

pipeline.md present but contains only stub template text — no real build command defined. Pipeline verification skipped.

### Build confidence

High — the skill is a single markdown instruction file with two straightforward steps (one Bash read, one MCP call). Both sources confirmed working in-session. No regressions possible in a new-file-only change.

### Scope flags

None.

### Approach needs revisiting

No.
