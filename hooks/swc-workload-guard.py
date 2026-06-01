#!/usr/bin/env python3
"""PreToolUse hook for mcp__swc-workload__* calls.

Resolves the expected workload context from the project's .swc/_meta.json and
the current git branch, then validates the call's `workload` argument against
that. Denies the call with an informative message if:

  - no .swc/_meta.json exists,
  - the current branch has no mapping in _meta.json,
  - the call's workload arg doesn't match the resolved context.

Hook spec: Claude Code PreToolUse — reads JSON on stdin, writes optional JSON
on stdout. Exit code is always 0; the JSON's permissionDecision controls
allow/deny.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def emit(decision: str, reason: str | None = None) -> None:
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
        }
    }
    if reason:
        payload["hookSpecificOutput"]["permissionDecisionReason"] = reason
    print(json.dumps(payload))
    sys.exit(0)


def allow() -> None:
    sys.exit(0)


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except Exception:
        allow()
        return

    tool_name = event.get("tool_name", "")
    if not tool_name.startswith("mcp__swc-workload__"):
        allow()
        return

    cwd = event.get("cwd") or os.getcwd()
    tool_input = event.get("tool_input") or {}
    given = tool_input.get("workload")

    meta_path = Path(cwd) / ".swc" / "_meta.json"
    if not meta_path.exists():
        emit(
            "deny",
            "No .swc/_meta.json in this project. Run /swc:workflowPlan or "
            "/swc:context-init to establish an SWC context before MCP calls.",
        )

    try:
        meta = json.loads(meta_path.read_text())
    except Exception:
        emit(
            "deny",
            "Could not parse .swc/_meta.json — confirm it is valid JSON before continuing.",
        )

    workloads = meta.get("workloads", {})

    try:
        branch = subprocess.check_output(
            ["git", "-C", cwd, "branch", "--show-current"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        branch = ""

    expected_folder = workloads.get(branch) if branch else None

    if not expected_folder:
        emit(
            "deny",
            f"No SWC context mapped for branch `{branch or '(none)'}` in "
            ".swc/_meta.json. Invoke /swc:context-lookup to resolve, or "
            "/swc:workflowPlan to start a new context, before making MCP calls.",
        )

    expected_path = str((Path(cwd) / ".swc" / expected_folder).resolve())

    given_str = str(given) if given is not None else ""
    given_normalised = (
        str(Path(given_str).resolve()) if given_str and Path(given_str).is_absolute() else given_str
    )

    if given_str == expected_folder or given_normalised == expected_path:
        allow()

    if not given_str:
        emit(
            "deny",
            f"Tool call missing `workload` argument. Expected: `{expected_folder}` "
            f"(resolved from branch `{branch}`).",
        )

    emit(
        "deny",
        f"Workload mismatch: called with `workload: {given_str}` but the resolved "
        f"context for branch `{branch}` is `{expected_folder}` "
        f"(at .swc/{expected_folder}/). Use the resolved context, or switch branch "
        "/ re-run /swc:context-lookup if a different workload is intended.",
    )


if __name__ == "__main__":
    main()
