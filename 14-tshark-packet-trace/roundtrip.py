#!/usr/bin/env python3
"""Capture a controlled UDP retry and the matching kernel transmit events."""
import argparse
from decimal import Decimal
import os
from pathlib import Path
import re
import selectors
import socket
import struct
import subprocess
import tempfile
import threading
import time


ADDRESS = "127.0.0.1"
PORT = 47006
CLIENT_PORT = 47007
REQUEST = struct.pack("!BI", 1, 42)
REPLY = struct.pack("!BI", 2, 42)


def put(path, value):
    path.write_text(str(value) + "\n")


def start_capture(process, pcap):
    with selectors.DefaultSelector() as selector:
        selector.register(process.stderr, selectors.EVENT_READ)
        deadline = time.monotonic() + 10
        output = b""
        while time.monotonic() < deadline:
            if pcap.stat().st_size >= 28:
                return
            if not selector.select(.05):
                continue
            part = os.read(process.stderr.fileno(), 4096)
            if not part:
                break
            output += part
            if b"Capture started" in output:
                return
    raise RuntimeError(f"TShark did not start capture: {output.decode(errors='replace')}")


def collect(tshark, output, instance):
    event_log = output / "endpoint.tsv"
    pcap = output / "packets.pcapng"
    trace = output / "kernel.trace"
    transmit = instance / "events/net/net_dev_queue"
    put(instance / "tracing_on", 0)
    put(instance / "trace_clock", "mono")
    put(instance / "trace", "")
    queue = []
    signal = threading.Event()

    def log(side, event):
        queue.append((time.time_ns(), side, event))

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind((ADDRESS, PORT))
        server_socket.settimeout(5)

        def server():
            try:
                if not signal.wait(5):
                    raise TimeoutError("server was not started")
                for index in range(2):
                    payload, peer = server_socket.recvfrom(64)
                    if payload != REQUEST:
                        raise ValueError("unexpected loopback request")
                    log("server", f"received-{index + 1}")
                    if index == 0:
                        log("server", "hold-reply")
                server_socket.sendto(REPLY, peer)
                log("server", "reply")
            except (OSError, ValueError) as error:
                log("server", f"error={error}")

        thread = threading.Thread(target=server)
        thread.start()
        capture_args = [tshark, "-q", "-i", "lo", "-f", f"udp port {PORT}",
                        "-c", "3", "-a", "duration:10", "-w", "-"]
        with pcap.open("xb") as packet_file, subprocess.Popen(
                capture_args, stderr=subprocess.PIPE, stdout=packet_file) as capture:
            try:
                start_capture(capture, pcap)
                put(transmit / "filter",
                    f'name == "lo" && (common_pid == {thread.native_id} || common_pid == {os.getpid()})')
                put(transmit / "enable", 1)
                put(instance / "tracing_on", 1)
                mono = time.monotonic_ns()
                wall = time.time_ns()
                put(instance / "trace_marker", f"LAB_CLOCK mono_ns={mono} epoch_ns={wall}")
                signal.set()
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
                    client.bind((ADDRESS, CLIENT_PORT))
                    client.settimeout(.12)
                    log("client", "send-1")
                    client.sendto(REQUEST, (ADDRESS, PORT))
                    try:
                        client.recvfrom(64)
                    except TimeoutError:
                        log("client", "timeout")
                    else:
                        raise AssertionError("unexpected reply before the deliberate hold")
                    log("client", "send-2")
                    client.sendto(REQUEST, (ADDRESS, PORT))
                    payload, _ = client.recvfrom(64)
                    if payload != REPLY:
                        raise AssertionError("unexpected reply payload")
                    log("client", "reply-received")
                thread.join(timeout=2)
                _, errors = capture.communicate(timeout=12)
                if capture.returncode:
                    raise RuntimeError(errors.decode(errors="replace"))
            finally:
                signal.set()
                if capture.poll() is None:
                    capture.terminate()
                    capture.wait(timeout=5)
                thread.join(timeout=6)
                put(instance / "tracing_on", 0)
                put(transmit / "enable", 0)
                trace.write_text((instance / "trace").read_text())
                event_log.write_text("epoch_ns\tendpoint\tevent\n" +
                                     "".join(f"{ns}\t{side}\t{event}\n" for ns, side, event in sorted(queue)))


