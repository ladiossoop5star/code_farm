# Episode 11 · Compare two driver paths with ftrace

[繁體中文](README.md)

Trace from `observe_probe` and capture the ready and timeout cases in separate windows. Compare nested calls, elapsed time, return values, and trace-buffer statistics.

## Run the exercise

On an AArch64 Linux host, prepare QEMU, AArch64 GCC, a statically linked AArch64 BusyBox, make, cpio, and gzip. Supply an AArch64 kernel image, matching headers, and the configuration used to build it. The exercise was tested with QEMU 8.2.2 and Linux 6.17.0-1014-nvidia. The runner creates a temporary initramfs and boots a guest without an external network interface.

Replace these example paths with files from the same kernel build and run from this directory.

```sh
export OBS_KERNEL=/path/to/arm64/Image
export OBS_HEADERS=/path/to/matching/headers
export OBS_CONFIG=/path/to/matching/kernel.config
bash run-guest
```

Use `OBS_QEMU`, `OBS_CC`, or `OBS_BUSYBOX` to override tool locations. Set `OBS_QEMU_DATA` when QEMU uses a separate system-data directory. Run `bash run-guest shell` for the manual exercise inside the guest and `poweroff -f` to end it.

The kernel requires `CONFIG_FUNCTION_GRAPH_TRACER` and `CONFIG_FUNCTION_GRAPH_RETVAL`. A successful run prints `VERIFY FUNCTION GRAPH OK`. [Recorded call graphs and statistics](sample.txt)

## Capture and compare

Inside the guest, list the available tracers and functions. These commands use the top-level tracefs controls in the dedicated guest.

```sh
cd /sys/kernel/tracing
grep -w function_graph available_tracers
grep -F observe_probe available_filter_functions
echo 0 > tracing_on
echo 128 > buffer_size_kb
echo function_graph > current_tracer
echo observe_probe > set_graph_function
echo funcgraph-retval > trace_options
echo funcgraph-retval-hex > trace_options
for mode in ready timeout; do
    : > trace
    echo 1 > tracing_on
    echo "$mode" > /sys/module/observe_lab/parameters/run
    echo 0 > tracing_on
    cat trace > "/tmp/$mode.graph"
    grep -E '^overrun:|^dropped events:' per_cpu/cpu*/stats
done
echo nop > current_tracer
: > set_graph_function
cat /tmp/ready.graph /tmp/timeout.graph
```

The ready case calls `observe_enable_queue` and returns 0 from `observe_probe`. In the timeout case, `observe_wait_ready` returns `-110`. The outer function calls `observe_cleanup`, then returns the same `-110`. Read `0xffffff92` using the corresponding function's signed 32-bit return type.

Check `overrun` and `dropped events` for each CPU. Timings vary with the environment, so start by comparing the call paths and return values.

[Linux ftrace documentation](https://docs.kernel.org/trace/ftrace.html)
