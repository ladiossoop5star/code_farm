# Episode 17 | Edward: Let AI Run a Multi-Machine Test with One Command

[繁體中文](README.md)

Start with the shortest test that reproduces the problem and produces enough evidence for this round. On this bench, a two-second wait after starting the iperf server is sufficient. Edward streams each block's raw output to the terminal and writes one temporary report. The AI deletes the report after reading it and reaching a verdict.

## Set up two test machines

On the Host, configure [`receiver` and `sender`](ssh-config.example) in `~/.ssh/config` with their SSH addresses and login accounts. Verify host keys and set up SSH key authentication.

```sh
ssh receiver hostname
ssh sender hostname
```

If SSH asks for the remote account password, finish setting up key authentication. Run Edward once both commands return their hostnames directly.

Both machines use Linux, Bash, and iperf 2.x. The sender also needs `ping`. The Host uses Bash, GNU coreutils, an OpenSSH client, and Python 3.11 or later. In both TOML files, replace `192.0.2.10` with the receiver's test IP as reachable from the sender. In this exercise, the receiver is the DUT, and iperf uses its default TCP port, 5001.

## Run the simple plan

```sh
./edward iperf-pass.toml
```

| Block | Machine | Operation |
| --- | --- | --- |
| 1 | `receiver` | Start the iperf server, write its output to `/tmp/iperf-server.log`, then `sleep 2` |
| 2 | `sender` | Send traffic for three seconds, then probe the DUT with `ping` |
| 3 | `receiver` | Read the receiver log with `cat` and remove the remote temporary file after a successful read |

Edward gives each block's entire `commands` section to Bash on its assigned machine. Each block gets a fresh shell. A block with `machine = "local"` runs directly on the Host. If an earlier command fails, Edward continues collecting the later output so the AI has evidence to diagnose the failure.

Run one round at a time on this bench. The receiver server runs for eight seconds with `-t 8`. Wait for it to exit before rerunning the test. To try the failure example, run `./edward iperf-fail.toml`. Its sender transmits 128 KiB.

## Give the test to an AI

> Run `./edward iperf-pass.toml`. Read the Report file named at the end of the output and apply the criteria in that file. Return PASS or FAIL. Cite the receiver measurements from block 3 and the DUT probe from block 2. Delete the report once you've finished reading it.

The normal plan requires positive throughput in three complete one-second intervals at the receiver and a ping reply from the DUT after the transfer. The DUT also replies in the failure case, but the measurement is shorter than three seconds. Both runs use the same criteria.

## Advanced reference

If a fixed two-second wait is unreliable, remote commands need explicit timeouts, or you need separate output files for each block, see the [advanced plan](advanced/iperf-pass.toml) and [advanced runner](advanced/edward). Update the test IP in the plan, then run `./advanced/edward advanced/iperf-pass.toml` from this directory. The Host also needs `setsid` (util-linux).
