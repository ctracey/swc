---
description: Review stage of the delivery workflow — present implementation summary and QA evidence to the human for acceptance or feedback. Sixth stage of the delivery workflow. Use when invoked by workflowDeliver or via /workflowDeliver_review.
allowed-tools: Read, Write, Bash, Skill, Glob
---

# Deliver — Review Stage

Final human review handoff. Presents what was built so the developer can answer "Did we build the right thing?" Two outcomes: accept (advance to commit/push) or feedback (write `feedback.md` and re-launch the delivery workflow from requirements).

## Context

The work item number, name, and workload folder path are available from the calling context. If missing, read the active workload via `context-lookup`.

## Steps

### 1. Check preconditions

Confirm `summary.md` exists at `.swc/<folder>/workitems/<N>/summary.md`. If not:

> "No `summary.md` found for work item [N]. The implement stage must complete before review can run."

Stop and return to the orchestrator.

### 2. Load artifacts

Read in parallel:
- `.swc/<folder>/workitems/<N>/summary.md` — latest pass section
- `.swc/<folder>/workitems/<N>/code-review-findings.md` — if it exists
- `.swc/<folder>/pipeline.md` — if it exists

### 3. Present the review handoff

Present a structured summary to the developer. Use this format:

---

> **Review — [N]: [work item name]**
>
> **What was built**
> [Bulleted list of changes from the latest pass `### Changes` section in summary.md]
>
> **QA evidence** *(as reported by the implementation agent)*
> - Tests: [test results from summary.md — pass/fail counts, framework, command]
> - New tests: [new tests added, from summary.md]
> - Scenarios covered: [scenarios from summary.md Testing section]
> - Build: [build outcome from summary.md Pipeline section — or "No pipeline.md defined"]
> - Server: [server status from summary.md Pipeline section — or "Not applicable"]
>
> **Code review**
> - Resolved: [count and brief description of findings resolved in refine, or "None"]
> - Deferred to tech debt: [count and brief description, or "None"]
>
> **Build confidence:** [one or two sentences from summary.md Build confidence section]
>
> **Scope flags:** [from summary.md Scope flags section, or "None"]

---

Do not re-run any commands. All evidence is sourced from the artifacts loaded in step 2.

If `code-review-findings.md` does not exist, omit the Code review section and note: "No review findings — refine stage did not run or was skipped."

### 4. Offer dev server (conditional)

Read `pipeline.md`. If it defines a `## Dev environment` section with a `**Start command:**` line (and the value is not "not applicable" or empty):

> "Want me to start the dev server so you can check the running app?
> Command: `[start command from pipeline.md]`"

If the developer says yes, run the start command via Bash.

If `pipeline.md` does not exist, has no `Dev environment` section, or the start command is absent/not applicable — skip this step entirely.

### 5. Review decision

Ask:

> "Does this look right to you — did we build what you were after? (yes / give feedback)"

Wait for the developer's response.

**If satisfied** (any affirmative): proceed to step 6.

**If feedback**: proceed to step 7.

### 6. Accept path

Confirm and return:

> "Great — moving to accept."

Return control to the orchestrator.

### 7. Feedback path

Collect the feedback. Once the developer has described what needs to change, play it back:

> "So the feedback is: [summary of what the developer said]. Is that captured correctly?"

If the developer corrects the playback, update and play back again. Repeat until confirmed.

### 8. Write feedback.md

Write to `.swc/<folder>/workitems/<N>/feedback.md` (replace any existing file):

```markdown
# Feedback — [work item number]: [work item name]

[The confirmed feedback, verbatim as the developer described it]
```

### 9. Re-launch delivery workflow

Announce:

> "Feedback captured. Re-launching the delivery workflow — requirements will open with your feedback as context."

Use the Skill tool to invoke `workflowDeliver` with the work item number as the argument. The requirements stage will detect `feedback.md` and open with it as pre-loaded context.

## Exit criteria

**Done when (accept path):**
- Artifacts loaded and handoff presented
- Developer indicated satisfaction
- Control returned to orchestrator

**Done when (feedback path):**
- Artifacts loaded and handoff presented
- Feedback confirmed by developer
- `feedback.md` written to `.swc/<folder>/workitems/<N>/`
- Delivery workflow re-launched

**Return control to the calling skill.**
