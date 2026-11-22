# 第 13 集｜AArch64 韌體離線 dump

[English](README.en.md)

練習韌體在 QEMU `virt` 讀入固定的 2750 毫伏，低於 3000 毫伏門檻，執行 `brk #0x42`。韌體例外處理程式把 x0–x30、SP、ELR_EL1、SPSR_EL1、ESR_EL1 及 FAR_EL1 保存到 RAM。採集器等到完成標記，再保存 32 KiB RAM 和同次建置的 SHA-256 指紋。

| 區段 | 位址與用途 |
| --- | --- |
| 韌體程式 | `0x40080000` 起，符號與指令由同版 ELF 提供 |
| 擷取的 RAM | `0x400c0000` 到 `0x400c7fff`，little endian |
| 例外紀錄 | RAM 基底先有 `FWLAB13` 標記，接續保存的 64 位元欄位 |
| 控制狀態 | `state` 位於 `0x400c1000`，由 GDB 按 C 型別解讀 |
| 堆疊 | 從 `0x400c8000` 往較低位址成長，樣本 SP 是 `0x400c7fe0` |

## 從來源重建

需 Python 3、AArch64 GCC、AArch64 QEMU 和支援 ARM64 的 GDB。預設從 PATH 找 `qemu-system-aarch64` 與 `aarch64-linux-gnu-gcc`。工具裝在其他位置時，可用 `FW_QEMU`、`FW_QEMU_DATA`、`FW_QEMU_LIBS` 指定安裝位置，也可用 `FW_CC` 指定交叉編譯器。若系統上的 GDB 不支援 AArch64，可用 `gdb-multiarch` 替代以下指令中的 `gdb`。實測 GCC 13.3.0、GDB 15.1。

從此目錄執行，方便 GDB 找到與捕捉檔對應的來源。

```sh
lab_dir=$(mktemp -d)
python3 capture.py "$lab_dir/sample"
rt="$lab_dir/sample"
readelf -h "$rt/firmware.elf"
readelf -n "$rt/firmware.elf"
python3 core.py "$rt/firmware.elf" "$rt/exception.ram" "$rt/manifest.json" "$rt/firmware.core"
gdb -nx -iex 'set debuginfod enabled off' "$rt/firmware.elf" "$rt/firmware.core"
```

GDB 裡依序讀出暫存器、指令、堆疊和 RAM。

```text
info registers pc sp x30
x/i $pc
bt
p state
x/4uw &state
```

## 核對版本不符與資料不足

```sh
python3 core.py "$rt/other-build.elf" "$rt/exception.ram" "$rt/manifest.json" "$lab_dir/wrong.core"
python3 core.py --omit-stack "$rt/firmware.elf" "$rt/exception.ram" "$rt/manifest.json" "$rt/partial.core"
gdb -nx -iex 'set debuginfod enabled off' -batch "$rt/firmware.elf" "$rt/partial.core" -ex 'x/4gx $sp'
```

版本不符時，轉換器拒收並回報 `ELF fingerprint mismatch`。縮減版沒有堆疊所在的記憶體區段，讀取 SP 會回報 `Cannot access memory`。轉換器只支援本練習格式，實際 dump 應依裝置的格式與記憶體地圖處理。

樣本可從此目錄直接開啟 `sample/firmware.elf` 和 `sample/firmware.core`，結果見 [GDB 輸出](sample/gdb.txt) 和 [配對紀錄](sample/manifest.json)。

[GDB 檔案指令](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Files.html) · [QEMU QMP](https://www.qemu.org/docs/master/interop/qemu-qmp-ref.html)
