# Replay a saved bisection

[繁體中文](replay.md)

Follow the [exercise](README.en.md) to run the manual search in `ring-clean`. Save `ring-manual.log` and return to `main`. Run these commands in the same Git history.

```sh
git bisect replay "$lab_dir/ring-manual.log"
git bisect log
git bisect reset
```

The replay identifies v06 again. To confirm the behavior, rerun the external test script from the exercise. When handing off the investigation, include the good and bad commits, the test criteria, the bisection log, and the test output. [Git bisect log and replay](https://git-scm.com/docs/git-bisect#_bisect_log_and_bisect_replay)
