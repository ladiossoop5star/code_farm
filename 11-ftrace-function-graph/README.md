# 第 11 集｜用 ftrace 比較驅動程式的 2 條路

[English](README.en.md)

以 observe_probe 為追蹤根，在 2 個分開的取樣窗口擷取 ready 和 timeout。比較子呼叫、耗時、回傳值與追蹤緩衝區。

## 重跑環境

在 AArch64 Linux 主機準備 QEMU、AArch64 GCC、靜態連結的 AArch64 BusyBox、make、cpio 和 gzip。另備同一版的 AArch64 核心映像、核心 headers 和設定檔。實測使用 QEMU 8.2.2 與 Linux 6.17.0-1014-nvidia。程式把模組和練習腳本放進暫存 initramfs，啟動沒有對外網路的 guest。

從本目錄執行。把下列範例路徑換成同一版核心的實際檔案，再啟動練習。

```sh
export OBS_KERNEL=/path/to/arm64/Image
export OBS_HEADERS=/path/to/matching/headers
export OBS_CONFIG=/path/to/matching/kernel.config
bash run-guest
```

如工具裝在其他位置，可用 `OBS_QEMU`、`OBS_CC` 或 `OBS_BUSYBOX` 指定。也可設定 `OBS_QEMU_DATA` 指向 QEMU 系統資料目錄。下文的手動操作以 `bash run-guest shell` 進入練習 guest 後執行。`poweroff -f` 結束 guest。

核心需支援 `CONFIG_FUNCTION_GRAPH_TRACER` 和 `CONFIG_FUNCTION_GRAPH_RETVAL`。執行成功會看到 `VERIFY FUNCTION GRAPH OK`。 [實測呼叫圖和統計](sample.txt)

## 擷取與比對

進入 guest 後，列出 tracer 和可追函式。以下使用專用 guest 的 tracefs 頂層控制。

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

正常輪走到 `observe_enable_queue`，外層回 0。逾時輪是 `observe_wait_ready` 回 `-110`、外層呼叫 `observe_cleanup`，最後外層回同一個 `-110`。樣本的 `0xffffff92` 依對應函式的 32 位元有號回傳型別解讀。

比對時核對每顆 CPU 的 `overrun` 和 `dropped events`。正常與逾時的時間會因環境而變，先核對呼叫路徑和回傳值。

[Linux ftrace 文件](https://docs.kernel.org/trace/ftrace.html)
