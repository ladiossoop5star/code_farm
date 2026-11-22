#!/usr/bin/env python3
"""Exercise a loopback TCP relay with a real iperf2 receiver and sender."""

import argparse
from contextlib import nullcontext
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
from threading import Thread
import time


ADDRESS = "127.0.0.1"
ROUND = Path(os.environ["TEST_ROUND"])
VARIANT = os.environ["TEST_VARIANT"]


def save(name, value):
    path = ROUND / f"{name}.json"
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(value) + "\n")
    temp.replace(path)


def endpoint(name):
    return json.loads((ROUND / f"{name}.json").read_text())


def listener():
    return socket.create_server((ADDRESS, 0))


def sink():
    with listener() as reservation:
        port = reservation.getsockname()[1]
    args = ["stdbuf", "-oL", "-eL", "iperf", "-s", "-1", "-B", ADDRESS,
            "-p", str(port), "-i", "1", "-f", "m"]
    with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True) as child:
        for line in child.stdout:
            print(line, end="", flush=True)
            if "Server listening on TCP port" in line:
                save("sink-address", {"port": port})
                print("SINK READY", flush=True)
        return child.wait()


def transfer(source, upstream):
    started = time.monotonic()
    received = 0
    forwarded = 0
    print("DUT SESSION START", flush=True)
    while data := source.recv(65536):
        received += len(data)
        if VARIANT == "crash" and time.monotonic() - started >= 1.2:
            print(f"DUT CRASH INJECTED forwarded={forwarded}", flush=True)
            os._exit(42)
        if upstream:
            upstream.sendall(data)
            forwarded += len(data)
    print(f"DUT SESSION COMPLETE received={received} forwarded={forwarded}", flush=True)


def return_traffic(upstream, source):
    try:
        while data := upstream.recv(65536):
            source.sendall(data)
        source.shutdown(socket.SHUT_WR)
    except ConnectionError:
        # The sender can close its side after the final measurement.
        pass


def dut():
    with listener() as server:
        port = server.getsockname()[1]
        save("dut-address", {"port": port, "identity": ROUND.name})
        print(f"DUT listening on loopback TCP/{port}", flush=True)
        print("DUT READY", flush=True)
        source, _ = server.accept()
        with source:
            sink_port = endpoint("sink-address")["port"]
            forward = socket.create_connection((ADDRESS, sink_port), timeout=3) if VARIANT != "drop" else nullcontext()
            with forward as upstream:
                if upstream is None:
                    transfer(source, None)
                else:
                    upstream.settimeout(5)
                    feedback = Thread(target=return_traffic, args=(upstream, source), daemon=True)
                    feedback.start()
                    transfer(source, upstream)
                    upstream.shutdown(socket.SHUT_WR)
                    feedback.join(timeout=5)
        while True:
            probe, _ = server.accept()
            with probe:
                probe.sendall((ROUND.name + "\n").encode())


def client():
    port = endpoint("dut-address")["port"]
    args = ["iperf", "-c", ADDRESS, "-p", str(port), "-t", "3",
            "-i", "1", "-b", "12m", "-f", "m"]
    result = subprocess.run(args, check=False)
    print(f"IPERF CLIENT EXIT={result.returncode}", flush=True)
    return result.returncode


def health():
    info = endpoint("dut-address")
    try:
        with socket.create_connection((ADDRESS, info["port"]), timeout=1) as probe:
            with probe.makefile("r") as response:
                identity = response.readline(128).strip()
        if identity == info["identity"]:
            print("DUT PROBE OK", flush=True)
            return 0
        print("DUT PROBE FAILED: unexpected identity", flush=True)
    except OSError as error:
        print(f"DUT PROBE FAILED: {error}", flush=True)
    return 1


def main():
    actions = {"sink": sink, "dut": dut, "client": client, "health": health}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=actions)
    return actions[parser.parse_args().action]()


if __name__ == "__main__":
    sys.exit(main())
