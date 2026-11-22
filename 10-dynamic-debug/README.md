# 第 10 集｜驅動程式的 Debug Log 怎麼寫、怎麼用？

[English](README.en.md)

先用 debug mask 開關自己驅動裡的 PCIe、DMA 和 reset 日誌，再用 Dynamic Debug 觀察 USB core。最後可用 `observe_lab` 練習把範圍縮到 1 個印字點。

## 重跑環境

在 AArch64 Linux 主機準備 QEMU、AArch64 GCC、靜態連結的 AArch64 BusyBox、make、cpio 和 gzip。另備同一版的 AArch64 核心映像、核心 headers 和設定檔。實測使用 QEMU 8.2.2 與 Linux 6.17.0-1014-nvidia。程式把模組和練習腳本放進暫存 initramfs，啟動沒有對外網路的 guest。

從本目錄執行。把下列範例路徑換成同一版核心的實際檔案，再啟動練習。

```sh
export OBS_KERNEL=/path/to/arm64/Image
export OBS_HEADERS=/path/to/matching/headers
export OBS_CONFIG=/path/to/matching/kernel.config
```

如工具裝在其他位置，可用 `OBS_QEMU`、`OBS_CC` 或 `OBS_BUSYBOX` 指定。也可設定 `OBS_QEMU_DATA` 指向 QEMU 系統資料目錄。

## 1. 在驅動內用 debug mask 分流

執行 `bash run-usb-guest`。這個練習需要 `modinfo`、與核心相符的 HID 模組，以及對應的解壓工具（如 `zstd`）。所有下列 `/proc`、`/sys` 和 `dmesg` 操作都在隔離 guest 裡進行。

```sh
insmod /lab/log_mask.ko
cd /proc/demo_drv
original=$(cat debug_mask)
echo 0x05 > debug_mask
cat debug_mask
echo 1 > trigger
dmesg -c | grep DLOG
echo 0x04 > debug_mask
cat debug_mask
echo 1 > trigger
dmesg -c | grep DLOG
echo "$original" > debug_mask
cat debug_mask
```

PCIe、DMA 和 reset 各用 `0x01`、`0x02`、`0x04`。第 1 輪會印 PCIe 和 reset，第 2 輪只印 reset，2 輪都會印完成標記。可讀 [模組原始碼](log-mask/log_mask.c) 追蹤從 procfs 寫入到分類判斷的路徑。模組使用固定事件做示範。若專案透過 ioctl 設定 mask，觸發前讀回設定、比對日誌、最後還原的步驟也相同。

## 2. 用 Dynamic Debug 觀察 USB core

沿用同一個 guest。先確認核心有 `CONFIG_DYNAMIC_DEBUG=y`、控制檔列得出 `usbcore` 的印字點，再把虛擬埠設為預設不授權新裝置。

```sh
grep '^CONFIG_DYNAMIC_DEBUG=' /lab/kernel.config
control=/proc/dynamic_debug/control
grep -m 3 -F '[usbcore]' "$control"
for module in hid usbhid; do
    if [ -f "/lab/$module.ko" ]; then insmod "/lab/$module.ko"; fi
done
usb=/sys/bus/usb/devices
original_auth=$(cat "$usb/usb1/authorized_default")
echo 0 > "$usb/usb1/authorized_default"
dmesg -c >/dev/null
```

按 `Ctrl-a` 再按 `c` 進 QEMU monitor，輸入 `device_add usb-kbd,bus=xhci.0,port=1,id=lab-kbd`，再用同一組按鍵回 guest。等裝置列舉後執行以下指令。第 1 輪可看到 VID/PID 與未授權訊息，sysfs 只有 `1-1`。

```sh
pattern='idVendor|not authorized|port1: status|busnum'
dmesg -c | grep -E "$pattern"
ls -d "$usb"/1-1*
```

用 monitor 的 `device_del lab-kbd` 拔除虛擬鍵盤。回 guest 確認 `ls "$usb/1-1"` 已找不到裝置，再執行下列指令。

```sh
echo 'module usbcore file hub.c +p' > "$control"
dmesg -c >/dev/null
```

在同一個虛擬埠用相同的 monitor 指令插回鍵盤。等列舉後用同一條指令篩選，會多看到 port 狀態、`480 Mb/s` 和 bus 編號。授權後會出現 `1-1:1.0`，其 driver 應連到 `usbhid`。

```sh
dmesg -c | grep -E "$pattern"
echo 1 > "$usb/1-1/authorized"
readlink -f "$usb/1-1:1.0/driver"
echo 'module usbcore file hub.c -p' > "$control"
echo "$original_auth" > "$usb/usb1/authorized_default"
grep -F '[usbcore]' "$control" | grep 'hub[.]c:' | grep ' =[^ ]*p '
poweroff -f
```

在這份乾淨 guest 裡，最後 1 個搜尋應無輸出。

## 3. 把範圍縮到 observe_lab 的 1 個印字點

執行 `bash run-guest` 會跑自動核對，成功時顯示 `VERIFY DYNAMIC DEBUG OK`。執行 `bash run-guest shell` 可進入 guest 手動練習。 [完整實測片段](sample.txt)

進入 guest 後先讀控制檔。每列包括來源、模組、函式、目前旗標和格式字串。用同一組條件加 `+p`、`-p` 開關指定的印字點。

```sh
control=/proc/dynamic_debug/control
trigger=/sys/module/observe_lab/parameters/run
grep -F '[observe_lab]' "$control"
printf '%s\n' 'module observe_lab file observe_lab.c func observe_wait_ready +p' > "$control"
grep -F '[observe_lab]' "$control" | grep -F ' =p '
echo ready > "$trigger"
echo timeout > "$trigger"
dmesg | grep 'OBS '
printf '%s\n' 'module observe_lab file observe_lab.c func observe_wait_ready -p' > "$control"
grep -F '[observe_lab]' "$control" | grep observe_wait_ready
```

核對只有 `observe_wait_ready` 那一列有 `p`。正常輪顯示 `READY=1` 及 `ret=0`，逾時輪顯示 `READY=0` 及 `ret=-110`。最後一個讀取應看到這列的旗標還原為 `=_`。

[Linux Dynamic Debug 文件](https://docs.kernel.org/admin-guide/dynamic-debug-howto.html)
