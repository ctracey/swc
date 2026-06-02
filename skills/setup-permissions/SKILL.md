---
description: Set up blanket project-level read permissions for all swc skills. Run once per project to stop individual skill-load prompts. Invoked automatically by front-line swc skills — can also be run directly via /setup-permissions.
allowed-tools: Read, Write
---

# SWC Setup Permissions

Grant read access for all swc skill files in this project so they load without individual prompts.

## Steps

### 1. Resolve the swc skills path

Read `~/.claude/settings.json`. Find `extraKnownMarketplaces["tracer-plugins"].source.path` — this is the marketplace root (e.g. `/Users/tracer/claude-plugins`).

Then read `<marketplace_root>/.claude-plugin/marketplace.json` and find the `plugins[]` entry with `name == "swc"`. Use its `source` field (a path relative to the marketplace root, e.g. `./plugins/swc_v1.1.0-PR`) to compose the swc skills path:

```
<swc_skills_path> = <marketplace_root> + "/" + <swc_plugin_source> + "/skills"
```

Resolve any `./` prefix on the source. Do not assume `<marketplace_root>/plugins/swc/skills` — the `swc` plugin's `source` may point to a different folder (versioned, PR branch, etc.), and hard-coding the path will create read-permission rules that don't match where skills actually load from.

### 2. Check existing permissions

Read `.claude/settings.json` (treat as `{}` if missing). Check whether `permissions.allow` contains **all ten** of:

- `"Skill(swc:*)"`
- `"Read(<swc_skills_path>/**)"`
- `"Read(.swc/**)"`
- `"Write(.swc/**)"`
- `"Edit(.swc/**)"`
- `"Bash(mkdir -p .swc/**)"`
- `"Bash(python3 <swc_skills_path>/**)"`
- The skill-helper JSON-parse one-liner (see step 4 for the exact JSON-encoded string)
- `"mcp__swc-workload__*"`
- `"mcp__plugin_swc_swc-workload__*"`

**All ten present:** print `swc: skill permissions already configured.` and stop.

**Any missing:** proceed to step 3 — the writer in step 4 will add the missing entries while preserving any that already exist.

### 3. Inform the user

Print:
```
swc: granting permissions for all swc skills in this project.
Skill invocations, skill-file reads, swc python helpers, .swc/ doc reads,
and swc-workload MCP calls will run without individual prompts.
Other operations within skills (git, edit, write, non-swc bash) still ask as normal.
```

### 4. Write permissions

Add all ten of the following entries to `permissions.allow` in `.claude/settings.json`, preserving all existing content. Skip any entry that is already present. Write the file.

| Rule | What it allows |
|---|---|
| `Skill(swc:*)` | Invoking any swc skill |
| `Read(<swc_skills_path>/**)` | Reading any swc skill file (SKILL.md, helper scripts, fixtures) |
| `Read(.swc/**)` | Reading any SWC context doc (plan, notes, changelog, workitems/, etc.) — scoped to the project's `.swc/` folder |
| `Write(.swc/**)` | Create stub docs and workitem files under `.swc/` (context-init, etc.) |
| `Edit(.swc/**)` | Modify SWC context docs (notes, changelog, summaries) |
| `Bash(mkdir -p .swc/**)` | Create `.swc/<folder>/` and `workitems/<N>/` directories. **Note:** matches relative-path mkdirs only — if a skill builds an absolute mkdir path, it will still prompt. |
| `Bash(python3 <swc_skills_path>/**)` | Running swc-shipped python helpers (e.g. `context-lookup.py`, `progress.py`) without prompting; other `python3` invocations still ask |
| **JSON-parse one-liner** (see below) | Running the swc convention `python3 -c` helper that extracts `output` (or `error`) from a script's JSON envelope. Used by multiple skills to render their python helpers' results. Listed as an exact-string rule (not all `python3 -c`) so other one-liners still prompt. |
| `mcp__swc-workload__*` | Calling any tool on the `swc-workload` MCP when registered at project scope (e.g. via `claude mcp add`) |
| `mcp__plugin_swc_swc-workload__*` | Calling any tool on the `swc-workload` MCP when bundled with the swc plugin (`.mcp.json` at plugin root). Claude Code namespaces plugin-bundled MCPs as `plugin_<plugin>_<server>`. |

The JSON-parse one-liner rule, exactly as it must appear in `.claude/settings.json` (JSON-encoded — copy verbatim, including the backslash escapes):

```
"Bash(python3 -c \"import sys,json; d=json.load\\(sys.stdin\\); print\\(d.get\\('output', d.get\\('error', ''\\)\\)\\)\")"
```

Both MCP rules are kept because the same MCP can be active in either form depending on how it's registered. Listing both means setup works regardless.

### 5. Confirm

Print:
```
✔ Permissions written to .claude/settings.json
  Reload with /hooks or restart Claude Code to activate.
```
