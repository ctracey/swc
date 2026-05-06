# Claude Code task execution workflow

## Overview

This document describes a structured approach to delegating software development tasks through Claude Code using a main session, an implementation subagent, and a review subagent. The workflow is sequential — one task at a time — with the user present to approve outcomes and resolve decision points.

The design prioritises clean context, quality gates, and user control at every stage.

---
## Actors and responsibilities

These are the main actors that support this approach:

 - Main session
 - Implementation subagent
 - Review subagent

### Main session

The main session is the orchestrator. It holds the project context and drives the task lifecycle from start to finish.

**Responsibilities:**
- Maintain the three reference documents (`todo.md`, `plan.md`, `architecture.md`)
- Trigger the task execution skill to begin each task
- Receive and assess the rich summary artifact from the implementation subagent
- Spawn the review subagent and provide it with the summary artifact
- Assess review findings and, where needed, spawn a fresh implementation subagent to apply fixes
- Present the structured user handoff and await approval
- Commit and push to the GitHub PR branch on task completion
- Move to the next task once the user approves

The main session never implements code. It delegates, coordinates, and decides.



### Implementation subagent

The implementation subagent is spawned by the main session for each task or fix cycle. It operates within its own session context, meaning the WAY fires fresh, preferences are clean, and there is no accumulated context baggage from prior tasks.

**Scope: one work item per run.** The subagent receives a single work item, executes it fully, and stops. It does not proceed to the next item.

**Responsibilities:**
- Receive the task brief from the main session (task description from `workload.md`, plus `plan.md` and `architecture.md` for context)
- Follow the implementation skill workflow — the two bookend moments are mandatory:
  1. **Upfront approach agreement (blocking gate)** — propose the implementation approach and wait for explicit user approval before writing any code
  2. **Final satisfaction check** — present what was done and confirm the user is satisfied before closing
- Write tests first (spec-driven TDD) — the test file is the spec. The test harness is language/framework-appropriate, agreed with the user, and documented in `architecture.md`
- **Spec approval is a blocking gate** — the agent does not touch implementation code until the user has approved the test spec
- Implement until tests pass — done signal is a passing test suite
- Produce a rich summary artifact covering: what was done, decisions made, approach taken, tests added, build status
- Write a `workitems/<item-number>/context.md` capturing the agreed approach, decisions made, and any open questions for this item
- **Proactively make the case for quality** — don't wait for the reviewer to ask. Lead with why the solution is sound: approach rationale, edge cases considered, test coverage, known trade-offs. The reviewer's job is verification, not extraction.
- Return the summary artifact to the main session

The implementation subagent does not directly invoke the review subagent. That responsibility sits with the main session.



### Review subagent (code-reviewer)

The review subagent is spawned autonomously by `swc_deliver` after the implementation agent returns its summary. It is a **quality pre-filter** — its job is to ensure the code is clean and well-structured before the human sees it. It does not assess correctness or intent — that is the human's role at Gate 3.

**Responsibilities:**
- Receive the summary artifact and relevant code context
- Check code quality, SOLID principles, and refactoring opportunities
- Return structured findings

Findings trigger another implementation pass (via `swc_implement`) to address quality issues. This loop runs autonomously until the quality bar is met. The human is not involved in this loop — they see the result only once quality has been cleared.

---
## Workflow sequence

