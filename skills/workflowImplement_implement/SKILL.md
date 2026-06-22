---
description: Implement stage of the implementation workflow — scenario-driven TDD loop against the approved spec. Second stage of the implementation workflow. Use when invoked by workflowImplement.
allowed-tools: Read, Write, Edit, Glob, Bash
---

# Implement — Implement Stage

## Steps

### 1. Determine approach and spec type

Read the `## Test approach` field from `solution.md` (set during the deliver solution-design stage):
- **Full TDD** — write test per scenario, implement until passing, update docs. Default if absent.
- **Lightweight** — implement directly against the spec checklist; no automated test file required.

Read `specs.md` and `architecture.md` to determine the spec type:

| Type | Indicator | Verification |
|------|-----------|--------------|
| Code (CLI, script, service) | Test framework documented in architecture.md | Automated test file, run suite |
| Skill / Way (markdown) | Work item is a `.md` instruction file | Acceptance checklist; use `ways-tests` skill for ways |
| Agent | Work item defines agent behaviour | Input/output scenarios, verified by running the agent |

### 2. Judgment-call guidance

When facing spec ambiguity or an approach choice not covered by `solution.md` or `specs.md`:

- **Make the call.** Choose the most reasonable interpretation and keep going.
- **Log it immediately** in context.md as `- **Assumption:** [what was assumed, should be verified]`.
- **Do not interrupt the user.** Pausing for minor decisions defeats the purpose of autonomous implementation.

The only exception is a genuine direction decision where the wrong call would require significant rework and the docs give no basis to decide — surface that explicitly, write what you have to context.md, and halt.

Assumptions logged here are aggregated into the `### Judgment calls` section of `summary.md` at the summarise stage so they are easy to review.

### 3. Cycle through scenarios

Work through each scenario in `specs.md` one at a time.

#### Code work items

For each scenario:

1. **Write the test** for this scenario in the agreed test file and framework (from architecture.md)
2. **Run the test** — confirm it fails before writing any implementation
3. **Implement** to make it pass
4. **Fix loop** — if still failing: diagnose, fix, re-run. Max **3 fix cycles** per scenario.
   - After 3 cycles still failing → go to [Blocked](#blocked)
5. **Document** in context.md — any decision, assumption, or deviation made while working this scenario:
   - `- **Decision:** [what was chosen and why]`
   - `- **Assumption:** [what was assumed, should be verified]`
   - `- **Tried:** [what didn't work and why]`
6. **Update docs** — keep docs current as you go; do not batch all doc updates to the end.
   - `README.md` — update only the section(s) directly affected by this scenario:
     - New or changed components → Architecture section
     - New or changed commands → Operations section (or `docs/operations.md`)
     - Pipeline changes → CI/CD section
     - Do not rewrite sections unrelated to this work item
   - `docs/operations.md` — if run/build/test commands changed
   - `docs/environment.md` — if setup steps or prerequisites changed
   - `docs/architecture.md` — if the design or component relationships changed
   - `.swc/` docs — if a convention, constraint, or decision was clarified

#### Skill / Way / Agent work items

For each scenario:

1. **Read the criterion** from the acceptance checklist in specs.md
2. **Check** whether the skill/way/agent file satisfies it — read the file and verify directly
3. **Implement** if not satisfied: edit the file to satisfy the criterion
4. **Document** in context.md: what was found, what changed
5. **Update docs** as needed

For Ways specifically, run `ways-tests` after each scenario to score the match.

### 4. Run the full suite

After all scenarios pass, run the full test suite (code) or walk the complete checklist (skill/way/agent) to confirm no regressions.

If regressions are found: treat each as a new scenario cycle with the same 3-cycle limit.

### 5. Blocked

If a scenario still fails after 3 fix cycles, or no reasonable forward path exists within the agreed brief:

1. Write to context.md:
   ```
   - **Blocker (stopped):** scenario "[name]" — attempted [what was tried x3]. Failing because [root cause as understood]. Cannot proceed without: [what is needed].
   ```

2. Write a partial `summary.md` to `.swc/<folder>/workitems/<N>/summary.md`:

   ```markdown
   # Summary — <N>: <title> — Pass <n> — <YYYY-MM-DD>

   ## Changes

   [What was completed before the blocker — one bullet per scenario that passed]

   ## Blocker

   [Scenario that failed, what was tried across 3 cycles, root cause, what is needed to unblock]

   ## Testing

   Blocked — partial implementation only.

   ## Test results

   Scenarios passing: [X of Y]. Blocked on: [scenario name].

   ## Pipeline

   Not run — blocked before completion.

   ## Build confidence

   Low — blocked on [scenario].

   ## Review findings

   None.

   ## Scope flags

   None.

   ## Approach needs revisiting

   [If the agreed approach is the root cause of the blocker, describe what a better approach would be. Otherwise: No.]
   ```

3. Stop. Return control to the orchestrator. Do not advance to Refine.

## Exit criteria

**Normal completion:**
- All scenarios in specs.md addressed and passing
- Full suite / checklist passes with no regressions
- context.md has at least one entry for this pass
- Relevant docs updated where behaviour or conventions changed

**Blocked:**
- Blocker documented in context.md with root cause and what is needed
- Partial summary.md written
- Stopped cleanly — orchestrator notified
