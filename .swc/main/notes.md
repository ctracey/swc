# Notes

## Decisions

## Risks

## References

## Ideas

### WI-6: Dynamic skill discovery & installation

The goal is a skill that surfaces relevant skills from the Claude public marketplace based on the current project's tech stack, then installs accepted ones project-scoped via the local marketplace CLI.

**Flow:**
1. Detect stack — read well-known files (package.json, requirements.txt, Cargo.toml, go.mod, Gemfile, pyproject.toml, etc.) to infer languages, frameworks, and tools in use.
2. Marketplace lookup — query the Claude public marketplace for skills tagged to the detected stack. Return a ranked list of suggestions with name, description, and marketplace listing URL.
3. User acceptance — present suggestions interactively; user accepts or rejects each one. Batch accepted skills for install.
4. Install — for each accepted skill: add the plugin to the local marketplace via its public listing, then install it with `--scope project`.

**Key constraints:**
- Should not auto-install without explicit user confirmation per skill.
- Stack detection should be non-destructive (read-only file inspection).
- Install must use the local marketplace CLI (not manual file copying) so versioning and dependencies are tracked correctly.
- Project-scoped install keeps the skill local to this repo — no global pollution.

**Open questions:**
- Does the public marketplace expose a queryable API, or does lookup require scraping / a known index?
- How does the local marketplace CLI accept a public listing reference — by URL, slug, or ID?
- Should re-running the skill skip already-installed skills or offer an upgrade path?