```
/swc-deliver [N]  (main session — interactive)
  │
  ├── [GATE 1] Propose approach → human agrees
  ├── Write test spec (scenario-based, agreed harness)
  ├── [GATE 2] Present spec → human approves
  ├── [GATE 3] Solution design — surface implementation questions → human resolves
  │
  ├── [PRE-FLIGHT] Optional health check (opt-in, main session)
  │     User confirms → commands sourced from solution.md (fallback: architecture.md)
  │     → findings presented with scope relevance → user decides on failures
  │     → quality-baseline.md written → included in brief
  │
  ├── /swc-implement (main session — spawns agent)
  │     Brief: work item + plan.md + architecture.md + requirements.md + specs.md
  │     + solution.md + quality-baseline.md (if exists) + context.md from prior passes (if any) + review findings (if any)
  │     └── Implementation agent (autonomous — follows implementation workflow)
  │           ├── Reads prior context.md passes to understand what was tried and why
  │           ├── Implements against approved spec until tests pass
  │           ├── Documents decisions and assumptions in context.md (appends new pass)
  │           ├── Flags scope concerns in summary, continues on original scope
  │           └── Appends pass section to summary.md, returns
  │
  ├── swc_code-reviewer agent (autonomous — quality pre-filter)
  │     ├── Reads requirements.md, specs.md, summary.md, code files
  │     ├── Reviews: quality, SOLID, security, test coverage
  │     └── Writes structured findings to code-review-findings.md (BLOCK/WARN/PASS)
  │
  ├── [REFINE] User decides per finding: resolve or tech debt
  │     ├── Resolve → /swc-implement again with findings in brief (max 2 loops)
  │     └── Tech debt → appended to tech-debt.md, advance
  │
  └── [GATE 3] Human review — correctness and satisfaction (blocking gate)
        Human sees: tests passing, code quality cleared, summary artifact
        Human question: "Did we build the right thing?"
        │
        ├── Not satisfied → back to GATE 1 with context (full pass, not a patch)
        │
        └── Satisfied → commit + push to PR branch
```

---
## Technical solutions

This solution onboards the agent by:

 - using claude code extensible mechanisms that influence agent behaviour
 - customising workflows & behaviour

### WAY (context injection mechanism)

A WAY is a session-scoped context injection pattern defined in `CLAUDE.md`. A hook at session start watches for a pattern match in the user's prompt. The first time a matching pattern is detected, the relevant context is injected — once per session only.

Because each subagent has its own session, the WAY fires fresh for both the implementation subagent and the review subagent. This ensures preferences are always present and not lost due to context drift in a long main session.

**Example WAY content:**
- Source code lives in `src/`, test files in `tests/`
- Tech stack constraints and folder conventions
- Code style preferences


### Skills

Skills define reusable, repeatable processes that can be triggered explicitly (via slash command) or implicitly when Claude Code infers the intent.

| Skill | Purpose |
|---|---|
| `swc_deliver` | Delivery workflow — runs Gates 1–3 in main session, orchestrates quality loop, commit/push |
| `swc_implement` | Agent spawning — assembles brief, spawns fresh implementation agent |
| Implementation workflow | The workflow the implementation agent follows — autonomous, spec→code→tests→summary |



### Hooks

| Hook | Trigger | Purpose |
|---|---|---|
| Session start hook | Start of every session | Initialises WAY pattern matching |
| Pre-commit / pre-push hook | Before git operations | Confirms user is ready before code is committed or pushed |



### Subagent definitions

| Subagent | Spawned by | Scope |
|---|---|---|
| Implementation agent | `swc_implement` (called by `swc_deliver`) | Single work item — implements against approved spec, documents in context.md, returns summary |
| Review agent (`code-reviewer`) | `swc_deliver` (after implementation returns) | Quality pre-filter — code quality, SOLID, refactoring; findings fed back to `swc_implement` |

Each subagent gets its own session, its own WAY injection, and operates independently. Fresh subagents on every pass — never reuse a prior session.

**Why fresh agents:** users cannot converse directly with a spawned agent. The agent receives its brief, executes autonomously, and returns a result. This constraint shapes the whole design — interactive work (gates) stays in the main session; autonomous work (implementation, review) is delegated to fresh agents with complete briefs.


---
## Reference documents

Reference docs live in the `.swc/` workload folder for the branch. All scoped to the branch/PR.

