# Solution Design — 1.4.4.2: Define context.md format

## Approach

Update `notes.md` with the canonical context.md format definition (replacing the existing draft sketch at lines ~137–165). Then update the orient and summarise stage skills with only the context.md-specific logic — orient opens a new dated pass section at the start of each run; summarise enforces a pass section exists before exit. The broader stage logic (brief reading in orient, summary artifact in summarise) remains as placeholder for 1.4.4.4.

## Technical decisions

- **Scope boundary:** only context.md-specific behavior added to orient and summarise. Everything else stays placeholder. `implement-implement` is untouched.
- **Format location:** canonical definition lives in `notes.md` as the authoritative reference. The skill files reference this convention without duplicating it.
- **Orient behavior:** check if context.md exists (may be first pass), read prior passes if present, append a new `## Pass N — YYYY-MM-DD` section header. Pass number derived by counting existing `## Pass` headers + 1.
- **Summarise behavior:** verify that the current pass section has at least one bullet entry. If empty or missing, prompt the agent to fill it before exiting — do not silently pass.

## Deferred

- Full orient stage logic (reading brief docs, understanding starting point) — 1.4.4.4
- Full summarise stage logic (writing summary artifact) — 1.4.4.4
- Implement stage inner loop and context.md entry guidance — 1.4.4.4
