# Requirements — 1.5.2: Streamline permissions for swc usage

## Intent

swc skills currently trigger permission prompts for commands outside the `settings.json` allowlist — specifically `git`, `python3`, `gh`, and `mkdir`. The existing allowlist covers read-only shell tools (`cat`, `grep`, `ls`, etc.) but not the operations swc skills routinely perform. The goal is to add allowlist entries so normal swc workflow use runs without interrupting the user with prompts.

## Constraints

- Permissions live in `~/.claude/settings.json` under `permissions.allow`
- The allow pattern format is `Bash(command_prefix:*)` — matching the start of the shell command string
- Changes apply globally (all Claude Code sessions), not just swc sessions

## Out of scope

- Changing `defaultMode` — stays `default`
- Per-project or per-skill permission scoping (not supported by the current settings format)

## Approach direction

Add `Bash(...)` entries to the `permissions.allow` list in `settings.json`. The open question — to resolve in solution design — is how broadly to scope each command: broad (`git:*` allows all git subcommands) vs. selective (allow read-only subcommands, keep write operations like `git push` and `gh pr comment` gated). User leans toward broadly permissive but the trade-off needs surfacing before implementation.

## Parked

- Exact scope per command (broad vs. selective) — deferred to solution design stage
- Whether `python3` should be scoped to `~/.claude/**` scripts only or allowed broadly
