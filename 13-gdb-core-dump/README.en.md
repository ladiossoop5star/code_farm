# Episode 13 · Analyze an AArch64 firmware dump with GDB

[繁體中文](README.md)

In QEMU `virt`, the exercise firmware reads a fixed value of 2750 mV. That is below the 3000 mV threshold and triggers `brk #0x42`. The exception handler saves x0–x30, SP, ELR_EL1, SPSR_EL1, ESR_EL1, and FAR_EL1 to RAM. The capture tool waits for the completion marker, then saves 32 KiB of RAM and SHA-256 fingerprints for the capture and matching build.

| Region | Address and purpose |
| --- | --- |
| Firmware | Starts at `0x40080000`. Use the matching ELF for symbols and instructions. |
| Captured RAM | `0x400c0000` through `0x400c7fff`, little-endian. |
| Exception record | RAM starts with the `FWLAB13` marker followed by the saved 64-bit fields. |
| Controller state | `state` at `0x400c1000`, decoded by GDB using the C type. |
| Stack | Grows down from `0x400c8000`. The sample SP is `0x400c7fe0`. |

## Rebuild from source

You need Python 3, AArch64 GCC, AArch64 QEMU, and a GDB build that supports AArch64. The scripts look for `qemu-system-aarch64` and `aarch64-linux-gnu-gcc` on PATH. Tool overrides are `FW_QEMU`, `FW_QEMU_DATA`, `FW_QEMU_LIBS`, and `FW_CC`. If your system GDB does not support AArch64, substitute `gdb-multiarch` in the commands. The exercise was tested with GCC 13.3.0 and GDB 15.1.

Run from this directory so GDB can find the source associated with the capture.

```sh
lab_dir=$(mktemp -d)
python3 capture.py "$lab_dir/sample"
rt="$lab_dir/sample"
readelf -h "$rt/firmware.elf"
readelf -n "$rt/firmware.elf"
python3 core.py "$rt/firmware.elf" "$rt/exception.ram" "$rt/manifest.json" "$rt/firmware.core"
gdb -nx -iex 'set debuginfod enabled off' "$rt/firmware.elf" "$rt/firmware.core"
```

In GDB, inspect the registers, instruction, call stack, and RAM.

```text
info registers pc sp x30
x/i $pc
bt
p state
x/4uw &state
```

## Try a mismatched build and a partial dump

```sh
python3 core.py "$rt/other-build.elf" "$rt/exception.ram" "$rt/manifest.json" "$lab_dir/wrong.core"
python3 core.py --omit-stack "$rt/firmware.elf" "$rt/exception.ram" "$rt/manifest.json" "$rt/partial.core"
gdb -nx -iex 'set debuginfod enabled off' -batch "$rt/firmware.elf" "$rt/partial.core" -ex 'x/4gx $sp'
```

The converter rejects the mismatched ELF with `ELF fingerprint mismatch`. The partial core omits the stack segment, so reading memory at SP returns `Cannot access memory`. The converter handles this exercise's dump layout. On another device, use its memory map and exception record format.

You can also open `sample/firmware.elf` and `sample/firmware.core` directly. [GDB output](sample/gdb.txt) · [Capture manifest](sample/manifest.json)

[GDB file commands](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Files.html) · [QEMU QMP](https://www.qemu.org/docs/master/interop/qemu-qmp-ref.html)
