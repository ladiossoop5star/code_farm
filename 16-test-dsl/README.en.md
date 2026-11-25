# Episode 16 · Test DSL

[繁體中文](README.md)

Each block groups consecutive operations on one machine. Set `machine` to the target's name. Write ordinary shell commands on separate lines inside `commands`. Start a new block when you switch machines. Use the shell's trailing `&` for a background service, then check this round's log for readiness before moving on.

| Example | Block order |
| --- | --- |
| [Direct traffic](two-blocks.toml) | Start the receiver and wait for it to listen → Send traffic for three seconds |
| [Traffic through the DUT](relay.toml) | Wait for the receiver → Wait for the DUT relay → Send traffic and probe the DUT from the same sender block |

`machine` identifies the computer that runs the commands. Run local commands directly. For a remote computer, connect over SSH and run them there. An SSH alias can hold the remote address, login name, and jump host. For UART or USB, run the tool or script on the computer the device is plugged into. For example, run `tm_set_cmd` locally if the UART cable is plugged into the local computer. If the cable is plugged into a remote computer, connect over SSH and run the same tool there.

The plan describes the order of operations and the evidence needed to pass. This episode explains the plan, and later episodes use it with Edward and Alphonse.

## Walk through the examples

Both examples run on one computer, with a separate terminal for each role. Use Linux, Bash, iperf 2.x, and GNU `stdbuf`. Put `wait-ready` from episode 08 on your `PATH`. Create a directory with `mktemp -d` for each round and set `TEST_ROUND` to that same path in each terminal. Run each block's `commands` in the corresponding terminal. Wait for readiness before switching targets.

The direct example uses loopback and defaults to port `55106`. If it is occupied, set `IPERF_PORT` to the same unused port on both the sender and the receiver. For the relay example, run from the directory containing episode 15's `relay.py`. Set `TEST_VARIANT` to the same value in all terminals. Try `forward`, `drop`, and `crash` in separate rounds. Compare the receiver intervals and DUT probe with the written criteria. Once you have collected the evidence, stop the background processes started for that round.

[Episode 08 wait-ready](https://github.com/ladiossoop5star/code_farm/blob/main/08-ai-cli-tools/bin/wait-ready) · [Episode 15 relay.py](https://github.com/ladiossoop5star/code_farm/blob/main/15-ai-test-loop/relay.py)
