#!/usr/bin/env python3
"""Non-interactive resolution of the SWC context for the current branch.

Modes:
  probe [branch]            — inspect git + .swc state, emit JSON describing what to do next
  persist <branch> <folder> — upsert the branch→folder mapping in .swc/_meta.json

The script never calls MCP and never prompts the user. The skill keeps those
responsibilities and uses this script to collapse the non-interactive
filesystem/git checks into a single tool call.

Probe output shapes (one of):
  {"status": "resolved",
   "context": {"type": "branch"|"folder", "source": "...", "name": "...",
               "location": ".swc/...", "absolute_path": "/abs/.../.swc/..."},
   "from": "meta"|"scan"}

  {"status": "needs_user_input",
   "reason": "not_a_git_repo"|"default_branch"|"single_folder_no_match"|"multi_folder",
   "current": {"branch": "..."|null, "derived_folder": "..."},
   "candidates": [{"name": "...", "location": "...", "absolute_path": "...", "match": bool}, ...]}

  {"status": "no_workload",
   "current": {"branch": "...", "derived_folder": "..."}}

`absolute_path` is what MCP calls require for `workload`. The CLI does not
resolve folder names or relative paths — always pass the absolute form.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


DEFAULT_BRANCHES = {"main", "master"}


def is_git_repo(cwd: str) -> bool:
    try:
        r = subprocess.run(
            ["git", "-C", cwd, "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, check=False,
        )
        return r.returncode == 0 and r.stdout.strip() == "true"
    except Exception:
        return False


def current_branch(cwd: str) -> str | None:
    try:
        r = subprocess.run(
            ["git", "-C", cwd, "branch", "--show-current"],
            capture_output=True, text=True, check=False,
        )
        if r.returncode == 0:
            return r.stdout.strip() or None
    except Exception:
        pass
    return None


def derive_folder(name: str) -> str:
    return name.replace("/", "_")


def list_swc_folders(cwd: str) -> list[str]:
    swc = Path(cwd) / ".swc"
    if not swc.exists():
        return []
    return sorted(
        p.name for p in swc.iterdir()
        if p.is_dir() and not p.name.startswith(".")
    )


def read_meta(cwd: str) -> dict:
    meta_path = Path(cwd) / ".swc" / "_meta.json"
    if not meta_path.exists():
        return {}
    try:
        return json.loads(meta_path.read_text())
    except Exception:
        return {}


def write_meta(cwd: str, meta: dict) -> None:
    swc = Path(cwd) / ".swc"
    swc.mkdir(parents=True, exist_ok=True)
    (swc / "_meta.json").write_text(json.dumps(meta, indent=2) + "\n")


def abs_swc_path(cwd: str, folder: str) -> str:
    return str((Path(cwd).resolve() / ".swc" / folder))


def probe(cwd: str, branch_arg: str | None) -> dict:
    if not is_git_repo(cwd):
        return {
            "status": "needs_user_input",
            "reason": "not_a_git_repo",
            "current": {"branch": None, "derived_folder": Path(cwd).name},
            "candidates": [],
        }

    branch = branch_arg or current_branch(cwd)
    if not branch:
        return {
            "status": "needs_user_input",
            "reason": "not_a_git_repo",
            "current": {"branch": None, "derived_folder": Path(cwd).name},
            "candidates": [],
        }

    derived = derive_folder(branch)

    if branch in DEFAULT_BRANCHES:
        return {
            "status": "needs_user_input",
            "reason": "default_branch",
            "current": {"branch": branch, "derived_folder": derived},
            "candidates": [],
        }

    meta = read_meta(cwd)
    workloads = meta.get("workloads", {})
    if branch in workloads:
        folder = workloads[branch]
        return {
            "status": "resolved",
            "context": {
                "type": "branch",
                "source": branch,
                "name": folder,
                "location": f".swc/{folder}",
                "absolute_path": abs_swc_path(cwd, folder),
            },
            "from": "meta",
        }

    folders = list_swc_folders(cwd)
    if not folders:
        return {
            "status": "no_workload",
            "current": {"branch": branch, "derived_folder": derived},
        }

    if len(folders) == 1:
        only = folders[0]
        if only == derived:
            return {
                "status": "resolved",
                "context": {
                    "type": "branch",
                    "source": branch,
                    "name": only,
                    "location": f".swc/{only}",
                    "absolute_path": abs_swc_path(cwd, only),
                },
                "from": "scan",
            }
        return {
            "status": "needs_user_input",
            "reason": "single_folder_no_match",
            "current": {"branch": branch, "derived_folder": derived},
            "candidates": [
                {
                    "name": only,
                    "location": f".swc/{only}",
                    "absolute_path": abs_swc_path(cwd, only),
                    "match": False,
                }
            ],
        }

    return {
        "status": "needs_user_input",
        "reason": "multi_folder",
        "current": {"branch": branch, "derived_folder": derived},
        "candidates": [
            {
                "name": f,
                "location": f".swc/{f}",
                "absolute_path": abs_swc_path(cwd, f),
                "match": f == derived,
            }
            for f in folders
        ],
    }


def persist(cwd: str, branch: str, folder: str) -> None:
    meta = read_meta(cwd)
    workloads = meta.get("workloads", {})
    workloads[branch] = folder
    meta["workloads"] = workloads
    write_meta(cwd, meta)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)

    p_probe = sub.add_parser("probe", help="inspect git + .swc state, emit JSON")
    p_probe.add_argument("branch", nargs="?", default=None)

    p_persist = sub.add_parser("persist", help="upsert branch→folder mapping in .swc/_meta.json")
    p_persist.add_argument("branch")
    p_persist.add_argument("folder")

    args = parser.parse_args()
    cwd = os.getcwd()

    if args.mode == "probe":
        print(json.dumps(probe(cwd, args.branch)))
    elif args.mode == "persist":
        persist(cwd, args.branch, args.folder)


if __name__ == "__main__":
    main()
