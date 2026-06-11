## Pass 1 — 2026-06-11

- **Decision:** Used `${CLAUDE_SKILL_DIR}/../../.claude-plugin/plugin.json` to locate `plugin.json` from the `skills/version/` directory — resolves correctly to the plugin root regardless of the user's working directory. Verified manually.
- **Decision:** `mcp__swc-workload__version` returns `{ mcp, cli }` where `cli` can be null — MISSING guard handles both null and absent.
- **Decision:** Lightweight approach (no automated test file) — skill is a markdown instruction file; checklist verification is the agreed test strategy.
