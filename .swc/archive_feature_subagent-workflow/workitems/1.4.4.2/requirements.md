# Requirements — 1.4.4.2: Define context.md format

## Intent

`context.md` is the running memory artifact that travels between fresh agent sessions. The implementation agent is fully autonomous once spawned — it makes decisions, hits blockers, and may add things not in the original brief. Without a living record, a new session reinvents the wheel and the user can't understand what the agent did autonomously without reading all the code. This work item defines the canonical format for context.md so the implementation workflow skills can enforce it consistently.

## Constraints

- Must be lightweight — written at decision points throughout execution, not as a documentation event at the end
- Only captures what isn't already derivable from code, tests, requirements.md, specs.md, or solution.md
- Append-only across passes — each agent run adds a new dated section; prior passes are never overwritten
- At least one entry required per pass — if nothing diverged, say so explicitly

## Out of scope

- Defining the summary artifact format (1.4.4.3)
- Building the implementation workflow skill (1.4.4.4)

## Approach direction

Define the format as a canonical reference, then update the orient and summarise stage skills to enforce it — orient opens a new pass section at the start, summarise verifies a pass section exists before the agent exits. The format itself lives in notes.md as the authoritative definition, referenced by the skill files.

## What belongs in a pass entry

Entries are bullets covering any of these categories (self-labelled, no mandatory subsections):

- **Unilateral decisions** — chose X over Y, wasn't in solution.md, here's why
- **Assumptions to verify** — user should sanity-check before accepting the work
- **Blockers** — resolved with a low-risk guess (captured for user review) or unresolved (agent stopped, user decision needed)
- **Good-practice additions** — agent added something beyond scope because it was the right thing to do
- **Failed approaches** — tried X, didn't work, here's what was learned
- **Current state** — where things were left if the pass ended incomplete
