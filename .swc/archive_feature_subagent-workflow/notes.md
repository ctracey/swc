# PR-5 Notes — Claude Code subagent workflow

## Doc purpose

| Doc | Purpose |
|-----|---------|
| `_plan` | What and why — goals, features, scope, intent. Written upfront. |
| `_notes` | How — conventions, agreements, decisions that apply across tasks. Stable reference. |
| `_changelog` | What happened — append-only per-task record of decisions, changes, and learnings. |
| `_architecture` | Tech stack, folder structure, hard constraints. |

Read `_notes` to understand the rules. Read `_changelog` to understand why they are the way they are.

## Skill naming convention

Skills use a `swc_` namespace prefix (underscore as namespace separator, hyphens for word separation within the name). This groups the skill family visually in `ls skills/` and distinguishes them from Claude Code's native `Task*` tools.

| Skill | Purpose |
|-------|---------|
| `swc_list` | Display the task list visually |
| `swc_report-plan` | Concise summary of the `plan.md` doc, with invitation to ask for detail |
| `swc_report-notes` | Concise summary of the `notes.md` doc, with invitation to ask for detail |
| `swc_changelog` | Recent changelog entries, with invitation to ask for more |
| `swc_update` | Update task status in the file |
| `swc_begin` | Scaffold a new workload + plan + architecture set |
| `swc_init` | Write the five stub docs into a resolved workload folder |
| `swc_deliver` | Delivery workflow — interactive, runs gates 1–4, feedback loop, commit/push |
| `swc_implement` | Implementation workflow — subagent brief, autonomous, spec→code→tests→summary |
| `swc_execute` | ~~Spawn an implementation subagent for a task~~ — superseded by `swc_deliver` |

## Skill invocation

Skills support both explicit and implicit invocation:
- **Explicit** — user types `/skill-name` or `/skill-name [args]`
- **Implicit** — Claude infers intent from the description field in the skill frontmatter

Both modes should be supported for all skills in this workflow.

### swc_execute usage

```
/swc-execute                   # next unchecked task from active workload
/swc-execute 3                 # specific task number
```

Implicit triggers: "work on task 3", "start the next task", "execute task 2"

## Task status convention

Parent task status rolls up from subtasks:
- Any subtask in progress or done (but not all done) → parent is `[-]`
- All subtasks done → parent is `[x]`
- No subtasks started → parent is `[ ]`

Markers: `[ ]` not started, `[-]` in progress, `[x]` done

## todo-list display format

Visual symbols used by the `todo-list` skill:

| Status | Symbol | Text treatment |
|--------|--------|----------------|
| Done | `✔` | Unicode combining strikethrough (U+0336 after every character) |
| In progress | `▣` | Plain text |
| Not started | `□` | Plain text |

Subtasks indented with two spaces. Output as plain text — no markdown code block.

## Changelog entry format

```markdown
## Task N.M — Description `YYYY-MM-DD HH:MM`

- Decision or change made
- Why it was made
```

Entries are in **chronological order** — appended as work happens, not sorted by task number.

## File naming convention

- Hyphen couples name parts (tighter binding): `todo-pr-5`
- Underscore separates a doctype qualifier (looser binding): `todo-pr-5_plan`
- Always lowercase

## Available agents and relation to this plan

| Agent | Description | Relation to this plan | Author |
|---|---|---|---|
| `workflow-orchestrator` | Coordinates ADR-driven workflow, guides debate→ADR→branch→implement→PR | Overlaps with the main session orchestrator role — but ADR-focused, not todo-task-focused | Aaron Bockelie |
| `task-planner` | Plans work using branches and TodoWrite, breaks down complex work | Overlaps with todo-begin (3.1) — scaffolding a task breakdown from a plan | Aaron Bockelie |
| `code-reviewer` | Reviews code for quality, SOLID, requirement traceability | Is the review subagent (6.2) — just needs context wiring | Aaron Bockelie |
| `Plan` | Designs implementation strategy, identifies critical files | Could feed into implementation subagent briefs, or replace parts of todo-begin | Claude Code built-in |
| `system-architect` | Drafts ADRs, never implements | Not directly in scope unless ADR gates are added to the workflow | Aaron Bockelie |

