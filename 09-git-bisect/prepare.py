#!/usr/bin/env python3
"""Create a standalone, repeatable completion-ring Git history."""

import argparse
import os
from pathlib import Path
import subprocess


STEPS = (
    "start the completion-ring model",
    "record the test input format",
    "note the ring index layout",
    "document the empty-ring case",
    "describe completion batching",
    "document the counter wrap case",
    "reuse the slot mask for pending counts",
    "record the completion service order",
    "document the polling fallback",
    "note the counter sampling order",
    "add an interrupt coalescing example",
    "describe the ring reset sequence",
    "record test environment assumptions",
    "extend the test command examples",
    "document the trace field names",
    "reorganize the review notes",
    "record the release checklist",
)


def create_history(destination, broken_build):
    destination.mkdir(parents=True, exist_ok=False)
    source = (Path(__file__).resolve().parent / "ring.c").read_text(encoding="utf-8")
    ring = destination / "ring.c"
    notes = destination / "lab-notes.txt"

    git_env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    git_env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)

    def git(*args, commit_time=None):
        env = git_env.copy()
        if commit_time:
            env.update(GIT_AUTHOR_DATE=commit_time, GIT_COMMITTER_DATE=commit_time)
        subprocess.run(["git", *args], cwd=destination, env=env, check=True)

    git("init", "--quiet", "--initial-branch=main")
    git("config", "user.name", "Lab Builder")
    git("config", "user.email", "lab@example.invalid")
    git("config", "core.hooksPath", os.devnull)
    git("config", "core.autocrlf", "false")
    git("config", "commit.gpgSign", "false")
    for step, title in enumerate(STEPS):
        revision_source = source
        if step >= 6:
            revision_source = source.replace("2u * RING_SIZE - 1u", "RING_SIZE - 1u")
        if broken_build and step == 5:
            revision_source = '#error "missing generated register definitions"\n' + revision_source
        ring.write_text(revision_source, encoding="utf-8")
        with notes.open("a", encoding="utf-8") as history:
            history.write(f"{step:02d} {title}\n")
        git("add", "ring.c", "lab-notes.txt")
        git("commit", "--quiet", "-m", f"v{step:02d} {title}",
            commit_time=f"2025-01-01T12:{step:02d}:00+00:00")
        git("tag", f"demo-v{step:02d}")
    git("tag", "demo-good", "demo-v00")
    git("tag", "demo-bad", "demo-v16")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="new directory for the demo repository")
    parser.add_argument("--broken-build", action="store_true",
                        help="make the revision directly before the regression unbuildable")
    args = parser.parse_args()
    create_history(args.destination.resolve(), args.broken_build)


if __name__ == "__main__":
    main()
