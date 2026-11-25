# Episode 18 | Running a multi-pane test with Alphonse

Alphonse gives an AI agent instructions for running one TOML plan in Herdr. The agent follows a fixed pane layout, sends the commands in order, and returns PASS or FAIL from the current output. [Pane layout rules](skills/alphonse/SKILL.md#fixed-pane-layout)

## Setup

1. Prepare 2 Linux test endpoints with iperf 2. The receiver doubles as the device under test (DUT). The sender also needs `ping` and must be able to reach the DUT's test IP.
2. Adapt the [example SSH config](ssh-config.example) to your lab. `receiver` and `dut-console` are separate logins to the same DUT. Set up keys, verify the host fingerprints, and confirm that `ssh receiver`, `ssh sender`, and `ssh dut-console` each open a Bash shell without a remote password prompt. Replace `192.0.2.10` in the TOML commands with the receiver's actual test IP. It may differ from the SSH address.
3. The host needs Python 3.11 or later for the pane setup script to read TOML. Open your agent in Herdr and load the [Alphonse skill](skills/alphonse/SKILL.md). With Pi, for example, launch `pi --skill ./skills/alphonse/SKILL.md` from this directory. The agent needs file and shell access.

## Run one round

> Use Alphonse to run iperf-pass.toml once. Apply pass_criteria and cite this round's output from the receiver, sender, and console.

- The server runs in the foreground of the receiver pane. Once it prints `Server listening`, the agent moves on to the sender pane.
- The sender runs iperf for 3 seconds, then pings the DUT. A separate DUT login runs `uname -r` and shows whether the shell responds after the transfer.
- After collecting the current output, the agent stops the server it started with Ctrl+C. Keep only the verdict and evidence needed by the fix loop. Ask the agent to keep the panes open if you want to inspect them afterward.
- Run [iperf-fail.toml](iperf-fail.toml) as a separate round. It sends 128 KiB. The round fails when the receiver lacks 3 complete intervals with positive throughput, even if ping and the console still respond.

Use `ready` when a foreground program should keep running in its own pane. Other blocks finish their commands before the agent advances. For more involved test operations, call a script from the block. Keep timing-sensitive startup or sampling in the same script.
