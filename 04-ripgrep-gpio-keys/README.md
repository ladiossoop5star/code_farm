# 第 04 集｜從一行 log 追到 gpio-keys

[English](README.en.md)

`logs/` 收錄影片中 2 次 QEMU 自測的結果。這個練習用 `rg` 和 Vim 重走定位路徑，會用到原始碼摘集、2 份 Device Tree 和自測程式。從本目錄執行下列指令。

```sh
rg -Fn -C 3 'gpio-keys input device missing' logs/disabled.log guest-src
rg --files boards -g '*.dts'
rg -n 'gpio-keys|MODULE_DEVICE_TABLE' linux/drivers/input/keyboard/gpio_keys.c
rg -n -C 3 'ifdef MODULE|define MODULE_DEVICE_TABLE' linux/include/linux/module.h
rg -n 'config KEYBOARD_GPIO|CONFIG_KEYBOARD_GPIO\)' linux/drivers/input/keyboard
rg -n -A 8 'gpio-keys \{' boards
```

第一個搜尋從相同錯誤行找到自測停止的位置。接著查看驅動的配對表和 `MODULE_DEVICE_TABLE` 的定義。Kconfig 選項是 `KEYBOARD_GPIO`，Makefile 透過 `CONFIG_KEYBOARD_GPIO` 納入 `gpio_keys.o`。板級檔案的 `compatible` 保持 `gpio-keys`，用以下對照確認節點狀態的差異。

```sh
diff -u boards/disabled.dts boards/enabled.dts
cat logs/disabled.log logs/enabled.log
```

`diff` 顯示狀態從 `disabled` 變成 `okay`，結束碼 1 代表找到差異。影片保持 kernel、模組與自測程式一致。失敗輪找不到輸入裝置，啟用後的成功輪收到 `KEY_POWER`。

## 把結果送進 Vim Quickfix

```sh
quickfix=$(mktemp)
rg --vimgrep 'gpio-keys|MODULE_DEVICE_TABLE|KEYBOARD_GPIO' linux boards > "$quickfix"
vim -q "$quickfix"
```

在 Vim 執行 `:copen` 看清單，再用 `:cnext` 或 Enter 跳到命中處。從相同目錄啟動 Vim，清單裡的相對路徑才會對上。需要更精確的結果時，縮小 `rg` 指令的目錄或 glob。

`linux/` 是影片使用的 Linux 核心來源摘集，保留檔頭與 SPDX 標記，授權見 [GPL 第 2 版](COPYING-GPL-2.0)。`boards/` 是 QEMU virt 練習的反編譯 Device Tree 及對照版本。兩份原始紀錄可離線重讀，從來源重跑搜尋無需建置 Linux。

[Linux 核心上游來源](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/) · [ripgrep 使用說明](https://github.com/BurntSushi/ripgrep/blob/master/GUIDE.md)

## 在 QEMU 重跑兩個案例

準備 QEMU 8.2.2 AArch64、dtc、cpio、gzip、Python 3、可靜態編譯的 AArch64 C 工具鏈和靜態 BusyBox。使用能在 QEMU virt 啟動的 ARM64 核心及其同版、已解壓縮的 `gpio_keys.ko`。本次設定為 `CONFIG_KEYBOARD_GPIO=m`，模組依賴已編入核心。把以下範例路徑換成實際位置，從教材目錄開始。

```sh
kernel=/path/to/arm64/Image
module=/path/to/gpio_keys.ko
busybox=/path/to/aarch64/static-busybox
guest_cc=aarch64-linux-gnu-gcc
work=$(mktemp -d)
mkdir -p "$work/root/bin" "$work/root/dev" "$work/root/proc" "$work/root/sys"
install -m 0755 "$busybox" "$work/root/bin/busybox"
install -m 0755 guest-src/init "$work/root/init"
install -m 0644 "$module" "$work/root/gpio_keys.ko"
"$guest_cc" -static -O2 guest-src/check-key.c -o "$work/root/check-key"
(cd "$work/root" && find . -print0 | cpio --null -o -H newc | gzip) > "$work/guest.cpio.gz"
dtc -I dts -O dtb -o "$work/disabled.dtb" boards/disabled.dts
dtc -I dts -O dtb -o "$work/enabled.dtb" boards/enabled.dts
```

同一個 shell 繼續執行。兩輪共用核心、initramfs 與核心參數，切換的只有 DTB。

```sh
boot_guest() {
    variant=$1
    shift
    qemu-system-aarch64 -machine virt,acpi=off -cpu cortex-a57 \
        -m 1024 -smp 2 -nodefaults -nic none -display none -serial stdio -monitor none \
        -kernel "$kernel" -initrd "$work/guest.cpio.gz" -dtb "$work/$variant.dtb" \
        -append 'console=ttyAMA0 rdinit=/init quiet' "$@"
}
boot_guest disabled
```

第一輪應看到 `DT status=disabled` 和 `DUT SELFTEST FAIL: gpio-keys input device missing`。跑下一輪時，先記下所印的 socket 路徑。

```sh
printf '%s\n' "$work/qmp.sock"
boot_guest enabled -qmp "unix:$work/qmp.sock,server=on,wait=off"
```

看到 `DUT READY: waiting for KEY_POWER` 時，在另一個終端執行 `python3 press-power.py /path/to/qmp.sock`，換成剛才印出的完整路徑。等候時間是 5 秒。成功輪會依序顯示 `DT status=okay`、`BOUND` 和 `DUT SELFTEST PASS: received KEY_POWER`。如果省略模擬按鍵，已綁定裝置的自測會回報 `DUT SELFTEST FAIL: KEY_POWER event missing`。
