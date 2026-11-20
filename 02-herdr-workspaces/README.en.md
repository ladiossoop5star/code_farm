# Episode 02 · Herdr Workspaces Quick Reference

[繁體中文](README.md)

Install the Herdr TUI on your development host. Use a Space for each task, Tabs for different kinds of work, and Panes for the programs themselves. [Herdr TUI documentation](https://herdr.dev/tui/docs/)

| Work shown in the episode | Suggested location |
| --- | --- |
| Navigate driver code and review diffs | Code tab |
| Compile and keep the build output | Build tab |
| Run a self-test and watch the UART console | Two panes in the Test tab |
| Handle an urgent task | A separate Space |

## Exercise

1. Run `herdr` and create a Space named `dma-driver-debug` in the sidebar. Add Code, Build, and Test tabs. Right-click to split the Test tab, then drag the divider to resize the panes.
2. Run `sleep 120` in the Build or Test tab to stand in for a long job. Switch to another Space and back. The process should still be in the same pane.
3. Detach or disconnect SSH, then sign in to the original host with the same account and run `herdr` again. Keep the host and Herdr server running during the exercise.
4. If you use a supported agent, use the sidebar to open the pane of an agent that is waiting for confirmation. The status depends on the agent integration.

The default prefix is `Ctrl+b`. Press the prefix and then `?` for active shortcuts, `c` to create a tab, or `q` to detach while leaving the background session running. [Keyboard guide](https://herdr.dev/tui/docs/keyboard/)

## Try the configuration

[config.toml.example](config.toml.example) enables mouse controls and prompts for the name of a new tab, as shown in the episode. On Linux or macOS, validate it with a temporary configuration directory.

```sh
config_root=$(mktemp -d)
mkdir "$config_root/herdr"
cp config.toml.example "$config_root/herdr/config.toml"
XDG_CONFIG_HOME="$config_root" herdr config check
```

The example passed with Herdr 0.8.0. Run `herdr --help` to locate your active configuration before merging in the settings you want. [Configuration guide](https://herdr.dev/tui/docs/configuration/)
