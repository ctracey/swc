# PR-5 Task Breakdown — Claude Code subagent workflow

## Tasks

- [-] **1. MAIN WORKFLOW**
  - [-] 1.1. **Launch new swc project**
     - [x] 1.1.1. Define reference doc conventions (`todo.md`, `plan.md`, `architecture.md`, structure)
     - [x] 1.1.2. Build the todo-begin skill (scaffold todo + plan + architecture from a documented plan)
     - [x] 1.1.3. Explicitly check and confirm git repo state with user as the first step of planning — branch, remote, open PRs — in a streamlined single exchange before proceeding
     - [x] 1.1.4. Split _notes and _changelog into separate docs
     - [x] 1.1.5. Define when and how notes/docs are updated in the workflow (post-task, post-review, or on handoff)
     - [x] 1.1.6. Switch from todo-pr tracking to .swc workload tracking, Decide tracking strategy (branch-only vs always vs never)
     - [ ] 1.1.7. Add cleanup step to ship flow if branch-only approach adopted
     - [ ] 1.1.8. Add `.swc/` to `.gitignore` during swc init — when `swc_init` scaffolds a new workload folder, check whether a `.gitignore` exists in the project root and append a `.swc/` entry if not already present, so workload tracking files are not accidentally committed to the project repo


  - [-] 1.2. **Workload management**
     - [x] 1.2.1. Build the todo-list skill
     - [x] 1.2.2. Build the todo-plan skill
     - [x] 1.2.3. Build the todo-notes skill
     - [x] 1.2.4. Build the todo-changelog skill
     - [x] 1.2.5. Build the todo-report skill
     - [x] 1.2.6. Build the todo-update skill
     - [ ] 1.2.7. Build the todo-add skill
     - [x] 1.2.8. Reconsider gitignore of todo files — decide if todo-pr-N files should be tracked in git
     - [x] 1.2.9. Rename this skillset
     - [x] 1.2.10. Move .swc to root of repo instead of inside .claude and consider tracking decoupling — the `todo-*` prefix ties skills to a specific file format; evaluate whether the skills should be renamed to reflect the workflow concept rather than the storage mechanism, and whether tracking (the todo files) should be decoupled from the workflow skills themselves
     - [ ] 1.2.11. Resolve workload guard / skill conflict — the guard hook fires on any direct edit to workload.md, including edits made by swc_workload-update itself; the guard and skill need a shared mechanism (e.g. a CLI tool or detectable marker) so sanctioned edits are not flagged
     - [x] 1.2.13. Build a workload rendering script — parse and display workload.md reliably via script (like progress.py for the banner) so swc_workload doesn't rely on manual LLM parsing, which drops sub-items at scale

      
  - [x] 1.3. **Planning workflow for new project**
     - [x] 1.3.1. Explore Aaron's ADR method and assess fit with this workflow
     - [x] 1.3.2. Streamline repo/branch suggestion in plan-context for new projects — when there is no existing repo or branch, guide the user through creating one as part of the first planning step rather than leaving it as an afterthought
     - [x] 1.3.3 workflow visualisation
         - [x] 1.3.3.1. Visualise workflow progress and active step — show which phase the current session is in (planning, executing, reviewing, shipping) and progress within it
         - [x] 1.3.3.2. Explore a workflow config skill or script — single source of truth for step names used by `todo-begin` and the progress banner, avoiding drift between the `steps=` string and the numbered step list
         - [x] 1.3.3.3. Build an abstracted workflow skill — generic workflow engine that any multi-stage process (planning, executing, reviewing, shipping) can use, rather than hardcoding stage logic in individual skills
         - [x] 1.3.3.4. Improve swc_plan-intent skill


  - [-] 1.4. **Task execution workflow**
     - [x] 1.4.1. **Address documented risks before building**
         - [x] 1.4.1.1. Resolve R4 — define testability approach for skills and ways
         - [x] 1.4.1.2. Define quality loop exit conditions and escalation path (R2)
         - [x] 1.4.1.3. Define context.md enforcement — required sections before agent can return (R3)
         - [x] 1.4.1.4. Define how swc_deliver grounds Gate 1 in codebase reality (R1)
         - [x] 1.4.1.5. Define quality loop visibility in Gate 3 handoff (R5)

     - [x] 1.4.2. **Delivery workflow — swc_deliver**
         - [x] 1.4.2.0. Build `swc_workflow_deliver` skill — entry-point skill that resolves the target work item, confirms with the user, and delegates to `swc-workflow-orchestrator` with the deliver stage definitions (stub created; needs full stage wiring)
         - [x] 1.4.2.1. Gate 1 — propose approach with codebase context, human agrees
         - [x] 1.4.2.2. Gate 2 — write test spec, human approves
         - [x] 1.4.2.3. Spawn implementation agent — assemble brief and delegate to swc_implement
         - [x] 1.4.2.4. Quality loop — orchestrate review agent + fresh impl agent until quality cleared
         - [x] 1.4.2.5. Gate 3 — human review handoff (tests passing, quality cleared, summary)
         - [x] 1.4.2.6. Commit and push on satisfaction
         - [x] 1.4.2.7. Update work item status during delivery workflow — mark `[-]` when delivery starts, `[x]` on successful completion
         - [x] 1.4.2.8. Add solution design stage to deliver workflow — insert a pre-spawn stage between specs and implement where implementation-level questions are resolved with the user before the agent brief is sealed
         - [x] 1.4.2.9. Add quality baseline stage to deliver workflow — run health checks after solution design, surface failures with scope relevance assessment, capture decisions in quality-baseline.md for the implementation agent brief

     - [x] 1.4.3. **Agent spawning — swc_implement**
         - [x] 1.4.3.1. Define brief assembly (work item + approach + spec + plan.md + architecture.md + context.md from prior passes + review findings)
         - [x] 1.4.3.2. Build swc_implement skill

     - [x] 1.4.4. **Implementation workflow**
         - [x] 1.4.4.1. Define the implementation workflow — what the agent follows
         - [x] 1.4.4.2. Define context.md format — append-only per pass, required sections
         - [x] 1.4.4.3. Define the rich summary artifact format
         - [x] 1.4.4.4. Build the implementation workflow skill
         - [x] 1.4.4.5. Implementation workflow — mark work item as in-progress at start of orient stage, done on successful summarise
         - [x] 1.4.4.6. Doc updates during implementation — agent updates README and relevant docs as part of each pass; define what belongs in README and consider a way to guide this
         - [x] 1.4.4.7. Consider agent progress messages to main session — milestone transparency for workflow stages, feedback loops, and loop iteration count (e.g. implement cycle 2/3)

     - [x] 1.4.5. **Review integration**
         - [x] 1.4.5.1. Define structured findings format for code-reviewer
         - [x] 1.4.5.2. Wire code-reviewer into delivery workflow quality loop
         - [x] 1.4.5.3. On acceptance, ensure broader docs are updated — architecture.md, tests, inline code comments, and any other artefacts affected by the work item, not just task-specific docs

     - [-] 1.4.6. **To consider**
         - [ ] 1.4.6.1. Implementation agent reflection — does this live in context.md or the summary artifact?
         - [x] 1.4.6.2. Agent identity — surface clear agent name to user so role boundary is always visible
         - [ ] 1.4.6.3. "Approach needs revisiting" signal — explicit flag in summary artifact that triggers Gate 1 again


