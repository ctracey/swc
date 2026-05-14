---
description: Summarise the notes and decisions captured for the active workload. Use when the user says "what notes do we have", "show me the notes", "what decisions have been made", "summarise the notes", or invokes /report-notes.
allowed-tools: Read, Glob, Bash
---

# SWC Notes Summary

Read the active notes file and present a concise overview of key decisions and conventions captured.

## Steps

### 0. Ensure swc skill permissions

Follow the `setup-permissions` skill.

### 1. Resolve the active workload

1. Run `git branch --show-current`
2. Read `.swc/_meta.json`
3. Look up branch in `workloads` map → folder name
4. Fallback: most recently modified folder under `.swc/`

Read `.swc/<folder>/notes.md`.

### 2. Summarise

Open with two lines:
```
NOTES SUMMARY
notes doc: .swc/<folder>/notes.md
```

List topics as a flat bullet list — one line per topic, naming the key decision or convention only. No sub-bullets unless a topic has more than one distinct rule. Keep the whole output under 10 lines.

### 3. Close with an invitation

End with:

> "Ask me about any of these, or say 'show notes doc' to see the complete notes file."
