# Requirements — 1.4.5: Review integration

## Intent

Wire a code-quality review step into the swc delivery workflow. The implementation agent focuses on implementing — it no longer self-reviews. After the agent returns, the deliver workflow spawns `swc_code-reviewer` to review the code, writes findings to a structured file, and presents them to the user. The user decides to resolve findings (loop back to implement) or accept them as tech debt (document and advance). Gate 3 sees the full pass history and final review state before the human approves.

## Constraints

- `swc_code-reviewer` is a new agent — the existing `code-reviewer` agent is not modified
- Code work items only — skills, ways, and docs are out of scope for this reviewer
- Findings are written to `.swc/<folder>/workitems/<N>/code-review-findings.md`, fresh each review pass (not appended — prior findings should be resolved)
- Tech debt is appended to `.swc/<folder>/tech-debt.md` (workload-level, accumulates across work items)
- `summary.md` drops the `## Review findings` section — findings live in `code-review-findings.md`
- `summary.md` is appended per implementation pass (each pass adds a dated section); not overwritten
- The refine stage moves out of the implement workflow and into the deliver workflow — it is interactive (user gate)
- The implement workflow loses refine: orient → implement → summarise only

## Out of scope

- Modifying the existing `code-reviewer` agent
- Reviewing skills, ways, markdown, or documentation work items
- Automated resolution of findings (the implementation agent applies fixes, it does not decide which findings to resolve)
- GitHub PR integration

## Approach direction

Three deliverables:

1. **`agents/swc_code-reviewer.md`** — new agent inspired by `code-reviewer`, but swc-aware: receives work item brief + summary artifact + code context, reviews for quality/SOLID/security/tests, writes structured findings to `code-review-findings.md`, returns.

2. **`swc_workflow_deliver-refine` skill** — new deliver workflow stage (replacing the implement-refine placeholder). Spawns `swc_code-reviewer`, reads findings, presents to user: resolve (loop back to implement) or tech debt (append to `tech-debt.md` and advance). Max two autonomous loops before escalating.

3. **Deliver workflow wiring** — the deliver workflow orchestrator gains a `refine` stage after `implement`. The implement workflow skill loses its `refine` stage. The `## Review findings` section is removed from the `summary.md` format in `notes.md`.

Deliver stage sequence after this work:
```
requirements → specs → solution-design → implement → refine → Gate 3
```
Where refine = review + user decision + optional re-implement loop.

## Parked

- 1.4.5.3 (broader doc updates on acceptance) — architecture.md, inline comments, other affected artefacts. Covered under this item but detail deferred to specs.
- Whether `tech-debt.md` needs a per-finding header format (work item number, date, severity) — to be defined in specs.
- The `## Review findings` section removal from `summary.md` is a format change to `notes.md` — small but needs to happen as part of this work.
