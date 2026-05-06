# Requirements — 1.4.4.4: Build the implementation workflow skill

## Intent

The implementation workflow is the sequence the implementation agent follows once spawned by `swc_workflow_deliver-implement`. Two of the four stage skills are placeholders and need real logic written. This work item fills in `orient` (complete brief-reading) and `implement` (full loop logic), making the agent-side workflow executable end-to-end.

The agent runs autonomously — no user interaction during execution. All decisions are documented in context.md; blockers that cannot be resolved within the brief cause the agent to stop and surface the gap.

## Constraints

- Agent-side only — no user interaction gates in these two stages
- `summarise` (stage 4) is already implemented and must not change
- `refine` (stage 3) stays as a placeholder — left for work item 1.4.5
- Must handle first-pass and subsequent-pass scenarios (context.md may or may not exist)
- Spec type varies by work item (code → test file; skills/ways → acceptance checklist) — the implement stage must work for both

## Out of scope

- `refine` stage implementation (1.4.5)
- `summarise` stage changes
- The delivery-side workflow (`swc_workflow_deliver-*`)
- Formal test spec and agent-based implementation — this work item is written directly given we are improving the agent workflow itself

## Approach direction

Rewrite `swc_workflow_implement-orient/SKILL.md` and `swc_workflow_implement-implement/SKILL.md` with complete, executable instructions. Both are markdown skill files — done when the instructions are clear, complete, and cover the key scenarios a real agent would encounter.

Each stage skill must include an `## Exit criteria` section. The orchestrator evaluates these to determine when a stage is complete and to emit the gate confirmation message — stage skills do not announce themselves or confirm completion inline.

## Decisions

- **Implement loop is scenario-driven:** the agent cycles through each scenario in `specs.md` one at a time — write test → implement until passing → update docs (context.md, README, relevant swc docs). After all scenarios pass, run the full suite to confirm no regressions. For skills/ways (acceptance checklist), the same cycle applies without automated test tooling.
- **Inner loop limit:** 3 fix cycles per scenario. If a scenario still fails after 3 attempts, the agent writes its current state to context.md (what was tried, what's failing, why it's stuck), writes a partial summary.md, and stops — surfacing the situation to the user for review rather than looping indefinitely.
