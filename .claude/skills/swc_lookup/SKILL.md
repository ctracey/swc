---
name: swc_lookup
description: Locate or create the active SWC workload folder for the current branch. Single source of truth for branch→folder naming. Use when you need to find the active workload, or when invoked via /swc-lookup.
allowed-tools: Read, Glob, Bash, Write
---

# SWC Lookup

Determine the `.swc/<folder>/` path for the current (or specified) branch. Handles git setup if needed. In create mode, also creates the folder and updates `_meta.json`.

## Arguments

- `/swc-lookup` — locate existing workload for the current branch
- `/swc-lookup <branch>` — locate existing workload for a specific branch
- `/swc-lookup --create` — locate or create the workload folder for the current branch (used by planning skills)

## Steps

### 1. Determine the working context

Run `git rev-parse --is-inside-work-tree 2>/dev/null` to check for a git repo.

**If not a git repo:**

```
This directory isn't a git repository.

  Initialise one now? (y / n — use folder name instead):
```

- **No:** use the current directory name (basename of `pwd`) as the identifier. Skip to step 2.
- **Yes:** ask for the primary branch name (default: `main`), then run `git init -b <name>`.
  After init, go to the branch recommendation prompt below.

**If a git repo exists**, run `git branch --show-current` (or use the branch argument if supplied).

**Branch recommendation — triggers when on `main`/`master` OR just after `git init`:**

```
⚠ Working directly on `<branch>` makes it harder to review and roll back changes.
  A feature branch is recommended.

  What should the working branch be called?
  (Enter a name, or press Enter to stay on `<branch>`):
```

- **Name provided:** run `git checkout -b <name>`, use the new branch.
- **Empty / Enter:** continue on the current branch. No further warning.

### 2. Derive the folder name

Replace every `/` in the branch (or directory) name with `_`.

> Example: `feature/swc-refactor` → `feature_swc-refactor`

### 3. Try _meta.json

Read `.swc/_meta.json`.

- **Found and branch has an entry:** folder confirmed → skip to step 5.
- **Missing or branch not in map:** continue to step 4. Print nothing.

### 4. Scan folders

List all folders under `.swc/` (exclude `_meta.json`). Compare against the derived folder name from step 2.

**No folders found — locate mode:**
```
No workload found under .swc/. Run /swc-workflow-plan to start one.
```
Stop.

**No folders found — create mode:**
Use the derived folder name from step 2. Proceed to step 5.

**One folder found:** confirm with the user before proceeding, noting whether it matches:
```
Found one workload: .swc/<branch-subfolder>/workload.md
[MATCH] This folder matches your current branch.   ← or [NO MATCH] if it doesn't
Use this? [Y/n]:
```
If the user declines:
- Locate mode: stop.
- Create mode: use the derived folder name from step 2 and treat as a new workload.

**Multiple folders found:** list them all, flag matches, and ask which to use:
```
Multiple workloads found — which one?
  1. .swc/<branch-subfolder-one>/workload.md  [MATCH]
  2. .swc/<branch-subfolder-two>/workload.md
Enter a number (or 'new' to start a fresh workload):
```

### 5. Persist the mapping to _meta.json

Upsert the branch→folder mapping in `.swc/_meta.json`.

Read the file first if it exists (to preserve other entries):

```json
{
  "workloads": {
    "<branch-name>": "<folder-name>"
  }
}
```

Write the updated file. Print nothing — this is a silent side-effect.

### 6. Return

**Locate mode:** print the located path:
```
Located: .swc/<folder>/workload.md
```

**Create mode:** return the located folder path to the calling skill. Do not print a confirmation — the calling skill handles that.

> **Goal:** single source of truth for branch→folder naming. Never silently load the wrong workload. When in doubt, ask.
