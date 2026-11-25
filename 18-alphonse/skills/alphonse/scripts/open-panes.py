#!/usr/bin/env python3
"""Open the fixed Alphonse test layout for one TOML plan."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import tomllib


def herdr(*args):
    output = subprocess.check_output(["herdr", *args], text=True)
    return json.loads(output)["result"] if output.strip() else {}


def machines_in(plan_file):
    with plan_file.open("rb") as source:
        blocks = tomllib.load(source).get("blocks", [])
    if not isinstance(blocks, list) or not blocks or not all(isinstance(block, dict) for block in blocks):
        raise ValueError("The TOML needs at least one [[blocks]] entry.")
    machines = [block.get("machine") for block in blocks]
    if any(not isinstance(machine, str) or not machine.strip() for machine in machines):
        raise ValueError("Each block needs a machine name.")
    return list(dict.fromkeys(machines))


def split(parent, direction, ratio, cwd, created):
    pane_id = herdr("pane", "split", parent, "--direction", direction, "--ratio",
                    str(ratio), "--cwd", cwd, "--no-focus")["pane"]["pane_id"]
    created.append(pane_id)
    return pane_id


def column(top, count, cwd, created):
    panes = [top]
    for remaining in range(count, 1, -1):
        panes.append(split(panes[-1], "down", 1 / remaining, cwd, created))
    return panes


def open_layout(caller, machines):
    caller_tab = caller["tab_id"]
    workspace = caller["workspace_id"]
    cwd = caller.get("foreground_cwd") or caller.get("cwd") or os.getcwd()
    created = []
    new_tabs = []
    positions = []

    try:
        if herdr("tab", "get", caller_tab)["tab"]["pane_count"] == 1:
            count = min(len(machines), 3)
            top = split(caller["pane_id"], "right", 0.5, cwd, created)
            positions.extend((caller_tab, pane) for pane in column(top, count, cwd, created))

        for number, start in enumerate(range(len(positions), len(machines), 6), 1):
            count = min(6, len(machines) - start)
            new = herdr("tab", "create", "--workspace", workspace, "--cwd", cwd,
                        "--label", f"Alphonse {number}", "--no-focus")
            tab_id = new["tab"]["tab_id"]
            left = new["root_pane"]["pane_id"]
            new_tabs.append(tab_id)
            created.append(left)
            if count == 1:
                positions.append((tab_id, left))
                continue

            right = split(left, "right", 0.5, cwd, created)
            left_panes = column(left, (count + 1) // 2, cwd, created)
            right_panes = column(right, count // 2, cwd, created)
            positions.extend((tab_id, pane) for pane in left_panes + right_panes)

        panes = {}
        for machine, (tab_id, pane_id) in zip(machines, positions, strict=True):
            herdr("pane", "rename", pane_id, machine)
            panes[machine] = {"tab_id": tab_id, "pane_id": pane_id}
        return {"panes": panes, "created_tabs": new_tabs}
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError, KeyboardInterrupt):
        for pane_id in reversed(created):
            subprocess.run(["herdr", "pane", "close", pane_id], stdout=subprocess.DEVNULL)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()
    if os.environ.get("HERDR_ENV") != "1" or not os.environ.get("HERDR_PANE_ID"):
        parser.error("Alphonse must start inside a Herdr pane.")
    try:
        caller = herdr("pane", "current", "--current")["pane"]
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError):
        parser.error("Alphonse could not resolve the calling Herdr pane.")
    try:
        result = open_layout(caller, machines_in(args.plan))
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError, KeyboardInterrupt) as error:
        parser.exit(1, f"Alphonse pane setup failed: {error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
