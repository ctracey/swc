---
description: Locate or create the active SWC context folder for the current branch. Single source of truth for branch→folder naming. Use when you need to find the active context, or when invoked via /context-lookup.
allowed-tools: Read, Glob, Bash, Write, Skill, mcp__swc-workload__exists
---

# SWC Lookup

Determine the `.swc/<folder>/` path for the current (or specified) branch. A Python helper (`context-lookup.py`) does the non-interactive git/filesystem inspection in one call; the skill drives the interactive prompts and the single MCP `exists` call.

## Arguments

- `/context-lookup` — locate existing context for the current branch
- `/context-lookup <branch>` — locate existing context for a specific branch
- `/context-lookup --create` — locate or create the context folder for the current branch (used by planning skills)

## Steps

### 0. Ensure swc skill permissions

Follow the `setup-permissions` skill.

### 1. Probe state via the helper

Run the probe script once. Pass the branch argument if supplied:

```bash
python3 /Users/tracer/claude-plugins/plugins/swc/skills/context-lookup/context-lookup.py probe [<branch>]
```

The script emits one of:

- `{"status": "resolved", "context": {...}, "from": "meta"|"scan"}` — context is known. **Skip to Step 4.**
- `{"status": "needs_user_input", "reason": "...", "current": {...}, "candidates": [...]}` — handle in Step 2.
- `{"status": "no_workload", "current": {...}}` — handle in Step 3.

### 2. Handle interactive cases

Branch on `reason`:

**`not_a_git_repo`**
```
This directory isn't a git repository.

  Initialise one now? (y / n — use folder name instead):
```
- **Yes:** ask for the primary branch name (default `main`), then run `git init -b <name>`. Re-run Step 1.
- **No:** construct a synthetic context — `type: folder`, `source: current.derived_folder`, `name: current.derived_folder`, `location: .swc/<derived>`, `absolute_path: <pwd>/.swc/<derived>`. Skip persistence (Step 4) and continue to Step 5.

**`default_branch`**
```
⚠ Working directly on `<current.branch>` makes it harder to review and roll back changes.
  A feature branch is recommended.

  What should the working branch be called?
  (Enter a name, or press Enter to stay on `<current.branch>`):
```
- **Name provided:** run `git checkout -b <name>`, then re-run Step 1.
- **Empty / Enter:** use `current.derived_folder` as the resolved folder. Construct context: `type: branch`, `source: current.branch`, `name: current.derived_folder`, `location: .swc/<derived>`, `absolute_path: <pwd>/.swc/<derived>`. Continue to Step 4.

**`single_folder_no_match`** — invoke `mcp__swc-workload__exists` once against `candidates[0].absolute_path`, then confirm:
```
Found context {name: <candidates[0].name>, location: <candidates[0].location>, workload: <exists|missing>}
[NO MATCH] This folder doesn't match your current branch.
Use this? [Y/n]:
```
- **Yes:** resolve to that candidate. Carry the `exists` result forward to Step 5. Continue to Step 4.
- **No, locate mode:** stop — `No matching context — run /swc:context-init to create one.`
- **No, create mode:** use `current.derived_folder` as resolved. Continue to Step 4.

**`multi_folder`** — for each candidate, invoke `mcp__swc-workload__exists` against its `absolute_path` to fill workload status, then present:
```
Multiple contexts found — which one?
  1. {name: <a>, location: <a-path>, workload: <exists|missing>}  [MATCH if candidates[N].match=true]
  2. {name: <b>, location: <b-path>, workload: <exists|missing>}
Enter a number (or 'new' to start a fresh context):
```
- **Number N:** resolve to `candidates[N-1].name`. Carry that row's `exists` result to Step 5. Continue to Step 4.
- **`new`, create mode:** use `current.derived_folder`. Continue to Step 4.
- **`new`, locate mode:** stop — `No matching context — run /swc:context-init to create one.`

### 3. Handle `no_workload`

**Locate mode:**
```
No context found under .swc/. Run /swc:context-init to create one.
```
Stop.

**Create mode:** use `current.derived_folder` as the resolved folder. Construct context: `type: branch`, `source: current.branch`, `name: current.derived_folder`, `location: .swc/<derived>`, `absolute_path: <pwd>/.swc/<derived>`. Continue to Step 4.

### 3a. Confirm location (first-time `.swc/` creation only)

Before persisting (Step 4 writes `.swc/_meta.json`, which auto-creates `.swc/` if missing), check whether `.swc/` already exists in the current working directory.

- **`.swc/` already exists** — skip this step silently and proceed to Step 4.

- **`.swc/` does NOT exist** — this is the first SWC use in this project. Pause and confirm with the user before any folder is created.

  Resolve:
  - `<cwd>` — current working directory
  - `<repo_root>` — `git rev-parse --show-toplevel` (empty if not a git repo)

  Show:
  > "SWC stores its context docs in a `.swc/` folder. This is the first time you're using SWC in this project — `.swc/` will be created at:
  >
  >   `<cwd>`
  >
  > [Include the next line only if `<repo_root>` is non-empty AND `<cwd>` != `<repo_root>`:]
  > This is not the repository root. The repo root is `<repo_root>`. SWC context usually lives at the repo root so it travels with the project — consider switching there before continuing.
  >
  > Proceed and create `.swc/` here? (y/n)"

  - **Yes** — continue to Step 4.
  - **No** — stop and return control to the caller. Do not persist. Do not create `.swc/`. The user is expected to change directory and re-invoke.

### 4. Persist the mapping

If a `branch` value is known (i.e. not the non-git-fallback path), run:

```bash
python3 /Users/tracer/claude-plugins/plugins/swc/skills/context-lookup/context-lookup.py persist <branch> <folder>
```

Silent on success. Skip this step in the non-git-fallback path.

### 5. Resolve workload presence

If Step 2 already invoked `mcp__swc-workload__exists` for the resolved context (single_folder_no_match or multi_folder paths), reuse that result. Otherwise invoke it once now against the resolved context's `absolute_path`.

### 6. Return

**Locate mode:** print the structured line:
```
Found context {type: <type>, source: <source>, name: <name>, location: <location>, absolute_path: <absolute_path>, workload: <exists|missing>}
```

**Create mode:** return the resolved context to the calling skill (including `absolute_path`). Print nothing — the calling skill handles confirmation.

> **Goal:** single source of truth for branch→folder naming. Never silently load the wrong context. When in doubt, ask.

> **MCP arg note:** every `mcp__swc-workload__*` call requires `absolute_path` as its `workload` argument. The underlying CLI does not resolve folder names or relative paths — it expects the full absolute path to the context folder.
