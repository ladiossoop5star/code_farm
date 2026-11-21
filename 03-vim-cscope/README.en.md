# Vim + cscope Workbench

[繁體中文](README.md)

Reproduce the video's C navigation workflow with Vim, fzf, Tagbar, cscope,
Quickfix, and bookmarks. The sample driver runs as a local C program.

Install terminal Vim with +cscope, +quickfix, and +terminal, plus cscope,
Universal Ctags, ripgrep, Git, make, and a C compiler. The bootstrap script
fetches Gruvbox and the fzf runtime and executable from upstream.

~~~sh
sh bootstrap.sh
cd demo-driver
make index
vim -Nu ../.vimrc -i NONE -n
~~~

Extract the workbench to a path without spaces for Vim's cscope
connection. Run these commands from the workbench directory. The Vim
command uses the bundled configuration and skips Vim info and swap files.
Inside Vim, press **Ctrl-p**, type *demo_rx*, and open *src/demo_rx.c*.

Read [usage.md](usage.md) for the full exercise and key reference.
See [THIRD_PARTY.md](THIRD_PARTY.md) for package versions and licenses.
