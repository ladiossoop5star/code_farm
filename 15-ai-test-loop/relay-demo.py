"""Run the episode's local relay fixture and display its real test outputs."""
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time


def main():
    variant, = sys.argv[1:]
    assert variant in {"forward", "drop", "crash"}
    with tempfile.TemporaryDirectory(prefix="relay-take-") as directory:
        root = Path(directory)
        environment = {**os.environ, "TEST_VARIANT": variant, "TEST_ROUND": directory}
        processes = []

        def background(role):
            path = root / f"{role}.log"
            with path.open("w") as output:
                process = subprocess.Popen(
                    ["python3", "-u", "relay.py", role], env=environment,
                    stdout=output, stderr=subprocess.STDOUT, start_new_session=True,
                )
            processes.append(process)
            return path

        def ready(log, token):
            limit = time.monotonic() + 5
            while time.monotonic() < limit:
                if token in log.read_text():
                    return
                time.sleep(.04)
            raise TimeoutError(token)

        try:
            sink = background("sink")
            ready(sink, "SINK READY")
            print("Receiver ready", flush=True)
            dut = background("dut")
            ready(dut, "DUT READY")
            print("DUT ready · starting iperf\n", flush=True)
            client = subprocess.run(["python3", "-u", "relay.py", "client"], env=environment,
                                    check=False, capture_output=True, text=True, timeout=12)
            print("SENDER")
            for line in client.stdout.splitlines():
                if " sec " in line or "IPERF CLIENT EXIT" in line:
                    print(line)
            print("\nRECEIVER")
            intervals = [line for line in sink.read_text().splitlines() if " sec " in line]
            print("\n".join(intervals) if intervals else "[no measurement intervals]")
            print("\nDUT")
            for line in dut.read_text().splitlines():
                if "SESSION COMPLETE" in line or "CRASH INJECTED" in line:
                    print(line)
            subprocess.run(["python3", "-u", "relay.py", "health"], env=environment,
                           check=False, timeout=4)
        finally:
            for process in reversed(processes):
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=3)


if __name__ == "__main__":
    main()
