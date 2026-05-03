---
name: swc_util_base-dir
description: Knowledge skill — explains how to resolve the <base_dir> placeholder used in skill instructions that reference files bundled alongside the skill.
type: knowledge
---

# Skill Base Directory

When a skill instruction contains `<base_dir>`, substitute it with the base directory path shown at the top of the skill invocation context, on the line that reads:

```
Base directory for this skill: /path/to/skill/dir
```

## Example

Skill instruction:

```
python3 <base_dir>/script.py
```

Skill invocation context header:

```
Base directory for this skill: /Users/alice/workspace/project/.claude/skills/my-skill
```

Resolved command:

```
python3 /Users/alice/workspace/project/.claude/skills/my-skill/script.py
```

## Why

Skills may be installed at any path (global `~/.claude/skills/` or project-local `.claude/skills/`). Using `<base_dir>` instead of a hardcoded path ensures the skill works regardless of where it is installed.
