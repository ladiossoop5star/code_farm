# Episode 04 · Trace a gpio-keys failure with ripgrep

[繁體中文](README.md)

`logs/` contains the two QEMU self-test results from the episode. Use `rg` and Vim to follow the failure through the source excerpts, the two Device Tree files, and the guest self-test. Run these commands from the exercise directory.

```sh
rg -Fn -C 3 'gpio-keys input device missing' logs/disabled.log guest-src
rg --files boards -g '*.dts'
rg -n 'gpio-keys|MODULE_DEVICE_TABLE' linux/drivers/input/keyboard/gpio_keys.c
rg -n -C 3 'ifdef MODULE|define MODULE_DEVICE_TABLE' linux/include/linux/module.h
rg -n 'config KEYBOARD_GPIO|CONFIG_KEYBOARD_GPIO\)' linux/drivers/input/keyboard
rg -n -A 8 'gpio-keys \{' boards
```

The first search connects the error in the log to the place where the guest self-test stopped. The device match table and `MODULE_DEVICE_TABLE` lead to the driver and its header. Kconfig defines `KEYBOARD_GPIO`, which the Makefile uses to include `gpio_keys.o`. Both board files have the same `gpio-keys` compatible string.

```sh
diff -u boards/disabled.dts boards/enabled.dts
cat logs/disabled.log logs/enabled.log
```

The diff changes `status` from `disabled` to `okay`. Exit status 1 means differences were found. Both boots used the same kernel, module, and self-test. The first boot could not find the input device. Once the node was enabled, the self-test received `KEY_POWER`.

## Send matches to Vim Quickfix

```sh
quickfix=$(mktemp)
rg --vimgrep 'gpio-keys|MODULE_DEVICE_TABLE|KEYBOARD_GPIO' linux boards > "$quickfix"
vim -q "$quickfix"
```

Run `:copen` to see the matches and press Enter or use `:cnext` to jump to a hit. Start Vim in the directory where you ran `rg` so the relative paths resolve. Narrow the directory or glob if the list contains unrelated results.

The Linux excerpts in `linux/` retain the source notices and SPDX identifiers. See [GPL v2](COPYING-GPL-2.0). The board files are the decompiled Device Tree and its test variant from the QEMU virt exercise. The search workflow runs entirely offline with the included files. [Upstream Linux source](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/) · [ripgrep guide](https://github.com/BurntSushi/ripgrep/blob/master/GUIDE.md)

## Reproduce the runtime result

Use QEMU 8.2.2 for ARM64, `dtc`, `cpio`, `gzip`, Python 3, an AArch64 C toolchain with static libraries, and a static AArch64 BusyBox with the guest script's applets. Supply an ARM64 Linux kernel for the QEMU virt machine and its matching uncompressed `gpio_keys.ko`. The kernel config needs `CONFIG_KEYBOARD_GPIO=m`, with the module's dependencies available at boot. The episode used a build with its dependencies available in the kernel and the same kernel image, module, and initramfs for both boots.

Set `kernel`, `module`, and `busybox` to absolute paths for those three files. Set `guest_cc` to an AArch64 compiler such as `aarch64-linux-gnu-gcc`. Run the rest of this section from the exercise directory in one shell.

~~~sh
work=$(mktemp -d)
mkdir -p "$work/root/bin" "$work/root/dev" "$work/root/proc" "$work/root/sys"
install -m 0755 "$busybox" "$work/root/bin/busybox"
install -m 0755 guest-src/init "$work/root/init"
install -m 0644 "$module" "$work/root/gpio_keys.ko"
"$guest_cc" -static -O2 guest-src/check-key.c -o "$work/root/check-key"
(cd "$work/root" && find . -print0 | cpio --null -o -H newc | gzip) > "$work/guest.cpio.gz"
dtc -I dts -O dtb -o "$work/disabled.dtb" boards/disabled.dts
dtc -I dts -O dtb -o "$work/enabled.dtb" boards/enabled.dts
~~~

The decompiled board files differ in the `gpio-keys` node's status. Both boots use the same kernel, initramfs, and command line.

~~~sh
boot_guest() {
    variant=$1
    shift
    qemu-system-aarch64 -machine virt,acpi=off -cpu cortex-a57 \
        -m 1024 -smp 2 -nodefaults -nic none -display none -serial stdio -monitor none \
        -kernel "$kernel" -initrd "$work/guest.cpio.gz" -dtb "$work/$variant.dtb" \
        -append 'console=ttyAMA0 rdinit=/init quiet' "$@"
}
boot_guest disabled
~~~

Expect `DT status=disabled` and `DUT SELFTEST FAIL: gpio-keys input device missing`.

For the enabled boot, save the absolute path printed by the first command. In another terminal, run `python3 press-power.py /path/to/qmp.sock` when the guest prints `DUT READY: waiting for KEY_POWER`. The self-test waits five seconds for the simulated key.

~~~sh
printf '%s\n' "$work/qmp.sock"
boot_guest enabled -qmp "unix:$work/qmp.sock,server=on,wait=off"
~~~

Expect `DT status=okay`, a `BOUND` line showing the sysfs driver link, and then `DUT SELFTEST PASS: received KEY_POWER`. If you leave the simulated key alone, the enabled test reports `DUT SELFTEST FAIL: KEY_POWER event missing`. The three results show device discovery, driver binding, and event delivery at different points in the test.
