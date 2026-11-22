#!/usr/bin/env python3
"""Rebuild the public firmware and capture its exception RAM in isolated QEMU."""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import time

from core import BASE, RAM_SIZE, digest, register_frame


def build(source, destination, tag):
    cc = os.environ.get("FW_CC", "aarch64-linux-gnu-gcc")
    subprocess.run(
        [cc, "-g3", "-O0", "-ffreestanding", "-fno-omit-frame-pointer",
         "-fno-optimize-sibling-calls", "-fno-stack-protector", "-fno-pie",
         f"-ffile-prefix-map={source}=.",
         "-nostdlib", "-static", "-no-pie", f"-DBUILD_TAG={tag}",
         "-Wl,--build-id=sha1", "-Wl,-T,firmware.ld",
         "boot.S", "firmware.c", "-o", str(destination)],
        cwd=source, check=True,
    )


def command(stream, execute, arguments=None):
    message = {"execute": execute}
    if arguments:
        message["arguments"] = arguments
    stream.write(json.dumps(message).encode() + b"\n")
    while line := stream.readline():
        response = json.loads(line)
        if "error" in response:
            raise RuntimeError(response["error"])
        if "return" in response:
            return response["return"]
    raise RuntimeError(f"QMP closed before responding to {execute}")


def capture(source, output):
    qemu = os.environ.get("FW_QEMU", "qemu-system-aarch64")
    data = os.environ.get("FW_QEMU_DATA")
    libs = os.environ.get("FW_QEMU_LIBS")
    environment = os.environ.copy()
    if libs is not None:
        environment["LD_LIBRARY_PATH"] = libs
    firmware = output / "firmware.elf"
    snapshot = output / "exception.ram"
    build(source, firmware, 13)
    build(source, output / "other-build.elf", 14)
    with tempfile.TemporaryDirectory(prefix="fw13-") as run_dir:
        qmp = Path(run_dir) / "qmp"
        serial = Path(run_dir) / "serial"
        argv = [qemu]
        if data:
            argv += ["-L", data]
        argv += ["-machine", "virt,acpi=off", "-cpu", "cortex-a57",
                "-nodefaults", "-display", "none", "-nic", "none", "-m", "128",
                "-monitor", "none", "-serial", f"file:{serial}",
                "-qmp", f"unix:{qmp},server=on,wait=off", "-kernel", str(firmware)]
        with subprocess.Popen(argv, env=environment) as guest:
            try:
                deadline = time.monotonic() + 15
                while time.monotonic() < deadline:
                    if guest.poll() is not None:
                        raise RuntimeError("QEMU stopped before the firmware capture")
                    if qmp.exists() and serial.exists() and b"FWLAB READY" in serial.read_bytes():
                        break
                    time.sleep(.05)
                else:
                    raise TimeoutError("firmware exception marker did not arrive")
                with socket.socket(socket.AF_UNIX) as connection:
                    connection.settimeout(5)
                    connection.connect(str(qmp))
                    with connection.makefile("rwb", buffering=0) as stream:
                        assert "QMP" in json.loads(stream.readline())
                        command(stream, "qmp_capabilities")
                        command(stream, "stop")
                        command(stream, "pmemsave", {"val": BASE, "size": RAM_SIZE,
                                                   "filename": str(snapshot)})
                        command(stream, "quit")
            finally:
                if guest.poll() is None:
                    guest.terminate()
                guest.wait(timeout=5)
    registers = register_frame(snapshot.read_bytes())
    manifest = {"format": "FWLAB13", "arch": "AArch64", "machine": "QEMU virt",
                "ram_base": BASE, "ram_length": RAM_SIZE,
                "elf_sha256": digest(firmware), "ram_sha256": digest(snapshot),
                "esr_el1": f"{registers[34]:#x}"}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True)
    capture(Path(__file__).resolve().parent, args.output.resolve())
