# Specs — 1.4.4.2: Define context.md format

## Acceptance criteria

- `notes.md` contains a canonical `context.md` format definition that supersedes the existing draft sketch (lines ~137–165)
- The format specifies: pass header with date, bullet entries, no mandatory subsections, one entry minimum per pass
- The six entry categories are documented with clear guidance: unilateral decisions, assumptions to verify, blockers (guessed vs stopped), good-practice additions, failed approaches, current state
- The `orient` stage skill opens a new dated pass section at the start of each agent run
- The `summarise` stage skill verifies a pass section exists before the agent exits; if content is sparse or missing, it prompts the agent to fill it rather than letting it exit silently
- A new agent reading context.md from a prior pass can understand what was tried, decided, and where things were left — without reading the code

## Error cases

- The summarise skill must not allow the agent to exit with a missing or empty pass section — this is the primary failure mode that undermines resumability
