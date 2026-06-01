# Specs — 2: Delete superseded artefact‑mechanics skills

## Acceptance criteria

- `skills/workload/` no longer exists (folder and `workload.py` and `SKILL.md` gone).
- `skills/workload-update/` no longer exists.
- `skills/workload_item-start/` no longer exists.
- `skills/context--workload/` no longer exists.
- No other files under `skills/` are removed or modified.

## Error cases

- If any of the four folders is missing at the start, surface that — don't silently treat it as done.
