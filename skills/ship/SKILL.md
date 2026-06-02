---
description: Summarise session changes, update changelog and docs, commit, push, and optionally comment on the PR. Use when the user says "update docs & changelog", "wrap up this session", "prep to commit", "push this", "ship this", or invokes /swc-ship.
allowed-tools: Read, Write, Edit, Glob, Bash, Skill, mcp__swc-workload__list, mcp__swc-workload__start, mcp__swc-workload__complete, mcp__swc-workload__reset
---

# SWC Push

End-to-end session wrap-up: summarise changes, update docs, commit, push, and optionally comment on the PR.

## Steps

### 0. Ensure swc skill permissions

Follow the `setup-permissions` skill.

### 0a. Verify MCP dependency

Follow the `mcp-check` skill. If the MCP is missing, the check delegates to `mcp-install` — stop here, ship needs MCP access to read workload state.

### 1. Summarise local changes

Run these in parallel:

```bash
git diff --stat HEAD          # files changed
git diff HEAD                 # full diff
git branch --show-current     # active branch
```

Also resolve the active context via `context-lookup`, then invoke `mcp__swc-workload__list` against its `absolute_path` for task context.

### 2. Branch check

If the current branch is `main` or `master`, stop and warn the user:

> "You're on `main`. Changes should be made on a feature branch so they can be reviewed via PR.
>
> Shall I create a branch now? If so, what should it be called? (or suggest one based on the changes)"

Wait for the user's response. If they provide a name (or accept a suggestion), create and switch to it:

```bash
git checkout -b <branch-name>
```

If they explicitly confirm they want to proceed on `main` anyway, continue — but note that the PR step will be skipped.

### 3. Present summary to user

Output a brief summary:
- Which files changed and what kind of changes (new skill, fix, refactor, docs)
- Which workload task(s) this relates to, if determinable
- One-line characterisation of the session's intent

Then ask:
> "Does that capture what changed this session? Anything to add or correct before I update the docs?"

Wait for confirmation or corrections.

### 4. Test check

If tests have been run and are passing since the last changes — continue without asking.

If unknown, or tests were run before the most recent changes: ask the user whether tests are passing before proceeding.

### 5. Update workload changelog

Append a new session entry to `changelog.md` in the active context folder:

```markdown
## Session — <short description> `YYYY-MM-DD`

- <bullet per meaningful change>
- Motivation: <why, if not obvious>
```

Date is today. Description is a short phrase (not a sentence). Bullets are factual — what changed and why, not a restatement of file names.

### 6. Check workload item status

Compare the changes from step 1 against the workload items. Identify any items that appear related (by description keyword or task context).

For each match found, ask the user:

> "These workload items appear related to the changes — should any be updated?
>
> Mark any as done, leave as-is, or skip? (e.g. '5.3 done', 'skip')"

Wait for a response. Apply any status changes against the resolved context's `absolute_path` (one call per item) — `mcp__swc-workload__start` for in-progress, `mcp__swc-workload__complete` for done, `mcp__swc-workload__reset` for not-started. If the user says skip or nothing matches, continue.

### 7. Update other docs if needed

Check whether any other context docs need updating:
- `notes.md` — if a decision or convention was settled this session
- `plan.md` — if scope changed or a goal was clarified
- Workload status — if task status changed, use `mcp__swc-workload__start` / `mcp__swc-workload__complete` / `mcp__swc-workload__reset` (never edit `workload.json` directly)

Make only changes that reflect what actually happened. Don't pad.

### 8. Confirm ready to commit and push

Show the user what was written to the docs, then ask:
> "Docs updated. Ready to commit and push?"

Wait for confirmation. If they say no or want to make changes, address their feedback and re-confirm before proceeding.

### 9. Commit and push

Stage all changes (tracked and untracked), then commit and push:

```bash
git add .
git commit -m "<conventional commit message>"
git push -u origin <branch>
```

Write the commit message following the conventional commit format: `type(scope): description`. Focus on the why, not the what. Keep it one line unless a short body is genuinely needed.

Report the result:
> "Committed and pushed. [short sha] on [branch]."

### 10. Open or update PR

If on `main`, skip this step silently.

Check for an existing PR:

```bash
gh pr view --json number,title,url 2>/dev/null
```

**If no PR exists**, draft a PR and show it to the user:

> "Here's a draft PR — want me to create it?
>
> **Title:** [short title based on changes]
>
> [draft body]"

The PR body should follow this structure:
```markdown
## Summary

- <bullet per meaningful change>

## Motivation

<one short paragraph on why — what problem this solves or what it enables>
```

If yes, create it:

```bash
gh pr create --title "<title>" --body "$(cat <<'EOF'
<body>
EOF
)"
```

Report the PR URL.

**If a PR already exists**, draft a short comment (3–5 bullets) and show it to the user:

> "PR already open — here's a draft comment, want me to post it?
>
> [draft comment]"

If yes, post it:

```bash
gh pr comment <number> --body "$(cat <<'EOF'
<draft comment>
EOF
)"
```

If no, skip silently.

## Key principles

- Changelog entries are session-level — one entry per session, even if multiple tasks touched.
- Commit happens only after the user confirms in step 7 — never before.
- Work should be on a feature branch — always check and offer to create one before proceeding.
- PR creation is always drafted and shown to the user before posting — never create without confirmation.
- If no workload is active, write the changelog entry to the most recently modified `.swc/` folder and note it.