| File | Contents |
|---|---|
| `.swc/<folder>/workload.md` | Numbered task breakdown with status markers |
| `.swc/<folder>/plan.md` | Feature list, goals, product intent, out of scope |
| `.swc/<folder>/architecture.md` | Tech stack decisions, folder structure, architectural constraints. Also records agreed test harness approach per language/framework. |
| `.swc/<folder>/notes.md` | Conventions, agreements, decisions that apply across tasks |
| `.swc/<folder>/changelog.md` | Append-only per-task record of what happened and why |
| `.swc/<folder>/workitems/<N>/requirements.md` | Per-item: intent, constraints, approach direction. Written during requirements stage. |
| `.swc/<folder>/workitems/<N>/specs.md` | Per-item: acceptance criteria and scenarios. Written during specs stage. |
| `.swc/<folder>/workitems/<N>/solution.md` | Per-item: resolved implementation decisions and technical guidance. Written during solution-design stage. |
| `.swc/<folder>/workitems/<N>/quality-baseline.md` | Per-item: pre-flight health check results — commands run, findings with scope relevance, and user decisions. Written by the implement stage before spawning the agent; read by the agent during orient. Optional — only written if the user opts in. |
| `.swc/<folder>/workitems/<N>/context.md` | Per-item: agreed approach, decisions made, open questions. Written by the implementation subagent during execution. |

### `workload.md` task format

```markdown
- [ ] **N. Task name**
  - [ ] N.1. Sub-task description
```

### `plan.md` format

```markdown
## Goal / Why
## Features
## Out of scope
```

### `architecture.md` format

```markdown
## Tech stack
## Folder structure
## Constraints
```

---

### GitHub integration

- Each task completion triggers a commit and push to the PR branch
- Tags or commit markers track task boundaries
- Commit history provides a rollback point if a task is rejected
- The pull request represents the holistic outcome of the main session


---
## Decision points and user control

The implementation agent is expected to make decisions autonomously — data structures, implementation details, internal design. It does not stop to ask. Scope concerns are flagged in the summary artifact and raised at Gate 3; work continues on the original scope.

The agent stops only when no reasonable forward path exists within the agreed brief. This is a narrow exception, not the default.

User control is exercised at the four gates — not mid-implementation. See the implementation decision guide in `notes.md`.

---
## Key design principles

**Sequential over parallel** — one task at a time, user approves before the next begins.

**Single item scope** — one work item per agent run. The agent executes it fully and stops. It does not proceed to the next item autonomously.

**Spec-driven TDD** — tests are written before implementation. The test file is the spec. The agent does not write implementation code until the user has approved the test spec. Done means tests pass — not "looks right".

**Four human gates** — approach agreement, spec approval, solution design, and satisfaction/correctness review. Every gate is blocking. The solution design gate surfaces implementation-specific questions before the brief is sealed. The human satisfaction gate (Gate 4) can trigger a full feedback pass — back to Gate 1 with context, not a patch.

**Review agent is a quality pre-filter, not a correctness judge** — the `code-reviewer` agent runs autonomously before the human sees the result. It ensures code quality and SOLID compliance. Correctness — did we build the right thing? — is the human's judgement at Gate 3 only.

**Proceed unless genuinely stuck** — the implementation subagent is expected to make decisions: data structures, implementation details, internal design choices. These do not require stopping. Scope concerns are noted and raised in the summary at Gate 3 — work continues on the original scope. The only reason to stop mid-implementation is when no reasonable forward path exists within the agreed brief.

**Small tasks as discipline** — smaller tasks are clearer, less abstract, and more specific. Tight feedback loops catch drift early and prevent waste on work that isn't needed.

**Main session as orchestrator only** — never implements, only delegates and coordinates.

**Fresh subagents over session reuse** — clean context, fresh WAY injection, no accumulated drift.

**Rich summary as the handoff artifact** — context travels explicitly between actors, not via shared session state.

**Proactive quality pitch** — the implementation subagent arrives at handoff having already made the case for quality. The reviewer verifies; it doesn't interrogate.

**Structured user handoff** — always leads with what was done, not a question.
