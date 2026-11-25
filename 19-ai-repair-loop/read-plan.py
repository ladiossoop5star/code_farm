#!/usr/bin/env python3
"""Extract numbered Bash blocks from an Edward Test DSL plan."""

from pathlib import Path
import re
import subprocess
import sys
import tomllib


def write_plan(source, destination):
    with source.open("rb") as file:
        plan = tomllib.load(file)
    criteria = plan.get("pass_criteria")
    if not isinstance(criteria, str) or not criteria.strip():
        raise ValueError("pass_criteria must contain the acceptance criteria")
    blocks = plan.get("blocks")
    if not isinstance(blocks, list) or not blocks:
        raise ValueError("declare at least one [[blocks]] entry")

    entries = []
    for index, block in enumerate(blocks, 1):
        if not isinstance(block, dict):
            raise ValueError(f"block {index} must be a TOML table")
        machine = block.get("machine")
        commands = block.get("commands")
        if not isinstance(machine, str) or not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]*", machine):
            raise ValueError(f"block {index} has an invalid machine name")
        if not isinstance(commands, str) or not commands.strip() or "\0" in commands:
            raise ValueError(f"block {index} must contain shell commands")

        number = f"{index:02d}"
        script = destination / f"{number}.sh"
        script.write_text(commands, encoding="utf-8")
        if subprocess.run(["bash", "-n", str(script)], check=False).returncode:
            raise ValueError(f"block {index} has invalid Bash syntax")
        entries.append(f"{number}\t{machine}\n")

    (destination / "blocks.tsv").write_text("".join(entries), encoding="utf-8")
    (destination / "pass-criteria.txt").write_text(criteria.rstrip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    try:
        write_plan(Path(sys.argv[1]), Path(sys.argv[2]))
    except (OSError, ValueError) as error:
        sys.exit(f"edward: {error}")
