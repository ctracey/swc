# Changelog

## Session — workload tidy `2026-05-14`

- Added workload item 5.5: swc:ship cleanup for template-only context docs

## Session — swc skill permissions `2026-05-14`

- Added `setup-permissions` skill: grants `Skill(swc:*)` and `Read` for the skills directory, written to `.claude/settings.json` on first use per project
- Added Step 0 to 9 front-line skills delegating to `setup-permissions` — logic centralised, no duplication
- Seeded `.claude/settings.json` with permission rules as a live demo
- Marked workload item 3.1 done

