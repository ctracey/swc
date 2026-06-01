# feature/mcp-workload-migration — Migrate workload management to swc-workload-mcp

## Work items

- [x] **1. Plumbing**
  - [x] 1.1. Register `swc-workload-mcp` server config (project‑level, mirrors plugin install)
  - [x] 1.2. Update `setup-permissions` to allowlist `mcp__swc-workload__*` alongside `Skill(swc:*)`
  - [x] 1.3. Update `docs/usage.md` setup section — add MCP install step pointing at MCP repo instructions
  - [x] 1.4. Add `swc:mcp-check` skill — reusable dependency check (silent on success, delegates to guide on miss)
  - [x] 1.5. Add `swc:mcp-install` skill — placeholder guide for missing MCP (prompts user; install instructions deferred)
  - [x] 1.6. Wire `mcp-check` into `context-init` and front‑line workflow skills (`workflowPlan`, `workflowDeliver`, `report`, `ship`)

- [x] **2. Delete superseded artefact‑mechanics skills**
  - [x] 2.1. Delete `skills/workload/` (including `workload.py`)
  - [x] 2.2. Delete `skills/workload-update/`
  - [x] 2.3. Delete `skills/workload_item-start/`
  - [x] 2.4. Delete `skills/context--workload/`

- [x] **3. Adapt `context-init`**
  - [x] 3.1. Drop the `workload.md` stub block from the skill steps
  - [x] 3.2. Add MCP `init` invocation against the resolved folder
  - [x] 3.3. Confirm the other five stubs (plan/architecture/notes/changelog/pipeline) still scaffold correctly

- [ ] **4. Reframe `context-lookup` output**
  - [ ] 4.1. Replace `workload.md` display strings with structured `Found context {...}` output
  - [ ] 4.2. Populate `workload: exists/missing` field via MCP `exists` call
  - [ ] 4.3. Update multi‑folder case to list candidates with workload status per row
  - [ ] 4.4. Fix misleading "No workload found under .swc/" → "No context found under .swc/"

- [ ] **5. Rewrite workflow touchpoints**
  - [ ] 5.1. `workflowPlan_context` — use MCP `exists` for existing‑workload detection
  - [ ] 5.2. `workflowPlan_delivery` — use MCP `add` to write skeleton items
  - [ ] 5.3. `workflowPlan_breakdown` — use MCP `add` for full breakdown, MCP `list` for playback
  - [ ] 5.4. `workflowDeliver` — use MCP `find`/`get`/`list(status=in-progress)`/`set_status(in-progress)`/`add` (for untracked work)
  - [ ] 5.5. `workflowDeliver_requirements` — use MCP `get` for item entry
  - [ ] 5.6. `workflowDeliver_implement` — use MCP `get` for agent brief
  - [ ] 5.7. `workflowDeliver_refine` — use MCP `get`
  - [ ] 5.8. `workflowDeliver_review` — use MCP `get`
  - [ ] 5.9. `workflowDeliver_accept` — use MCP `set_status(done)`
  - [ ] 5.10. `workflowImplement_orient` — use MCP `get` and `set_status(in-progress)`
  - [ ] 5.11. `report` — use MCP `list` for render, MCP next‑not‑started for NEXT STEP
  - [ ] 5.12. `ship` — use MCP `list` to match changes → items, MCP `set_status` for updates

- [ ] **6. Update spawned‑agent prompts**
  - [ ] 6.1. `workflowDeliver_implement` agent prompt — agent uses MCP instead of reading workload file
  - [ ] 6.2. `workflowDeliver_refine` agent prompt — same change
  - [ ] 6.3. Confirm spawned agents inherit MCP access (no extra prompts at spawn time)

- [ ] **7. Update narrative docs**
  - [ ] 7.1. `docs/plugin-design.md` — rename `workload.md` → `workload.json` in tree; note MCP ownership
  - [ ] 7.2. `README.md` — update folder‑layout references; mention MCP dependency in install path
  - [ ] 7.3. `skills/context--files/SKILL.md` — rename workload row in folder layout table, mark as MCP‑managed
  - [ ] 7.4. `skills/skill--naming/SKILL.md` — drop examples referencing removed workload skills (if any)

- [ ] **8. Tests**
  - [ ] 8.1. Remove tests exercising `workload.py` rendering and markdown checkbox parsing
  - [ ] 8.2. Decide MCP test strategy (mock vs real fixture) and document the choice
  - [ ] 8.3. Add coverage for the new MCP‑backed touchpoints in at least one workflow skill