def summarize(tshark, output):
    fields = ("frame.number", "frame.time_epoch", "udp.srcport", "udp.dstport", "udp.payload")
    args = [tshark, "-r", str(output / "packets.pcapng"),
            "-Y", f"udp.port == {PORT}", "-T", "fields"]
    for field in fields:
        args += ["-e", field]
    lines = subprocess.check_output(args, text=True)
    rows = [line.split("\t") for line in lines.splitlines()]
    if len(rows) != 3:
        raise ValueError("expected exactly three captured datagrams")
    for index, row in enumerate(rows):
        reply = index == 2
        expected = REPLY if reply else REQUEST
        source, destination = (PORT, CLIENT_PORT) if reply else (CLIENT_PORT, PORT)
        if row[2:4] != [str(source), str(destination)] or bytes.fromhex(row[4].replace(":", "")) != expected:
            raise ValueError(f"unexpected captured datagram at frame {row[0]}")
    packet_times = [int(Decimal(row[1]) * 1_000_000_000) for row in rows]
    if not 90_000_000 <= packet_times[1] - packet_times[0] < 1_000_000_000:
        raise ValueError("retry time did not match the client timeout")
    trace = (output / "kernel.trace").read_text()
    clock = re.search(r"LAB_CLOCK mono_ns=(\d+) epoch_ns=(\d+)", trace)
    if clock is None:
        raise ValueError("kernel trace did not capture the paired clock marker")
    mono, epoch = map(int, clock.groups())
    events = re.findall(r"\s(\d+\.\d+): net_dev_queue: .*(?:name|dev)=lo(?:\s|$)", trace)
    kernel_times = [int(Decimal(event) * 1_000_000_000) + epoch - mono for event in events]
    if (len(kernel_times) != 3 or
            any(abs(packet - event) > 20_000_000 for packet, event in zip(packet_times, kernel_times))):
        raise ValueError(f"expected 3 kernel sends aligned to capture, got {kernel_times}")
    endpoint = (output / "endpoint.tsv").read_text()
    for marker in ("client\ttimeout", "server\thold-reply", "server\treply", "client\treply-received"):
        if marker not in endpoint:
            raise ValueError(f"missing endpoint event: {marker}")
    (output / "packets.tsv").write_text("\t".join(fields) + "\n" + lines)
    report = ["frame\ttransmit\tsequence\tpcap_ms\tkernel_ms"]
    for index, row in enumerate(rows):
        relative = lambda stamp: f"{(stamp - packet_times[0]) / 1e6:.3f}"
        label = ("request", "retry", "reply")[index]
        report.append(f"{row[0]}\t{label}\t42\t{relative(packet_times[index])}\t{relative(kernel_times[index])}")
    (output / "aligned.tsv").write_text("\n".join(report) + "\n")
    print("\n".join(report))
    print("VERIFY UDP PCAP, KERNEL TRACE AND ENDPOINT LOG OK")


def run(output, tshark):
    if os.geteuid() != 0 or os.stat("/proc/self/ns/net").st_ino == os.stat("/proc/1/ns/net").st_ino:
        raise SystemExit("Run in a new isolated network namespace with root privileges.")
    output.mkdir(parents=True)
    output = output.resolve()
    subprocess.run(["ip", "link", "set", "lo", "up"], check=True)
    with tempfile.TemporaryDirectory(prefix="trace14-") as mount_dir:
        mount_dir = Path(mount_dir)
        subprocess.run(["mount", "-t", "tracefs", "tracefs", mount_dir], check=True)
        try:
            instance = mount_dir / "instances" / f"episode14-{os.getpid()}"
            instance.mkdir()
            try:
                collect(tshark, output, instance)
                summarize(tshark, output)
            finally:
                instance.rmdir()
        finally:
            subprocess.run(["umount", mount_dir], check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--tshark", default="tshark")
    args = parser.parse_args()
    run(args.output, args.tshark)
