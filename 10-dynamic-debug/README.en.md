# Episode 10 · How to write and use driver debug logs

[繁體中文](README.md)

Use a debug mask to select PCIe, DMA, and reset messages in your own driver. Then use Dynamic Debug to observe USB core. The `observe_lab` exercise shows how to narrow a query to one log site.

## Run the exercise

On an AArch64 Linux host, prepare QEMU, AArch64 GCC, a statically linked AArch64 BusyBox, make, cpio, and gzip. Supply an AArch64 kernel image, matching headers, and the configuration used to build it. The exercise was tested with QEMU 8.2.2 and Linux 6.17.0-1014-nvidia. The runner creates a temporary initramfs containing the module and exercise scripts, then boots a guest without an external network interface.

Replace these example paths with files from the same kernel build and run from this directory.

```sh
export OBS_KERNEL=/path/to/arm64/Image
export OBS_HEADERS=/path/to/matching/headers
export OBS_CONFIG=/path/to/matching/kernel.config
```

Use `OBS_QEMU`, `OBS_CC`, or `OBS_BUSYBOX` to override tool locations. `OBS_QEMU_DATA` points to the QEMU data directory when needed.

## 1. Select driver log categories with a debug mask

Run `bash run-usb-guest`. This exercise also requires `modinfo`, the matching HID modules, and the decompressor for the modules (such as `zstd`). Run the following `/proc`, `/sys`, and `dmesg` commands inside the isolated guest.

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

The PCIe, DMA, and reset bits are `0x01`, `0x02`, and `0x04`. The first run prints PCIe and reset messages. The second prints only reset messages. Both print a completion marker. Follow the write from procfs to the category checks in the [module source](log-mask/log_mask.c). The module uses fixed sample events. If your driver exposes the mask through an ioctl, the same readback, log comparison, and restore steps apply.

## 2. Observe USB core with Dynamic Debug

Stay in the same guest. Check that the kernel has `CONFIG_DYNAMIC_DEBUG=y` and that the control file lists `usbcore` sites. Set the virtual port to leave newly attached devices unauthorized by default.

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

Press `Ctrl-a`, then `c` to open the QEMU monitor. Enter `device_add usb-kbd,bus=xhci.0,port=1,id=lab-kbd`. Use the same keys to return to the guest. Allow enumeration to finish, then run the commands below. The baseline shows the VID/PID and an authorization message. Only `1-1` appears in sysfs.

```sh
pattern='idVendor|not authorized|port1: status|busnum'
dmesg -c | grep -E "$pattern"
ls -d "$usb"/1-1*
```

Remove the keyboard with `device_del lab-kbd` in the monitor. Return to the guest and confirm that `ls "$usb/1-1"` can no longer find the device. Then run the following commands.

```sh
echo 'module usbcore file hub.c +p' > "$control"
dmesg -c >/dev/null
```

Reattach the keyboard with the same monitor command. After enumeration, the same log filter now shows port status, `480 Mb/s`, and the bus number. Authorizing the device creates the `1-1:1.0` interface. Its driver should point to `usbhid`.

```sh
dmesg -c | grep -E "$pattern"
echo 1 > "$usb/1-1/authorized"
readlink -f "$usb/1-1:1.0/driver"
echo 'module usbcore file hub.c -p' > "$control"
echo "$original_auth" > "$usb/usb1/authorized_default"
grep -F '[usbcore]' "$control" | grep 'hub[.]c:' | grep ' =[^ ]*p '
poweroff -f
```

The last search should print nothing in this fresh guest.

## 3. Narrow the query to one observe_lab site

Run `bash run-guest` for the automated exercise. A successful run prints `VERIFY DYNAMIC DEBUG OK`. Run `bash run-guest shell` for the manual exercise below. [Recorded output](sample.txt)

Inside the guest, inspect the control file. Each row shows the source location, module, function, flags, and message format. Add `+p` or `-p` to the same selection to enable or disable printing.

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

Check that only the row for `observe_wait_ready` has the `p` flag. The successful run prints `READY=1` and `ret=0`. The timeout prints `READY=0` and `ret=-110`. The final read should show the original `=_` flag.

[Linux Dynamic Debug documentation](https://docs.kernel.org/admin-guide/dynamic-debug-howto.html)
