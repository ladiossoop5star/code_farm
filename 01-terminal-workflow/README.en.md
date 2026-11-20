# Episode 01 · Terminal Workbench Quick Reference

[繁體中文](README.md)

Keep your editor, builds, and tests on a development host you can reconnect to over SSH. The device under test (DUT) runs the firmware or driver. The development host connects to it over UART, through a GDB debug link, or over the network, depending on the lab setup.

| Task | Where it runs | Tools |
| --- | --- | --- |
| Sign in or switch computers | Client | SSH and a terminal you know |
| Keep editing, build, and test panes available | Development host | Herdr or tmux |
| Navigate a large C codebase | Development host | Vim, cscope, ripgrep |
| Build, prepare tests, and save logs | Development host | GCC or Clang, make, a shell |
| Verify driver or firmware behavior | DUT | UART console and functional tests |

## Choose a terminal

| Platform | Terminal options |
| --- | --- |
| Windows | Windows Terminal with PowerShell or WSL |
| Linux desktop | GNOME Terminal, Ghostty, or Alacritty |
| macOS | Built-in Terminal or iTerm2 |
| Android | Termux |

Choose a terminal with keyboard handling, fonts, scrollback, and SSH support that work for you. Every client can use the toolchain, indexes, and test tools on the same development host.

## Check the SSH configuration

[ssh-config.example](ssh-config.example) uses an example hostname and account. Run this command from the exercise directory to check how OpenSSH interprets the file.

```sh
ssh -F ssh-config.example -G dev-server | sed -n '/^hostname /p; /^user /p; /^serveralive/p'
```

Expect `dev.example.com`, the user `developer`, a 30-second keepalive interval, and a limit of 3 unanswered probes. The command prints the resolved settings locally. Replace the example hostname, account, and key path with your own values before merging the entry into `~/.ssh/config`.

## Reconnect to the workbench from another terminal

1. Connect to your own development host. Open an editor inside Herdr or tmux, then run `sleep 120` in a second pane.
2. Disconnect the client. In another terminal, sign in to the same host and reattach to the session.
3. Check that both panes are still there. Programs can continue running when SSH disconnects as long as the host and session manager are still up. Save edits and logs to disk so you can recover them after a host restart.

[OpenSSH client configuration manual](https://man.openbsd.org/ssh_config)
