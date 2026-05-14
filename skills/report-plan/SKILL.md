---
description: Summarise the plan for the active workload. Use when the user says "what's the plan", "show me the plan", "summarise the plan", or invokes /report-plan.
allowed-tools: Read, Glob, Bash
---

# SWC Plan Summary

Read the active plan file and present a concise high-level summary, leaving the door open for follow-up questions.

## Steps

### 0. Ensure swc skill permissions

Follow the `setup-permissions` skill.

### 1. Resolve the active workload

1. Run `git branch --show-current`
2. Read `.swc/_meta.json`
3. Look up branch in `workloads` map → folder name
4. Fallback: most recently modified folder under `.swc/`

Read `.swc/<folder>/plan.md`.

### 2. Summarise

Open with two lines:
```
PLAN SUMMARY
plan doc: .swc/<folder>/plan.md
```

Then three things only:
- **Goal** — one sentence
- **Key features** — 3–5 bullets, one line each
- **Principles** — 2–3 bullets max, only if meaningfully distinct from features

Skip out-of-scope unless the user asks. Do not output the raw plan file.

### 3. Close with an invitation

End with:

> "Ask me about any part, or say 'show plan doc' for the full document."
