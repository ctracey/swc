---
description: Summarise session changes, update changelog and docs, commit, push, and optionally comment on the PR. Use when the user says "update docs & changelog", "wrap up this session", "prep to commit", "push this", "ship this", or invokes /swc-ship.
allowed-tools: Read, Write, Edit, Glob, Bash
---

# SWC Push

End-to-end session wrap-up: summarise changes, update docs, commit, push, and optionally comment on the PR.

## Steps

### 1. Summarise local changes

Run these in parallel:

```bash
git diff --stat HEAD          # files changed
git diff HEAD                 # full diff
git branch --show-current     # active branch
```

Also read `.swc/_meta.json` to find the active workload folder, then read `workload.md` for task context.

### 2. Present summary to user

Output a brief summary:
- Which files changed and what kind of changes (new skill, fix, refactor, docs)
- Which workload task(s) this relates to, if determinable
- One-line characterisation of the session's intent

Then ask:
> "Does that capture what changed this session? Anything to add or correct before I update the docs?"

Wait for confirmation or corrections.

### 3. Test check

If tests have been run and are passing since the last changes — continue without asking.

If unknown, or tests were run before the most recent changes: ask the user whether tests are passing before proceeding.

### 4. Update workload changelog

Append a new session entry to `changelog.md` in the active workload folder:

```markdown
## Session — <short description> `YYYY-MM-DD`

- <bullet per meaningful change>
- Motivation: <why, if not obvious>
```

Date is today. Description is a short phrase (not a sentence). Bullets are factual — what changed and why, not a restatement of file names.

### 5. Update other docs if needed

Check whether any other workload docs need updating:
- `notes.md` — if a decision or convention was settled this session
- `plan.md` — if scope changed or a goal was clarified
- `workload.md` — if task status changed (use `workload-update` for this, never edit directly)

Make only changes that reflect what actually happened. Don't pad.

### 6. Confirm ready to commit and push

Show the user what was written to the docs, then ask:
> "Docs updated. Ready to commit and push?"

Wait for confirmation. If they say no or want to make changes, address their feedback and re-confirm before proceeding.

### 7. Commit and push

Stage all changes (tracked and untracked), then commit and push:

```bash
git add .
git commit -m "<conventional commit message>"
git push
```

Write the commit message following the conventional commit format: `type(scope): description`. Focus on the why, not the what. Keep it one line unless a short body is genuinely needed.

Report the result:
> "Committed and pushed. [short sha] on [branch]."

### 8. PR comment

After pushing, check for an open PR:

```bash
gh pr view --json number,title 2>/dev/null
```

If no remote is configured or no PR exists, skip silently.

If a PR exists, draft a short comment (3–5 bullets, no preamble) and show it to the user:
> "Here's a draft PR comment — want me to post it?
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
- PR comment is always drafted and posted after the push — never before.
- PR comment is optional and user-confirmed — never post without showing the draft and getting approval.
- If no workload is active, write the changelog entry to the most recently modified `.swc/` folder and note it.
