---
description: Full status report combining plan summary, workload, and notes overview. Use when the user says "give me a report", "catch me up", "where were we", "status report", "picking up where we left off", or invokes /report.
allowed-tools: Read, Glob
---

# SWC Report

## Step 0. Ensure swc skill permissions

Follow the `setup-permissions` skill.

Then delegate to the three component skills in order, then add a NEXT STEP section.

1. Invoke `report-plan`
2. Invoke `swc-list`
3. Invoke `report-notes`

## 4. NEXT STEP

After the three sections, output:

```
NEXT STEP
[work item number] — [one-line description of what this work item is about]
```

Identify the first work item (or sub-item) with status `[ ]` not started, reading the workload file top to bottom. Use the work item number and a concise description of its purpose — do not copy the raw text verbatim if it is verbose.
