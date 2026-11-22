# 第 12 集｜用 bpftrace 看延遲分布

[English](README.en.md)

在 observe_measure 入口和返回的探針配對，將時間差轉成微秒。用相同的工作負載比較正常、1 筆離群和整體變慢。

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

主機需安裝 AArch64 版 bpftrace，guest 核心需支援 BPF、kprobe 和 syscall tracepoints。實測 bpftrace 0.20.2。執行成功會看到 `VERIFY BPFTRACE OK`。 [直方圖與樣本輸出](sample.txt)

## 手動看探針和直方圖

進入 guest 後執行下列指令。[`latency.bt`](latency.bt) 以 `tid` 配對進入和返回，適合本練習依序執行且無遞迴的函式。[`workload`](workload) 執行 3 組固定輸入。

```sh
bpftrace -l 'tracepoint:syscalls:sys_enter_write'
bpftrace -l 'kprobe:observe_measure'
bpftrace -c '/bin/sh /lab/workload' /lab/latency.bt
```

| 模式 | 工作負載 | 應觀察到的變化 |
| --- | --- | --- |
| 0 | 正常基線 | 12 筆，多數落在低延遲區間 |
| 1 | 單筆較慢 | 12 筆，熱門區間相近，多出 1 筆慢尾 |
| 2 | 整體變慢 | 12 筆，主要區間往右移 |

區間邊界與筆數會受虛擬機排程影響，可以先確認樣本總數，再比對每組分布的變化。

[bpftrace 官方文件](https://bpftrace.org/docs/)
