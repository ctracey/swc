#!/usr/bin/env python3
"""
Outputs JSON: { "swc": "<version>|N/A", "mcp_available": true|false }

mcp_available is true when the swc-workload MCP server is registered in any
Claude settings file visible from the current working directory or user home.
"""
import json
import os
import sys


def find_swc_version(skill_dir):
    plugin_json = os.path.normpath(os.path.join(skill_dir, "../../.claude-plugin/plugin.json"))
    try:
        with open(plugin_json) as f:
            return json.load(f).get("version", "N/A")
    except Exception:
        return "N/A"


def mcp_registered():
    candidates = [
        os.path.join(os.getcwd(), ".claude", "settings.json"),
        os.path.join(os.getcwd(), ".claude", "settings.local.json"),
        os.path.expanduser("~/.claude/settings.json"),
        os.path.expanduser("~/.claude/settings.local.json"),
    ]
    for path in candidates:
        try:
            with open(path) as f:
                data = json.load(f)
            servers = data.get("enabledMcpjsonServers", [])
            if "swc-workload" in servers:
                return True
        except Exception:
            continue
    return False


if __name__ == "__main__":
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(__file__)
    result = {
        "swc": find_swc_version(skill_dir),
        "mcp_available": mcp_registered(),
    }
    print(json.dumps(result))
