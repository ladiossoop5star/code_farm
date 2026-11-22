# Episode 09 · Find a completion-ring regression with git bisect

[繁體中文](README.md)

Use Git, Python 3, a POSIX shell, and a C compiler to build two independent exercise repositories. This C model has 8 slots and should report 8 pending completions when full. Commit v06 changes the count mask from 4 bits to 3, so a full ring reads as 0.

Run these commands from the exercise directory. Both repositories live in a fresh temporary directory, and the test runner stays outside them so every checkout uses the same test.

```sh
fixture_dir=$(pwd)
lab_dir=$(mktemp -d)
python3 prepare.py "$lab_dir/ring-clean"
python3 prepare.py --broken-build "$lab_dir/ring-skip"
cd "$lab_dir/ring-clean"
```

## Check the endpoints and mark results by hand

```sh
git switch --detach demo-good
sh "$fixture_dir/check-ring.sh"
git switch --detach demo-bad
sh "$fixture_dir/check-ring.sh"
git switch main
git bisect start demo-bad demo-good
```

At each step run `sh "$fixture_dir/check-ring.sh"`, then mark the result. The exercise history gives this sequence.

| Commit | Count when full | Mark |
| --- | ---: | --- |
| v08 | 0 | `git bisect bad` |
| v04 | 8 | `git bisect good` |
| v06 | 0 | `git bisect bad` |
| v05 | 8 | `git bisect good` |

Git identifies v06 as the first bad commit. Save the log before returning to your starting point.

```sh
git bisect log > "$lab_dir/ring-manual.log"
git bisect reset
```

## Automate the search

```sh
git bisect start demo-bad demo-good
git bisect run sh "$fixture_dir/check-ring.sh"
git bisect log > "$lab_dir/ring-auto.log"
git bisect reset
```

The runner returns 0 for a pass, 1 for a confirmed reproduction, 125 for a commit that cannot build, or 128 for an environment error or an unrelated failed check. Verify the expected results at both endpoints before starting. [Git bisect run exit codes](https://git-scm.com/docs/git-bisect#_bisect_run)

## Skip a commit that cannot build

```sh
cd "$lab_dir/ring-skip"
git bisect start demo-bad demo-good
git bisect run sh "$fixture_dir/check-ring.sh"
git bisect log > "$lab_dir/ring-skip.log"
git bisect reset
```

v05 cannot build in this history, so Git lists v05 and v06 as candidates. Use `git show` to compare them and record why v05 was skipped. To identify the first bad commit precisely, restore a compatible build environment and run the same test against v05.

## Verify the first bad commit

```sh
cd "$lab_dir/ring-clean"
git switch --detach 'demo-v06^'
sh "$fixture_dir/check-ring.sh"
git switch --detach demo-v06
sh "$fixture_dir/check-ring.sh"
git show demo-v06 -- ring.c
git switch main
```

The parent of v06 reports 8, and v06 reports 0. Inspect the patch that reduces the count mask to 3 bits. Then restore the earlier mask in a new exercise worktree and run the same test again.

```sh
git worktree add --detach "$lab_dir/ring-fix" demo-v06
git -C "$lab_dir/ring-fix" restore --source='demo-v06^' -- ring.c
(cd "$lab_dir/ring-fix" && sh "$fixture_dir/check-ring.sh")
```

A full ring again reports 8. This exercise proves the behavior for the same input in the model. Check the hardware specification for the counter layout and sampling rules on a real device.

[Replay a saved bisection](replay.en.md)
