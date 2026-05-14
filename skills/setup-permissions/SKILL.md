---
description: Set up blanket project-level read permissions for all swc skills. Run once per project to stop individual skill-load prompts. Invoked automatically by front-line swc skills — can also be run directly via /setup-permissions.
allowed-tools: Read, Write
---

# SWC Setup Permissions

Grant read access for all swc skill files in this project so they load without individual prompts.

## Steps

### 1. Resolve the swc skills path

Read `~/.claude/settings.json`. Find `extraKnownMarketplaces["tracer-plugins"].source.path` — this is the marketplace root (e.g. `/Users/tracer/claude-plugins`). The swc skills path is `<marketplace_root>/plugins/swc/skills`.

### 2. Check existing permissions

Read `.claude/settings.json` (treat as `{}` if missing). Check whether `permissions.allow` contains `"Skill(swc:*)"`.

**Already present:** print `swc: skill permissions already configured.` and stop.

### 3. Inform the user

Print:
```
swc: granting permissions for all swc skills in this project.
Skill invocations and skill-file reads will run without individual prompts.
Operations within skills (git, bash, edit, write) will still ask as normal.
```

### 4. Write permissions

Add both `"Skill(swc:*)"` and `"Read(<swc_skills_path>/*)"` to `permissions.allow` in `.claude/settings.json`, preserving all existing content. Write the file.

### 5. Confirm

Print:
```
✔ Permissions written to .claude/settings.json
  Reload with /hooks or restart Claude Code to activate.
```
