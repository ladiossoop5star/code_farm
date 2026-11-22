# Trace a DMA workaround with Git blame and pickaxe

[繁體中文](README.md)

Follow the history of a 4 KiB DMA descriptor split and see why it was later limited to Rev A. The exercise creates four commits for the initial implementation, the split, the revision check, and an indentation change.

You need Git, Python 3, GNU Make, and a C compiler. The exercise uses a local model of the DMA behavior.

## Verify the exercise

~~~sh
python3 prepare.py
~~~

The script creates a temporary Git history, checks the queries, full patch, and three cases, then prints the short hashes for the split, capability check, and indentation commits.

## Build a history to explore

Run the commands from this material directory in one shell. The commit hashes in your repository may differ from those in the video.

~~~sh
lab_dir=$(mktemp -d)
python3 prepare.py "$lab_dir/dma-demo"
cd "$lab_dir/dma-demo"
git log --oneline
~~~

## Find the change with blame

~~~sh
git blame -L '/if (crosses_4k(addr, len)/,+2' -- dma_submit.c
git blame -w -L '/if (crosses_4k(addr, len)/,+2' -- dma_submit.c
~~~

The first query points the if line at the indentation commit. With `-w`, it points to the commit that adds `caps->split_at_4k`.

## Compare the pickaxe results

~~~sh
git log --oneline -S'crosses_4k(addr, len)' -- dma_submit.c
git log --oneline -G'crosses_4k\(addr, len\)' -- dma_submit.c
~~~

`-S` checks for a change in the number of occurrences of the string, and finds the commit that first added the split. `-G` matches a regular expression against added or removed lines. Here it finds the split, capability check, and indentation commits.

## Inspect the full patch and rerun three cases

~~~sh
split=$(git log -1 --format=%H -S'crosses_4k(addr, len)' -- dma_submit.c)
gate=$(git blame -w --porcelain -L '/if (crosses_4k(addr, len)/,+1' -- dma_submit.c | sed -n '1s/ .*//p')
git show "$split" -- dma_submit.c
git show "$gate"
make test
cat design-notes.md
~~~

The capability patch includes `dma_caps.c`, `dma_submit.c`, and `selftest.c`. At DMA address `0x1ff0`, expect these results.

| Revision and length | Expected descriptors |
| --- | --- |
| Rev A, 32 bytes | Two of 16 bytes each |
| Rev B, 32 bytes | One of 32 bytes |
| Rev A, 16 bytes | One of 16 bytes |

The generated `design-notes.md` shows how to record the finding. Use the [English notes template](design-notes-template.en.md) to connect each conclusion to a patch, the revision it applies to, and a test you can rerun.
