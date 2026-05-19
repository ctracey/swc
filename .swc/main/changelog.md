# Changelog

## Session — WI-3.2 phase 1 delivery: workload CLI `2026-05-19`

- Delivered phase 1 of work item 3.2 — two-tier CLI in `cli/`:
  - `swc` (wrapper): top-level command. Resolves current branch → workload folder via `.swc/_meta.json`. Owns `init` (creates folder + writes mapping + forwards) and top-level `exists` (branch-aware, integrity-checking presence check with init recovery hint on broken states).
  - `swc_workload` (backend): pure path-driven tree manager. Takes `--workload <folder>` on every op. Knows nothing about git or `_meta.json`. Implements all 14 ops: `init`, `add`, `remove`, `rename`, `reorder`, `move`, `status`, `list`, `show`, `find`, `summary`, `read`, `exists`, `complete?`.
- 105 scenario tests across two tiers (`tests/cli/test_swc_*` end-to-end via wrapper; `tests/cli/test_swc_workload_*` direct against the backend with tmp paths). Covers REQ-01..REQ-25, REQ-28..REQ-31 from `specs.md`.
- 10 implementation passes captured in `summary.md` / `context.md`. Code-review verdict on final pass: PASS.
- Tech-debt items recorded: F-05 (hash-vs-digit number ref ambiguity ~6/100M), F-06 (file size at ~945 lines — natural split point comes with 3.3's plugin extraction).
- Motivation: consolidate all workload ops behind a single CLI so skills no longer hand-edit `workload.md`. Decouples item identity (stable hash IDs) from numbering (computed at render time) so docs survive renumbering and re-parenting.

### Phase 1 of 3 — remaining phases (gated on user signal)

- **Phase 2 — skill migration**: convert the 15 skills currently editing `workload.md` directly (`workload`, `workload-update`, `workload_item-start`, `ship`, `context-init`, `context-lookup`, `context--workload`, `workflowPlan_context`, `workflowPlan_delivery`, `workflowPlan_breakdown`, `workflowPlan_finalise`, `workflowDeliver`, `workflowDeliver_implement`, `workflowDeliver_refine`, `workflowImplement_orient`) to shell out to `swc workload <op>`. Includes a manual `.md` → `.json` migration of existing workloads (`swc workload init` per workload, item re-add).
- **Phase 3 — pre-edit hook**: PreToolUse hook in plugin config that intercepts Edit/Write attempts on `.swc/**/workload.json`, denies the action, and instructs the agent to use `swc workload <op>`. Added after phase 2 so skills don't get blocked mid-migration.
- 3.3 (plugin extraction) and 3.4 (MCP wrapper) remain follow-on work items — 3.3 will move `swc_workload` to its own marketplace plugin, leaving `swc` in this plugin as a forwarder; 3.4 adds an MCP wrapper on top of `swc workload <op>`.

## Session — specs & solution design for WI-3.2 CLI `2026-05-18`

- Wrote `specs.md` for WI-3.2: 31 EARS requirements covering lifecycle, authoring, status with rollup, lookup, read/report, missing prerequisites, hook, output, citation, and folder layout; Gherkin scenarios for each requirement; validation rules and business rules
- Wrote `solution.md` for WI-3.2: Python 3 single-plugin CLI (split to `swc-workload` deferred to 3.3), `workload.json` source of truth, SHA-256 truncated 7-char hash IDs over `username + iso-timestamp + branch + title`, numbers display-only, title-only item model (no description field), `key:value` filter syntax, composite reference `N.n(<hash>)` in default output
- Confirmed scope: build + test CLI first; migrate existing skills to call CLI as phase 2 within same WI; existing markdown workloads stay manual (no backfill)
- Status rule: direct parent updates allowed but warn when children not all done; child updates auto-roll parent
- Test approach: full TDD per scenario

## Session — streamline workflow-progress output `2026-05-14`

- Removed bold markers from active stage and title in progress banner — cleaner output in terminal context
- Updated skill to pipe JSON output through text extractor so bash tool shows plain text, not raw JSON
- Added `ensure_ascii=False` to JSON output so unicode characters render directly
- Skill now runs silently — bash tool output is the display, Claude does not re-emit
- Updated tests to reflect no-bold behaviour; all 18 passing
- Added workload item status check to `ship` skill — prompts user to update related items before committing
- Marked 5.3 done

## Session — close out documentation & usage epic `2026-05-14`

- Marked 2.2, 2.2.1, 2.2.2, 2.3, 2.3.1, 2.3.2 done — completes the full documentation & usage group
- Work item 2 now fully complete

## Session — workload restructure for docs epics `2026-05-11`

- Marked 2.1 (update tests for scenarios) done
- Reorganised section 2 sub-items: nested "including usage" and "pattern docs" under 2.2 (docs for swc); nested "plugin usage" and "plugin marketplace" under 2.3 (build instructions)

## Session — ship skill branch and PR enforcement `2026-05-08`

- Updated `ship` skill to check for `main`/`master` branch early and prompt to create a feature branch before proceeding
- PR step now always creates a PR with a summary + motivation body if one doesn't exist, rather than optionally commenting
- `git push` updated to `git push -u origin <branch>` to handle new branches correctly

## Session — rename code-reviewer agent to match naming convention `2026-05-08`

- Renamed `agents/swc_code-reviewer.md` → `agents/code-reviewer.md` — `code` is the object, `reviewer` is the action, matching the SWC `-` separator convention
- Fixed frontmatter opening delimiter in agent file (`--` → `---`)
- Updated all references in `workflowDeliver_refine/SKILL.md`, including correcting `subagent_type` to fully-qualified `swc:code-reviewer`

## Session — rename swc_push to ship, fix stale skill references `2026-05-06`

- Renamed `swc_push` skill folder to `ship` and removed redundant `name` frontmatter field — reflects the agreed workflow language where work items are shipped into the release package
- Swept all skills for stale `swc_`-prefixed cross-skill references; corrected to bare skill names (`context-lookup`, `workload_item-start`, `workflow-orchestrator`, `workload-update`, `workload`, `workflowImplement`)
- Removed `swc:` namespace prefix introduced during the rename — within-plugin references use bare names only

