# Episode 19 | A repair loop from FAIL to PASS

This local C exercise models the circular indices used when a network driver reclaims TX descriptors. The test program supplies the device completion pointer so you can exercise the reclaim logic and the AI workflow.

## Run it

You need Bash, a C compiler, Make, and Python 3.11 or later. The included Edward runner is the same minimal version used in Episode 17.

1. Copy the exercise into a fresh working directory. Run `make` to build the original `tx-check`.
2. Open your coding agent in that directory and give it the [task prompt](prompt.en.md). It should start with `./edward tx-wrap.toml`, read the round's output, then investigate the cause.
3. Check the source change, the new build, and the observed output from the same test after the repair. [Traditional Chinese prompt](prompt.zh-TW.md)

The baseline `wrap` case reclaims nothing and leaves 4 entries pending. After repair it should reclaim 201, 202, and 203 in order and leave 1 entry pending. The `linear` and `idle` cases should also satisfy the [criteria in the TOML](tx-wrap.toml). Run the same Edward command to see those observations yourself. The output ends with the location of the temporary report so you can remove it after reading.

Use the same plan before and after repair. To restore the initial state for a new round, copy the exercise into another fresh directory.
