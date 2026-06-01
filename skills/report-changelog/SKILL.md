---
description: Summarise the changelog for the active context. Use when the user says "what changed", "show me the changelog", "what happened in task N", "what happened in work item N", "recent changes", or invokes /swc-report-changelog.
allowed-tools: Read, Glob, Bash
---

# SWC Changelog

Read the active changelog file and present a concise overview of recent work item entries.

## Steps

### 0. Ensure swc skill permissions

Follow the `setup-permissions` skill.

### 1. Resolve the active context

1. Run `git branch --show-current`
2. Read `.swc/_meta.json`
3. Look up branch in `workloads` map → folder name
4. Fallback: most recently modified folder under `.swc/`

Read `.swc/<folder>/changelog.md`.

### 2. Summarise

- By default, show the **last 3 work item entries** — most recent first
- If the user asked about a specific work item (e.g. "what happened in 2.1"), show that entry in full
- For each entry: include the timestamp from the heading (`YYYY-MM-DD HH:MM`), then one line summary of what was decided or changed
- Entries are in chronological order — do not sort by work item number when appending

### 3. Close with an invitation

End with:

> "Say 'show full changelog' to see all entries, or ask about a specific work item."