> **Note on ADRs:** Aaron's ADR technique (`workflow-orchestrator`, `system-architect`) is an **architectural lead workflow** — it captures decisions, trade-offs, and rationale for future reference. This PR-5 workflow is a **task/outcome driven workflow** — it cares about getting work done, reviewed, and shipped one task at a time. The two can coexist: an ADR could precede and inform a todo breakdown, but ADR authorship is not part of this workflow's loop.

## task-planner integration with todo-begin (3.1)

`task-planner` is a good candidate to drive the breakdown step inside `todo-begin`. The proposed split:

1. `todo-begin` receives the feature description from the user
2. Spawns `task-planner` as a subagent to reason about task breakdown, dependencies, and branch strategy
3. Main session translates `task-planner`'s output into the persistent `todo-pr-N.md` format (with `_plan`, `_notes`, `_architecture` stubs)

Key mismatch to resolve: `task-planner` thinks in ephemeral TodoWrite + git branches; `todo-begin` needs persistent markdown files. The translation step is the main session's responsibility, not the subagent's.

`task-planner` should receive the `_plan` doc (goal, features, scope) as context so it breaks down work that matches the stated intent.

## Acceptance criteria for planning

The planning conversation is complete when the user can close all sessions, return the next day, open a new session, and — using only the docs — pick up delivery with confidence. No re-explaining context, no re-describing the goal, no re-making decisions already taken.

## Documents are the only briefing the implementer gets

The planning conversation happens in its own session. The implementation subagent — and any future session — will not have access to that conversation. The docs are the only thing they will see.

Every decision that influenced the work must be captured: what was decided, and why. Every constraint, intent, and direction agreed during planning. Not a transcript — but complete enough that someone who was not in the room can read the docs and do the work correctly.

If it shaped the direction, it belongs in the docs. Write to them throughout the conversation as agreements are reached. The final review is just confirming nothing was missed.

## Work item context artifacts

Each work item executed by the implementation subagent gets its own context document:

```
.swc/<folder>/
├── pipeline.md              ← project-level verification config (agreed during planning)
└── workitems/
    └── <item-number>/
        ├── context.md       ← agreed approach, decisions, open questions (per pass, append-only)
        └── summary.md       ← handoff artifact written by the implementation agent
```

- Folder name matches the work item number exactly (e.g. `1.4.2`)
- `context.md` is written by the implementation subagent during execution, not after
- `summary.md` is written during the Summarise stage and travels intact to the deliver workflow
- `pipeline.md` is project-level — agreed once during planning, not per work item
- The test file lives in the codebase alongside the code it describes — not here
- This folder is the reasoning record; the test file is the spec artifact

### context.md format

`context.md` is the running log of what the implementation agent did that wasn't obvious from the code, tests, or agreed brief. It's the memory that travels between fresh agent sessions. Lightweight and append-only — each agent run adds a new dated pass section, never overwrites prior content.

**Written at decision points throughout execution — not at the end.**

**Structure:**

```markdown
# Context — <N>: <title>

## Pass <n> — <YYYY-MM-DD>

- [entry]
- [entry]
```

**What belongs in a pass entry** (self-labelled bullets, no mandatory subsections):

