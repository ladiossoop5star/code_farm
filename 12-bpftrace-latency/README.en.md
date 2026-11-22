# Episode 12 · Compare latency distributions with bpftrace

[繁體中文](README.md)

Match entry and return probes on `observe_measure` and convert each elapsed time to microseconds. Compare three workloads to distinguish a single outlier from a general slowdown.

## Run the exercise

On an AArch64 Linux host, prepare QEMU, AArch64 GCC, a statically linked AArch64 BusyBox, make, cpio, and gzip. Supply an AArch64 kernel image, matching headers, and the configuration used to build it. The exercise was tested with QEMU 8.2.2 and Linux 6.17.0-1014-nvidia. The runner creates a temporary initramfs and boots a guest without an external network interface.

Replace these example paths with files from the same kernel build and run from this directory.

```sh
export OBS_KERNEL=/path/to/arm64/Image
export OBS_HEADERS=/path/to/matching/headers
export OBS_CONFIG=/path/to/matching/kernel.config
bash run-guest
```

Use `OBS_QEMU`, `OBS_CC`, or `OBS_BUSYBOX` to override tool locations. Set `OBS_QEMU_DATA` when QEMU uses a separate system-data directory. Use `bash run-guest shell` for the manual exercise inside the guest and `poweroff -f` to end it.

Install the AArch64 build of bpftrace on the host. The guest kernel needs BPF support, kprobes, and syscall tracepoints. The exercise was tested with bpftrace 0.20.2. A successful run prints `VERIFY BPFTRACE OK`. [Recorded histograms](sample.txt)

## Inspect the probes and histograms

Run the commands inside the guest. [latency.bt](latency.bt) matches entry and return by `tid`, which works for this sequential, non-recursive exercise. [workload](workload) runs the three fixed input sets.

```sh
bpftrace -l 'tracepoint:syscalls:sys_enter_write'
bpftrace -l 'kprobe:observe_measure'
bpftrace -c '/bin/sh /lab/workload' /lab/latency.bt
```

| Mode | Workload | Expected distribution |
| --- | --- | --- |
| 0 | Baseline | 12 samples, mostly in low-latency buckets |
| 1 | One slow call | 12 samples, a similar main cluster and a single long-tail sample |
| 2 | General slowdown | 12 samples, with the main cluster shifted toward higher latency |

VM scheduling can change the bucket counts and boundaries. Check the total sample count first, then compare how each distribution changes.

[bpftrace documentation](https://bpftrace.org/docs/)
