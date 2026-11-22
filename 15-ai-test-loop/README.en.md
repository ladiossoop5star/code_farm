# 15 | Testing lets an AI agent know when the fix is done

[繁體中文](README.md) · [Agent workflow](workflow.md)

Send real iperf traffic through a small TCP relay. Define the passing criteria before you look at the receiver measurements and the relay health probe.

The demo requires Linux, Python 3, and iperf 2.x (the `iperf` executable). Run these commands in this directory. All traffic stays on `127.0.0.1`. The demo cleans up its temporary files and processes.

```sh
python3 relay-demo.py crash
python3 relay-demo.py drop
python3 relay-demo.py drop    # Retest the same revision with the tightened criteria
python3 relay-demo.py forward
```

| Case | Receiver evidence | Device evidence | Verdict |
| --- | --- | --- | --- |
| `crash` | Only the first complete interval | The demo injects a process exit and the health probe fails | FAIL |
| `drop` | No measurement intervals | Relay responds to the health probe but forwards zero bytes | A health-only check can pass. The tightened criteria give FAIL. |
| `forward` | Positive throughput in all three intervals (0–1, 1–2, and 2–3 seconds) | Transfer completes and the health probe succeeds | PASS |

Write criteria an agent can check. State which endpoint supplies evidence, how long the measurement must run, and which conditions must hold together. Then use `drop` to find the gap in the original condition “the device must not crash.”
