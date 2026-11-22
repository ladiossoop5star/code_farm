# Git worktree and reflog exercise

[繁體中文](README.md)

Keep an unfinished firmware change in its own directory while you fix a timeout on an older release. The simulated DUT stays BUSY, but the old code returns READY. After fixing the bug, move the hotfix branch back to the old release and recover the fix from that branch's reflog.

You need Git, Python 3.11 or later, GNU Make, and a C compiler. The manual exercise uses Bash and GNU sed. A local C program simulates the DUT.

## Verify the full exercise

Run from this material directory:

~~~sh
python3 verify.py
~~~

Expect FAIL on the old version, PASS after the fix, and PASS after recovery. The checker also confirms that the fix disappears from `git log --all` after the branch moves, that the reflog identifies the same commit, and that cleanup preserves the original diff and binary.

## Follow along with the video

Run each step in the same Bash session, starting from this material directory. The exercise creates a disposable repository for the branch move and forced worktree removal.

### 1. Keep the unfinished edits and check out the old release

~~~sh
lab_dir=$(mktemp -d)
python3 verify.py --prepare "$lab_dir"
cd "$lab_dir/firmware"

git status --short --branch
git diff -- wait.c
ls -l out/selftest
git worktree add -b hotfix/ready-timeout ../firmware-hotfix release/1.x
git worktree list
~~~

The original directory has `feature/probe-log` and an uncommitted edit to log the status read by probe. The hotfix starts on `release/1.x`.

### 2. Reproduce the bug, fix it, and commit

~~~sh
cd ../firmware-hotfix
if make test; then
    echo "Expected the old version to fail" >&2
    exit 1
fi
sed -i '/^    return READY;$/s/READY/TIMEOUT/' wait.c
git diff -- wait.c
make test
ls -l out/selftest ../firmware/out/selftest
git add wait.c
git commit -m "Return TIMEOUT when DUT stays BUSY"
git log -1 --oneline
~~~

The first run prints `FAIL: DUT stayed BUSY but wait_ready returned READY`. After changing the return value when the loop runs out, the same test prints `PASS: READY after polling, TIMEOUT when BUSY`. Each worktree has its own `out/selftest`.

### 3. Move the demo hotfix branch back to the old release

Detach from the hotfix branch before moving it:

~~~sh
git switch --detach release/1.x
git branch -f hotfix/ready-timeout release/1.x
git branch -v
git switch hotfix/ready-timeout
git log -1 --oneline
git log --all --oneline
~~~

The hotfix branch now points to `Add firmware READY self-test`. The commit titled `Return TIMEOUT when DUT stays BUSY` is absent from the branch history and from `git log --all`.

### 4. Recover the commit and rerun the test

~~~sh
git reflog show -2 hotfix/ready-timeout
git show 'hotfix/ready-timeout@{1}' -- wait.c
git switch -c rescue/ready-timeout 'hotfix/ready-timeout@{1}'
git log -1 --oneline
make -B test
~~~

In this exercise, `@{1}` is the position before the move. Use `git show` to verify the message and the diff from `READY` to `TIMEOUT`. The rescue branch makes the fix visible in `git log` again, and the test passes after rebuilding.

### 5. Clean up the hotfix worktree

~~~sh
printf 'make test: PASS\n' > run-note.txt
git status --short --branch
cd ../firmware
if git worktree remove ../firmware-hotfix; then
    echo "Expected Git to refuse the untracked file" >&2
    exit 1
fi
git worktree remove --force ../firmware-hotfix
git worktree list
git show rescue/ready-timeout -- wait.c
git status --short --branch
git diff -- wait.c
ls -l out/selftest
~~~

Git refuses the first removal because `run-note.txt` is still present. In this exercise, the note and hotfix build artifacts are disposable. With `--force`, the worktree is removed along with its uncommitted files. The rescue branch still contains the fix, and the original working directory still has the original edits and binary.
