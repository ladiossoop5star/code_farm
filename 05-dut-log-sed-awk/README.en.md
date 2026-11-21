# Summarize DUT test logs with sed and awk

[繁體中文](README.md)

Use the QEMU power-button self-test logs from the episode to practice selecting lines, replacing text, extracting fields, and counting by group. Each run has its own raw console log. The ledger retains the source path for every result.

Run the commands below from this directory. The examples use `sh`, GNU `sed`, `awk`, `grep`, and `diff`.

## Start with one log

~~~sh
sed -n '3p' raw/before/01.log
sed -n 's/^DT status=/status=/p' raw/before/01.log
sed -n 's/^DT status=/status=/p' raw/before/01.log | awk -F= '{print $2}'
~~~

The commands print `DT status=disabled`, `status=disabled`, and `disabled`, respectively. In the last command, `-F=` splits fields at the equals sign and `$2` selects the second field. The raw logs retain the original CRLF line endings. The batch rules in `normalize.sed` strip the trailing carriage return.

## Process both batches

Each row of `runs.tsv` describes a run with its batch and raw log path. `build-ledger.sh` applies `normalize.sed` to each log and writes the batch, status, and path. `summarize.awk` counts the results by batch and status.

~~~sh
sh build-ledger.sh runs.tsv > ledger.tsv &&
awk -f summarize.awk ledger.tsv > summary.tsv &&
diff -u expected/ledger.tsv ledger.tsv &&
diff -u expected/summary.tsv summary.tsv
~~~

Both diffs should be empty.

| Batch | Runs | PASS | NO_DEVICE | NO_EVENT | NO_RESULT | REVIEW |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| before | 3 | 0 | 3 | 0 | 0 | 0 |
| after | 3 | 2 | 0 | 1 | 0 | 0 |

- `PASS` means the test received the simulated power-button event.
- `NO_DEVICE` means the input device was missing.
- `NO_EVENT` means the test waited for the power button and timed out.
- `NO_RESULT` means the log contains no self-test result line.
- `REVIEW` flags an unfamiliar result or more than one result in a single run.

Use the ledger to locate the after run with `NO_EVENT` and check the original messages.

~~~sh
awk -F '\t' '$1 == "after" && $2 == "NO_EVENT" {print $3}' ledger.tsv
grep -En '^DUT (READY|SELFTEST)' raw/after/02.log
~~~

## Include the interrupted run

The capture in [raw/after/04.log](raw/after/04.log) stopped after `DUT READY: waiting for KEY_POWER`. The run list still contains it, so it appears as `NO_RESULT`.

~~~sh
sh build-ledger.sh runs-with-interruption.tsv > ledger-with-interruption.tsv &&
awk -f summarize.awk ledger-with-interruption.tsv > summary-with-interruption.tsv &&
diff -u expected/ledger-with-interruption.tsv ledger-with-interruption.tsv &&
diff -u expected/summary-with-interruption.tsv summary-with-interruption.tsv
~~~

The before batch stays at three runs. The after batch now has four runs, with two `PASS`, one `NO_EVENT`, and one `NO_RESULT`. Each row still points to a raw log.
