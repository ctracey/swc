---
description: Summarise stage of the implementation workflow — complete context.md pass section, append a pass section to summary.md, return to deliver workflow. Third and final stage of the implementation workflow. Use when invoked by workflowImplement.
allowed-tools: Read, Write, Glob, Bash
---

# Implement — Summarise Stage

## Steps

### 1. Announce stage entry

> "Summarise stage — Work item: [N]: [name]. Verifying context.md and writing summary."

### 2. Verify context.md pass section

Read `.swc/<folder>/workitems/<N>/context.md`. Find the current pass section (the last `## Pass` header).

If the current pass section has no bullet entries, write a brief entry yourself and continue — do not gate on user input:

```
- **Pass summary (auto):** [one sentence covering what was done, any key decisions or assumptions made]
```

### 3. Collect pipeline results

Check if `.swc/<folder>/pipeline.md` exists.

- **If it exists:** read it. Run the build command defined in `## Build`. Capture the outcome (exit code, key output). Note whether the dev environment start command was verified (run it, check the health check signal, then stop it). Populate the Pipeline section of the summary with these results.
- **If absent:** note "No pipeline.md defined — pipeline verification skipped."

### 4. Determine pass number

Check if `.swc/<folder>/workitems/<N>/summary.md` exists.

- **If it does not exist:** this is pass 1. Create the file with the header and first pass section.
- **If it exists:** read it. Count the existing `## Pass` sections. This is pass N+1. Append a new pass section — do not overwrite existing content.

### 5. Write or append summary.md

**On first pass** — create the file:

```markdown
# Summary — <N>: <title>

## Pass 1 — <YYYY-MM-DD>

### Changes

[Bulleted list of what was done — one bullet per logical change. Be specific: file names, function names, what changed and why.]

### Testing

[What was tested and how — automation run (framework, command, outcome) and any manual scenarios walked through.]

### Test results

[Pass/fail counts, command output summary, or "no automated tests — verified by [method]".]

### Pipeline

[Results of running the project pipeline as defined in pipeline.md. For each check: what was run, what was expected, what happened. Write "No pipeline.md defined — skipped." if absent.]

### Build confidence

[One or two sentences: overall confidence the build is working and why. Flag any caveats.]

### Scope flags

[Work observations outside the agreed brief — not acted on, raised for Gate 3. Write "None" if nothing to flag.]

### Judgment calls

[List all `**Assumption:**` entries from context.md for this pass — one bullet each. These are calls made autonomously where the docs were ambiguous. Write "None" if no assumptions were logged.]

### Approach needs revisiting

[If the agreed approach proved unworkable mid-implementation, describe what was encountered and what a better approach would be. This flag triggers Gate 1 again. Write "No" if approach held.]
```

**On subsequent passes** — append to the existing file:

```markdown

---

## Pass <n> — <YYYY-MM-DD>

### Changes

[What changed in this pass relative to the previous — focus on what was fixed or improved, not a full restatement.]

### Testing

[What was re-run and what changed in the test results.]

### Test results

[Pass/fail counts.]

### Pipeline

[Pipeline results for this pass, or "No pipeline.md defined — skipped."]

### Build confidence

[Updated confidence assessment.]

### Scope flags

[New scope observations from this pass, or "None".]

### Judgment calls

[Assumption entries from context.md for this pass, or "None".]

### Approach needs revisiting

["No" if approach held, or describe what needs revisiting.]
```

### 6. Return

Return control to the orchestrator.

## Exit criteria

**Done when:**
- context.md pass section has at least one entry
- Pipeline checks run (or absence noted)
- Pass section appended to `summary.md` (or file created on first pass)
- Judgment calls section populated from context.md Assumption entries

**Return control to the calling skill.**