- **Decision:** chose X over Y — wasn't in solution.md — here's why
- **Assumption:** assumed A, which shaped B — user should verify
- **Blocker (guessed):** hit X, made a low-risk call to proceed with Y — flag for user review
- **Blocker (stopped):** hit X, cannot proceed without user input — [describe what's needed]
- **Added:** included X beyond scope — good practice, here's why
- **Tried:** attempted X — didn't work because Y — moved to Z instead
- **State:** currently at [point] — [what's done, what's next, what's incomplete]

**Enforcement:**
- One entry minimum per pass — if nothing diverged, write: `- Implemented per spec — no deviations.`
- The summarise stage verifies a pass section exists and has at least one entry before the agent exits
- The orient stage opens a new pass section at the start of each agent run

**Why this matters:** a new agent picking up a subsequent pass reads context.md to understand what was tried, what assumptions were made, and what dead ends to avoid — without re-examining all the code or re-asking the user.

### summary.md format

`summary.md` is the handoff artifact the implementation agent writes at the end of each pass. It is **append-only** — each pass adds a new dated section; earlier passes are never overwritten. Written during the Summarise stage; read by the deliver workflow refine stage and the human at Gate 3.

**Purpose:** make it easy for the human to accept or reject the work across all passes. Leads with what changed each pass, then evidence it works.

**Code review findings are separate.** Review findings live in `code-review-findings.md` (written by `swc_code-reviewer`), not in summary.md. Gate 3 reads both.

**Structure — first pass (creates file):**

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

[Results of running the project pipeline as defined in pipeline.md. Write "No pipeline.md defined — skipped." if absent.]

### Build confidence

[One or two sentences: overall confidence the build is working and why. Flag any caveats.]

### Scope flags

[Work observations outside the agreed brief — not acted on, raised for Gate 3. Write "None" if nothing to flag.]

### Approach needs revisiting

[If the agreed approach proved unworkable, describe what was encountered and what a better approach would be. Write "No" if approach held.]
```

**Subsequent passes — append only:**

```markdown

---

## Pass <n> — <YYYY-MM-DD>

### Changes

[What changed in this pass relative to the previous — focus on what was fixed or improved.]

### Testing / Test results / Pipeline / Build confidence / Scope flags / Approach needs revisiting

[Same sections — updated for this pass only.]
```

**What goes where:**
- `Changes` is always present — if nothing changed, something is wrong
- `Approach needs revisiting` is a gate signal — if set to anything other than "No", the deliver workflow surfaces it to the user before Gate 3
- Review findings → `code-review-findings.md` (separate file, fresh each review pass)

---

### pipeline.md format

`pipeline.md` is a project-level doc that defines what verification looks like for this project. Agreed once during planning (solution stage); used by the implementation agent during Summarise and by the deliver workflow at Gate 3.

**Location:** `.swc/<folder>/pipeline.md` — alongside `plan.md` and `architecture.md`.

**Purpose:** remove tech-stack bias from the summary format. The summary reports against whatever this file defines, so the format works for any project type (web app, CLI, skill/docs, service).

**Structure:**

```markdown
# Pipeline — <project name>

## Build

**Command:** `<command to run>`
**Expected outcome:** <what a passing build looks like — exit code, key output, artefact produced>

## Dev environment

**Start command:** `<command to start>`
**Health check:** <URL to hit, port to probe, signal to look for, or "not applicable">
**Stop command:** `<command to stop cleanly, or "ctrl-c">`

## Acceptance

<What the human needs to see to accept the work. Narrative — not automated. E.g. "Load localhost:3000, navigate to X, confirm Y renders correctly." Or "Run `cli-tool --help` and confirm output matches spec." Or "Not applicable — verified by test suite only.">
```

**Filling it in:** during `swc_workflow_plan-solution`, the user and Claude agree on what verification looks like for the project and write it here. Work items do not override it — if a work item needs something different, that is a project-level change discussed with the user.

**If `pipeline.md` is absent:** the implementation agent skips the Pipeline section in `summary.md` and notes its absence. The deliver workflow does not attempt to run a pipeline at Gate 3.

## Execution workflow layers

Three layers, each with a distinct responsibility:

| Layer | Skill | Where | Responsibility |
|---|---|---|---|
| Delivery | `swc_deliver` | Main session | Gates 1–3 (3 human gates), quality loop, calls `swc_implement`, commit/push |
| Spawning | `swc_implement` | Main session | Receives approved brief, spawns the implementation agent |
| Execution | implementation workflow | Agent session | Implements against spec, documents decisions, returns summary |

**Key rules:**
- `swc_deliver` does not know or care how the agent is spawned — it calls `swc_implement`
- `swc_implement` does not run gates — it only spawns the agent with the brief it receives
- The implementation agent does not interact with the user — it follows the implementation workflow autonomously
- All three layers read/write from `.swc/<folder>/workitems/<N>/` for the active work item
- `swc_execute` is retained as a legacy skill pending retirement once this is working

## Implementation decision guide

The subagent is expected to make decisions autonomously. The tipping point for stopping is narrow.

**Proceed and document in `context.md`:**
- Data structure choices — expected, make the call
- Implementation details, internal design, naming, algorithms
- Scope observations — note the concern, continue on original scope, raise at Gate 4

**Stop only when:**
- No reasonable forward path exists within the agreed brief and original scope
- i.e. genuinely blocked, not just uncertain

Scope questions never stop work. Flag them as recommendations in the summary artifact for Gate 4. The user decides there whether to extend scope as a new work item.

## Implementation workflow brief format

The implementation agent receives a structured brief assembled by `swc_deliver` / `swc_implement`. Format inherited from `swc_execute` and extended for multi-pass delivery:

```
## Work item brief

**Work item:** [number and name]
[description]

**Done when:** [prose criteria from work item entry — human-readable intent]

**Approved spec:** [path to spec file, or inline checklist for non-code work items]

## Plan
[contents of plan.md, or "not provided"]

## Architecture
[contents of architecture.md, or "not provided"]

## Prior context
[contents of .swc/<folder>/workitems/<N>/context.md — omitted on first pass]

## Review findings (pass N)
[structured findings from code-reviewer — omitted on first pass]
```

**"Done when" vs the spec:** "Done when" is the human-readable intent from the work item. The approved spec is the machine-checkable expression of it. The implementation workflow exits when the spec passes — not when it judges the prose criteria satisfied. The spec supersedes "Done when" as the operative exit condition.

## Spec-driven TDD convention

The implementation workflow is spec-first:

1. Agent proposes approach → **user approves (blocking gate)**
2. Agent writes test file → **user approves spec (blocking gate)**
3. Agent implements until tests pass
4. Done = tests passing

The test harness (framework, file location, naming) is language/framework-appropriate, agreed with the user, and documented in `architecture.md`. This agreement happens once per codebase, not per task.

## Workload tracking in git

Workload files are first-class documentation — tracked in git alongside the branch they describe.

- Location: `.swc/<folder>/` where folder = branch name with `/` replaced by `_`
- Files tracked: `workload.md`, `plan.md`, `notes.md`, `changelog.md`, `architecture.md`, `_meta.json`
- `.gitignore` allowlist pattern: `!.swc/`, `!.swc/*/`, `!.swc/**/*.md`
- Motivation: gives reviewers full context on intent, decisions, and task breakdown without ad-hoc tracking files cluttering `.claude/`

## todo-add skill — scenarios and requirements (2.7)

Deferred for later. Scenarios to handle when built:

### Task content
- Accept a title plus optional description and acceptance criteria (`**Done when:**`) inline or via prompt
- Title-only is the common case; description/criteria are optional but the skill should support them

### Adding a top-level task
- Append as the next numbered parent (e.g. 16 if 15 is last)
- Status defaults to `[ ]`

### Adding a subtask
- Append under the specified parent as the next N.x number
- If the parent had no subtasks, it becomes a container — status rolls up from the new subtask (stays `[ ]`)
- If the parent is already `[x]` (done), auto-update it to `[-]` — same rollup rule as todo-update; confirm in the output line rather than prompting

### File resolution
- Same logic as todo-update: most recently modified `todo-pr-N.md`, or explicit PR number if supplied

### Confirmation
- Single output line, e.g.: `✔ Added 2.7 under task 2. Parent task 2 updated to [-].`

### Out of scope for now
- Inserting mid-list (always append)
- Duplicate detection

---

## CLI tool for todo management

The todo skills (todo-list, todo-update, todo-add, etc.) could be backed by a small CLI tool rather than Claude reading/writing markdown directly. Benefits:

- Structured reads/writes — no risk of Claude mangling the file format
- Skills become thin wrappers: invoke CLI, present output
- CLI can be tested independently of Claude
- Could expose a `todo` command: `todo list`, `todo add`, `todo done 2.3`, `todo status`

Candidate approaches: a standalone shell script, a small Node/Python CLI, or a Bash wrapper. The CLI reads and writes `todo-pr-N.md` files; the skills handle presentation and user interaction.

Decision not yet made — captured here as a direction worth exploring when building todo-add (2.7). The `todo-update` skill was built without a CLI backing and works reliably for direct markdown edits — revisit for todo-add if complexity warrants it.

## MCP server for todo management

An MCP server is an alternative (or complement) to the CLI approach. Rather than skills invoking a shell command, they would call structured MCP tools — `todo_list`, `todo_update`, `todo_add`, `todo_status` — backed by a server that owns the file I/O.

Benefits over a plain CLI:

- Native tool calls — no shell invocation, no output parsing
- Structured input/output — schemas enforced at the protocol level
- Stateful if needed — server can hold parsed state across calls in a session
- Accessible to any agent or subagent in the session, not just the skill that invoked a command

The skills would become even thinner: call the MCP tool, present the result. The MCP server handles all reads and writes to `todo-pr-N.md` files.

Candidate implementation: a small Node or Python MCP server registered in `~/.claude/settings.json`. Could expose the same operations as the CLI — making the two approaches complementary rather than competing.

Decision not yet made — captured here as a direction worth exploring alongside the CLI tool idea.

## Packaging this workflow

The skills, ways, hooks, and agents that make up this workflow should be distributable as a unit. Options:

| Approach | Description |
|---|---|
| **Plugin** | Claude Code plugin bundling skills + ways + agents as a named package |
| **Dotfiles repo** | Fork of `~/.claude` with workflow pre-installed — user clones to get everything |
| **Install script** | Shell script that copies skills/ways/agents into `~/.claude` |
| **Project scaffold** | `todo-begin` skill writes the workflow files into `.claude/` at project setup time |

The plugin approach is cleanest for distribution (single install, versioned), but depends on Claude Code's plugin support. The install script is the most portable today.

Decision not yet made — worth revisiting when the workflow is stable enough to package.

## Open risks — execution workflow design

### R1: Brief quality assumption is fragile ✔ resolved
Gates 1 and 2 happen before the agent reads the codebase. The agreed approach may become unworkable once the agent encounters existing patterns or integration constraints — leading to silent deviation or a stuck agent.

**Resolution:** `swc_deliver` reads relevant codebase context before Gate 1 so approach agreement is grounded in reality.

### R2: Quality loop has no exit condition ✔ resolved
"Loop until quality bar is met" is undefined — no max iterations, no severity threshold, no escalation path. Risk of indefinite looping or compute waste.

**Resolution:** After findings on a second pass, escalate to the user. They can choose to accept the outstanding findings as documented tech debt and move on, or require another pass. The user holds the exit condition — the loop never runs more than twice without human judgement.

### R3: context.md quality is unenforced ✔ resolved
Iterative refinement depends on thorough context.md. Nothing enforces this. A sparse context.md means the next agent starts near-blind.

**Resolution:** The implementation workflow treats context.md sections as a required checklist before the agent can return. The agent cannot mark a pass complete without filling: agreed approach, decisions made (with reasoning), scope flags, and open questions.

### R4: TDD doesn't map cleanly to this project ✔ resolved
Gate 2 is a **spec approval gate**, not a test file gate. What constitutes a "spec" depends on the work item type, agreed with the user during the architecture discussion as part of planning.

| Work item type | Spec format |
|---|---|
| Code (CLI, scripts, MCP server) | Traditional test file — unit/integration, agreed framework |
| Skills (markdown instruction files) | Acceptance checklist — scenarios the skill must handle, verified by walkthrough |
| Ways (guidance files) | Way-matching test via `ways-tests` skill — score against target prompts, validate frontmatter |
| Agents | Behavioural spec — input/output scenarios, verified by spot-running the agent |

If a work item has no testable output (e.g. a pure docs update), the user and agent agree at Gate 1 that Gate 2 is a review checklist rather than a test file. Gate 2 still exists; it materialises as the agreed form.

`swc_deliver` and the implementation workflow describe spec types rather than assuming a test file. The architecture discussion answers: (1) what type is this work item, and (2) what does a passing spec look like for that type.

### R5: Quality loop is invisible to the user ✔ resolved
If the loop runs multiple times and still produces a poor result, the user finds out at Gate 3 with no visibility. Hard to debug or give useful feedback.

**Resolution:** Gate 3 always includes the reviewer findings from the final pass — the user sees the actual feedback, not just a pass/fail outcome. If the loop ran more than once, the handoff also shows what was flagged vs what was resolved across passes. The user sees the reasoning behind the result.

### Optimisation: "Approach needs revisiting" signal
If the agent discovers the agreed approach is wrong mid-implementation, it currently deviates silently or stops. A cleaner path: an explicit flag in the summary artifact that triggers Gate 1 again rather than surfacing as a vague Gate 3 failure.

## Ways and fresh agent sessions

Each subagent gets its own session, which means ways fire fresh for every subagent spawn. This is a feature, not a coincidence — it ensures that project preferences, code style, and workflow guidance are always present regardless of how far into a long main session we are.

Practical implications:

- **Implementation subagent** — ways fire on first relevant action (e.g. editing a file triggers `meta/tracking`, running a commit triggers `delivery/commits`). The subagent always gets clean, un-drifted guidance.
- **Review subagent** — same: `code/quality`, `code/security`, and other review-relevant ways fire fresh when it starts examining code.
- **Main session** — ways fire once per session. In a long session, guidance injected early may be far back in context. Spawning a subagent to handle a bounded task (rather than doing it inline) keeps the main session clean and ways fresh where they matter.

This is a reason to prefer subagents for implementation and review work even when the main session *could* do it — fresh ways are a form of context hygiene.

## Terminology: stage vs step

Workflow progression units are called **stages**, not steps.

**Why:** A stage has a clear entry/exit criteria — a stage gate — that must be satisfied before moving on. The word "stage" carries that gate semantics naturally. "Step" is reserved for the finer-grained activities *within* a stage, so using it at the workflow level creates ambiguous overlap.

**Applies to:**
- The progress banner — the `steps` parameter and concept should be `stages`
- `todo-begin` — the planning sequence is a series of stages (`context`, `intent`, `solution`, `delivery`, `breakdown`, `finalise`)
- Any future workflow config or tree visualisation

## Workflow tree with breadcrumb visualisation (10.x)

The current progress banner is flat — a single-level step list. Consider a tree structure for nested workflows where a top-level workflow (e.g. plan → execute → review → ship) contains sub-steps within each node. A breadcrumb would show both where you are in the outer workflow and where you are within the current inner workflow.

Example:
```
plan > context > intent > solution > ...
```

Open questions:
- Does the progress script extend to support a `parent` context, or is this a separate visualisation?
- How does this interact with the workflow config idea (10.2) — a tree config would be a natural extension of a flat step list.
- What is the right depth? Two levels (workflow > step) is probably enough.

Captured as a direction to consider alongside 10.2 before the visualisation layer solidifies.

## Workflow config — single source of truth for step names (10.2)

`todo-begin` currently defines the planning step names in two places: the `steps=` string passed to the progress banner, and the numbered step list. These will drift when steps are added or renamed.

A workflow config — a skill or script that owns the canonical step list — would give both `todo-begin` and the progress banner a single source to pull from. Open questions:

- Should this be a JSON block inside a skill, a standalone script that emits the config, or something else?
- Does it generalise beyond planning? `todo-execute` could have its own step list (e.g. `brief,implement,test,handoff`).
- If it's a script, can `todo-begin` call it to get the `steps=` value at runtime rather than hardcoding it?

Decision not yet made — captured here as task 1.3.3.2. Explore before adding more workflows that need progress banners.

## Workflow components inventory

**Skills** (built by this workflow)

| Skill | Status | Purpose |
|---|---|---|
| `swc_list` | ✔ done | Display task list with visual symbols |
| `swc_report-plan` | ✔ done | Summarise the `plan.md` doc |
| `swc_report-notes` | ✔ done | Summarise the `notes.md` doc |
| `swc_changelog` | ✔ done | Show recent changelog entries |
| `swc_report` | ✔ done | Full status report (plan + list + notes) |
| `swc_execute` | ✔ done → superseded | Spawn implementation subagent — replaced by `swc_deliver` |
| `swc_deliver` | □ not built | Delivery workflow — interactive gates, feedback loop, commit/push. Calls `swc_implement`; has no knowledge of agent mechanics. |
| `swc_implement` | □ not built | Agent spawning — receives approved brief from `swc_deliver`, spawns the implementation agent. Agent follows the implementation workflow. |
| `swc_update` | ✔ done | Update task status in file, with parent rollup |
| `swc_begin` | ◐ draft | Scaffold new workload + plan + architecture |
| `swc_init` | ✔ done | Write the five stub docs into a resolved workload folder |
| `review-subagent` | □ not built | Review findings format + skill |

**Ways** (relevant to this workflow)

| Way | Trigger | Relevance |
|---|---|---|
| `swc/` | keyword: swc/workload/work item | Core workload tracking guidance |
| `swc/workload-guard` | file edit: `workload.md` | Guards against direct status edits; enforces swc_update |
| `meta/subagents` | keyword: subagent/delegate/spawn | How to invoke subagents — directly used by swc_execute |
| `meta/todos` | context threshold >75% | Prompts task capture before compaction |

**Agents** (pre-existing, wired into this workflow)

| Agent | Role in this workflow |
|---|---|
| `code-reviewer` | Is the review subagent (6.2) — needs context wiring |
| `task-planner` | Candidate for breakdown step in `todo-begin` (3.1) |
| `Plan` (built-in) | Candidate for architecture analysis in `todo-begin` |

**Hooks** (planned, not yet built)

| Hook | Purpose |
|---|---|
| Pre-commit / pre-push | Confirm user is ready before git operations |

## Deliver workflow — stage design

### Stage split

| Stage | Content |
|---|---|
| **Requirements** | Intent clarification + high-level solution direction |
| **Specs** | Spec scenarios + acceptance criteria |
| **Solution design** | Implementation-level questions resolved with the user before the brief is sealed |
| **Implement** | Agent spawned with sealed brief — fully autonomous |

Requirements exits with agreed intent and a rough approach direction. Specs locks down acceptance criteria. Solution design is the final pre-spawn gate where implementation-level questions (design choices, ambiguities, integration decisions) are answered with the user — since the agent is fully autonomous once spawned and cannot ask mid-implementation.

**Rationale for solution design stage:** The implementation agent cannot converse with the user during execution. Any unresolved implementation question becomes either a silent deviation or a stuck agent. The solution design stage surfaces these questions explicitly before the brief is sealed, so the agent can proceed with confidence.

### Requirements stage behaviour

**Context loading** — two reads, both unconditional, no separate skill needed:
1. SWC workload docs: `plan.md`, `architecture.md`, `notes.md` from the active workload folder
2. Codebase context: derived from the work item description — grep for relevant symbols, read related files

**Opening move** — summarise what is already understood from the docs, invite the user to clarify or elaborate. If the work item description is thin (one line), flag this explicitly and ask for more detail before proceeding.

**Conversation flow:**
1. Summarise known intent from docs, invite elaboration
2. Ask questions until intent is clearly understood
3. Explore high-level solution direction — approach confirmation, not technical design
4. Confirm and write to task-specific requirements doc

**Scope boundary** — requirements covers *what and why* plus rough approach direction. Technical design details belong in specs or architecture.md.

### New task scenario

If the user triggers the deliver workflow for something not yet on the workload, the entry-point skill (`swc_workflow_deliver`) catches this before any stage runs. A work item is added and confirmed before proceeding. Requirements never starts without a resolved work item.

### Per-task document path

Task-specific files live at: `.swc/<folder>/workitems/<N>/`

No existing pattern — this is established fresh by the requirements stage. First file: `requirements.md`.

A skill for per-task doc naming, location, and format is planned but not yet built. Requirements will be the first thing to write into that path and will establish the convention used by specs and the implementation workflow.
