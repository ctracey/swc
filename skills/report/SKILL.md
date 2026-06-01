---
description: Full status report combining plan summary, workload, and notes overview. Use when the user says "give me a report", "catch me up", "where were we", "status report", "picking up where we left off", or invokes /report.
allowed-tools: Read, Glob, Skill, mcp__swc-workload__list
---

# SWC Report

## Step 0. Ensure swc skill permissions

Follow the `setup-permissions` skill.

## Step 0a. Verify MCP dependency

Follow the `mcp-check` skill. If the MCP is missing, the check delegates to `mcp-install` — stop here, the report cannot run without it.

Then delegate to the three component skills in order, then add a NEXT STEP section.

1. Invoke `report-plan`
2. Invoke `workload` (renders the work items via `mcp__swc-workload__list`)
3. Invoke `report-notes`

## 4. NEXT STEP

After the three sections, output:

```
NEXT STEP
[work item number] — [one-line description of what this work item is about]
```

Identify the first `not-started` work item (or sub-item). Use the items returned by `mcp__swc-workload__list` in their declared order — first item with status `not-started`. If the MCP exposes a `find_first(status=not-started)` (or equivalent) tool, prefer that. Use the work item number and a concise description of its purpose — do not copy the raw text verbatim if it is verbose.
