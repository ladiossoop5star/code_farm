#!/usr/bin/env python3
"""Verify the capture manifest and translate this firmware format to an ELF core."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

BASE = 0x400c0000
RAM_SIZE = 0x8000
MAGIC = b"FWLAB13\0"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def register_frame(data):
    if len(data) != RAM_SIZE or data[:8] != MAGIC:
        raise ValueError("unexpected firmware dump format or size")
    registers = struct.unpack_from("<36Q", data, 8)
    sp, pc = registers[31:33]
    if not BASE + 0x1000 <= sp < BASE + RAM_SIZE or sp % 16:
        raise ValueError("captured SP is outside the expected stack range")
    if not 0x40080000 <= pc < BASE or pc % 4:
        raise ValueError("captured PC is outside the expected text range")
    return registers


def make_core(firmware, snapshot, manifest_path, output, omit_stack=False):
    manifest = json.loads(manifest_path.read_text())
    if manifest["format"] != "FWLAB13" or manifest["ram_base"] != BASE:
        raise ValueError("manifest format or memory map does not match")
    if digest(firmware) != manifest["elf_sha256"]:
        raise ValueError("ELF fingerprint mismatch")
    if digest(snapshot) != manifest["ram_sha256"]:
        raise ValueError("RAM snapshot fingerprint mismatch")
    ram = snapshot.read_bytes()
    registers = register_frame(ram)
    if omit_stack:
        ram = ram[:0x2000]
    sig = 5  # GDB displays the saved BRK exception as SIGTRAP.
    status = bytearray(392)
    struct.pack_into("<i", status, 0, sig)
    struct.pack_into("<h", status, 12, sig)
    struct.pack_into("<i", status, 32, 1)
    struct.pack_into("<34Q", status, 112, *registers[:34])
    note = struct.pack("<III", 5, len(status), 1) + b"CORE\0\0\0\0" + status
    ident = b"\x7fELF\x02\x01\x01" + b"\0" * 9
    header = struct.pack("<16sHHIQQQIHHHHHH", ident, 4, 183, 1, 0, 64, 0, 0,
                         64, 56, 2, 0, 0, 0)
    note_header = struct.pack("<II6Q", 4, 0, 176, 0, 0, len(note), len(note), 4)
    load_header = struct.pack("<II6Q", 1, 6, 4096, BASE, BASE, len(ram), len(ram), 4096)
    with output.open("xb") as core:
        core.write((header + note_header + load_header + note).ljust(4096, b"\0"))
        core.write(ram)
    return registers


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("firmware", "snapshot", "manifest", "output"):
        parser.add_argument(arg, type=Path)
    parser.add_argument("--omit-stack", action="store_true", help="reproduce a partial dump in the lesson")
    args = parser.parse_args()
    try:
        regs = make_core(args.firmware, args.snapshot, args.manifest, args.output, args.omit_stack)
    except (OSError, KeyError, ValueError) as error:
        parser.exit(1, f"ERROR: {error}\n")
    print(f"ELF matched, PC={regs[32]:#x} SP={regs[31]:#x} LR={regs[30]:#x} "
          f"ESR_EL1={regs[34]:#x} FAR_EL1={regs[35]:#x}")
