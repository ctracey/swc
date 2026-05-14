# Notes

## Decisions

## Risks

## References

## Ideas

### WI-3.2: CLI tool for workload

Action catalog the CLI needs to support against `workload.md`. Compiled from a sweep of the existing swc skills — these are the operations currently performed (directly or indirectly) on the file.

**Lifecycle**
- Scaffold — create empty file with title and `## Work Items` heading
- Archive — rename folder with `_archived` suffix (Replace mode in `workflowPlan_context`)
- Cleanup — delete folder once all items complete

**Authoring (content)**
- Write skeleton — top-level items only, one per phase/priority
- Write full breakdown — parents + sub-items, hierarchical numbering
- Append item — add a new work item mid-flow (under appropriate section or as new top-level)
- Renumber items — nest existing items one level deeper (Sibling mode)

**Status mutation**
- Set item status — `[ ]` / `[-]` / `[x]` on a target line
- Roll up parent — re-evaluate parent marker from its sub-items' states
- Guard against downgrade — never move `[x]` backwards (silent / programmatic path)

**Resolution / lookup**
- Locate file — resolve `.swc/<folder>/workload.md` from current branch via `_meta.json` (fallback to most-recently-modified folder)
- Resolve target item — match by number (`2.6`), description keyword, or implied context ("current", "next"); disambiguate if needed
- Find in-progress items — filter for `[-]` to auto-pick when only one is active

**Read / report**
- Render visually — display with status symbols
- Summarise progress — work item count, done count
- Read item scope — fetch name + description for a given item number
- Check presence — does `workload.md` exist for this branch
- Check completeness — is the workload populated and confirmed

**Cross-doc coordination**
- Prompt for status updates from session changes — match changed files to items, ask user, route edits through the status-mutation path (never direct)

**Skills that currently perform these (for reference):** `context-init`, `context-lookup`, `context--workload`, `workflowPlan_context`, `workflowPlan_delivery`, `workflowPlan_breakdown`, `workflowPlan_finalise`, `workflowDeliver`, `workflowDeliver_implement`, `workflowDeliver_refine`, `workflowImplement_orient`, `workload`, `workload-update`, `workload_item-start`, `ship`.

### WI-6: Dynamic skill discovery & installation

The goal is a skill that surfaces relevant skills from the Claude public marketplace based on the current project's tech stack, then installs accepted ones project-scoped via the local marketplace CLI.

**Flow:**
1. Detect stack — read well-known files (package.json, requirements.txt, Cargo.toml, go.mod, Gemfile, pyproject.toml, etc.) to infer languages, frameworks, and tools in use.
2. Marketplace lookup — query the Claude public marketplace for skills tagged to the detected stack. Return a ranked list of suggestions with name, description, and marketplace listing URL.
3. User acceptance — present suggestions interactively; user accepts or rejects each one. Batch accepted skills for install.
4. Install — for each accepted skill: add the plugin to the local marketplace via its public listing, then install it with `--scope project`.

**Key constraints:**
- Should not auto-install without explicit user confirmation per skill.
- Stack detection should be non-destructive (read-only file inspection).
- Install must use the local marketplace CLI (not manual file copying) so versioning and dependencies are tracked correctly.
- Project-scoped install keeps the skill local to this repo — no global pollution.

**Open questions:**
- Does the public marketplace expose a queryable API, or does lookup require scraping / a known index?
- How does the local marketplace CLI accept a public listing reference — by URL, slug, or ID?
- Should re-running the skill skip already-installed skills or offer an upgrade path?

