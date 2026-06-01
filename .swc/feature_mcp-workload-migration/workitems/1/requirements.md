# Requirements — 1: Plumbing

## Intent

Stand up everything the plugin needs to call `swc-workload-mcp` so the rewrites in items 3–8 have a working MCP to talk to. This is pre-work — no behavioural change to the plugin yet, only registration, permissions, docs, and a dependency-check pattern. First-time users must be guided to install the MCP rather than seeing opaque tool-call failures.

## Constraints

- The plugin treats the MCP as an external dependency — it does not bundle, install, or auto-configure the MCP server itself.
- Detection must distinguish "MCP not installed" from "MCP installed but broken" so the guide can be useful in both cases.
- The check must not add per-skill boilerplate — one invocation at the top of front-line skills, mirroring the `setup-permissions` pattern.
- Subsequent items (3–8) depend on this landing first — items 5.x will add `swc:mcp-check` invocations to their respective front-line skills; this item only wires it into `context-init` and creates the check + guide skills themselves.

## Out of scope

- Wiring `swc:mcp-check` into every workflow skill — that's covered alongside each skill's MCP rewrite in items 5.x.
- A `PreToolUse` hook fallback — deferred; may be added later if call sites slip through.
- Detection internals (probe call vs. tool-listing inspection) — solution-design call.

## Approach direction

Six sub-tasks under this item:

1. **Register the MCP server** at the project level so the tool namespace `mcp__swc-workload__*` becomes available. Mechanism TBD with user — likely `.mcp.json` at repo root, or `claude plugin install` style if the MCP also ships via the marketplace.
2. **Allowlist the MCP tools** in `skills/setup-permissions/SKILL.md` alongside the existing `Skill(swc:*)` entry, so MCP calls don't trigger per-call permission prompts.
3. **Document the install path** in `docs/usage.md` setup section, pointing at the MCP repo with prereqs and a quickstart.
4. **Add `swc:mcp-check`** — a reusable, silent skill that probes for MCP presence. Returns silently when present; hands off to the guide skill when missing or broken.
5. **Add `swc:mcp-install`** — a guide skill that walks the user through registering the MCP (link to docs, copy-paste commands, sanity-check).
6. **Wire `swc:mcp-check` into `context-init`** — proactive check at workload creation, so first-time users hit the guide before any tool call is attempted.

## Parked

- **MCP repo location / install command** — still need from user before 1.1 and 1.3 can be implemented.
- **`.mcp.json` shape vs `claude plugin install` mirror** — covered in solution-design once the MCP repo details are known.
- **Workload update needed** — sub-items 4–6 above are not yet in `workload.md`. Confirm with user before adding `1.4 mcp-check skill`, `1.5 mcp-install guide skill`, `1.6 wire mcp-check into context-init`.
- **Front-line skill list** — which skills count as "MCP-heavy front-line" and need the defensive check. Defer to each item's solution-design under items 5.x.
- **Hook fallback** — deferred per notes.md decision.