- [-] **1.5. Batch skill acceptance**
     - [ ] 1.5.1. Walk through all swc skills and verify each against its acceptance criteria — identify gaps, inconsistencies, or stale placeholder content
     - [-] 1.5.2. Streamline permissions for swc usage — reduce or eliminate permission prompts when swc skills run

- [x] **1.6. swc_push improvements**
     - [x] 1.6.1. Improve swc_push to handle local repos — detect when no remote is configured and commit only (skip push and PR comment steps)

- [ ] **2. Advanced improvements**
  - [ ] 2.2. **Ways hygiene**
  - [ ] 2.2.1. Audit existing ways for content that belongs in a different scope or file — ensure new planning/subagent guidance lives in the right way rather than being patched into unrelated ways
  - [ ] 2.3. **Story mapping**
     - [ ] 2.3.1. Consider story mapping as a complement to task breakdown — logical user journey vs delivery roadmap with outcome/learning milestones
  - [ ] 2.4. **MCP service for todo list management**
     - [-] 2.4.1. Design MCP service interface — expose todo file read/write/query operations as MCP tools so any agent or skill can manage todos via a standard protocol rather than direct file I/O
     - [ ] 2.4.2. Implement MCP service
     - [ ] 2.4.3. Consider agent progress transparency via MCP — how workflow stage milestones, feedback loops, and loop iteration count are surfaced through the MCP interface rather than direct session messages
     - [ ] 2.4.4. Rename `workloads` key in `_meta.json` schema — update all skills and docs that read/write this key; decide on the new name as part of MCP schema design
  - [ ] 2.5. **Deliver batching**
     - [ ] 2.5.1. Consider delivering multiple work items in a single session — how batching interacts with gates, quality loops, and user attention
  - [ ] 2.6. **Deliver analysis mode**
     - [ ] 2.6.1. Consider a read-only analysis pass before delivery — understand codebase impact, surface risks, inform approach agreement at Gate 1
