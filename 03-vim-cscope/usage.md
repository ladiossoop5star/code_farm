# Vim + cscope workflow for C projects

Use this guide to reproduce the setup from the video, adapt the mappings to
your own projects, and follow the receive-path exercise. The example
configuration is [.vimrc](.vimrc). The exercise files are in
[demo-driver](demo-driver/).

## Install and check the dependencies

Use terminal Vim with `+cscope`, `+quickfix`, and `+terminal`. The setup was verified
with Vim 9.1, cscope 15.9, Universal Ctags 5.9.0, ripgrep 14.1.0, and fzf 0.75.0.
The exercise also needs make and a C compiler.

~~~sh
vim --version | grep -E 'cscope|quickfix|terminal'
cscope -V
ctags --version
rg --version
~~~

Check that the ctags version output identifies **Universal Ctags**. If your
distribution exposes it as `ctags-universal`, use that name when generating
tags and point Tagbar at the same executable with
`let g:tagbar_ctags_bin = '/path/to/ctags-universal'`.

Run the bootstrap from the directory containing this guide. It installs
the pinned fzf executable and Vim runtime and fetches the Gruvbox colorscheme.
The remaining plugins are included under `.vim/pack/workbench/start`.

~~~sh
sh bootstrap.sh
~~~

| Component | Role |
| --- | --- |
| fzf.vim | Pickers for files, text matches, tags, and jump history |
| Tagbar | Current-file symbol outline, generated on demand with Ctags |
| vim-airline and vim-airline-themes | Status line and tabpage labels with the understated theme |
| vim-bookmarks | Bookmark signs, annotations, navigation, and persistence |
| Gruvbox | Dark editor colors |

See [THIRD_PARTY.md](THIRD_PARTY.md) for the exact revisions, licenses, and
upstream repositories. The exercise command below loads the bundled packages.
To adapt the setup for everyday use, install the packages with your usual
plugin manager and merge the settings you want into `~/.vimrc` after backing
it up. Keep one copy of each plugin.
Airline shows the current mode, file, and position. The example keeps
Airline's tabpage labels and turns off its buffer list. The vimrc also defines
a native statusline for use without Airline.

## Build the project indexes

Start in the workbench directory and keep the full project path free of
spaces. Vim's cscope integration on the tested setup could not connect to
an index under a path containing spaces. The same file list feeds both
indexes.

~~~sh
cd demo-driver
find include src tests -type f \( -name '*.c' -o -name '*.h' \) |
  LC_ALL=C sort > cscope.files
cscope -Rbq
ctags -L cscope.files
vim -Nu ../.vimrc -i NONE -n
~~~

| Item | Purpose |
| --- | --- |
| `cscope.files` | Inspectable list of source files to index. Paths in this example are relative to the project root |
| `cscope -Rbq` | Builds the database in batch mode with `-b` and creates the fast inverted index with `-q`. The `-R` flag enables recursive discovery where applicable |
| `cscope -k` | Skips the default system include directory. Add it when indexing a self-contained tree such as the Linux kernel |
| `ctags -L cscope.files` | Builds the project `tags` file for tag jumps and `:Tags` |
| `make index` | Shortcut provided by the fixture. It regenerates `cscope.files` and uses `cscope -bqk -i cscope.files` before building tags |

The example vimrc connects to `cscope.out` in Vim's startup directory. If you
create the database after opening Vim, run `:cs add cscope.out` from the project
root or press **F5** with the example configuration. Use `:cs show` to inspect
the active connection and `:pwd` to verify the working directory.

- After saving edits to indexed files, press **F5** to rebuild and reload
  cscope. The supplied mapping adds `-u` to the command shown in the video
  so that an edit saved in the same second as the last build is picked up.
  It resets an existing connection or adds the database if needed.
- After adding, removing, or moving files, regenerate `cscope.files` before
  pressing **F5**. Update tags separately with `ctags -L cscope.files`,
  or run `make index` in the fixture and `:cs reset` in an open Vim session.
- In your own tree, select source roots relevant to the issue. Exclude
  generated files, other architectures, or vendor directories when they are
  outside the investigation. Include shared headers and implementation
  directories that can contain evidence. Keep a separate index per checkout
  when switching branches or worktrees frequently.

## Keyboard reference

Keys below are for Normal mode unless a row specifies a command-line
operation. Press **Esc** to return to Normal mode.

| Keys or command | Action |
| --- | --- |
| `i`, `a`, `o` | Insert before the cursor, insert after it, or open a new line below |
| `I`, `A`, `O` | Insert at the first nonblank character, append at the end of the line, or open a new line above |
| `x`, `dd`, `yy`, `p` | Delete a character, delete a line, yank a line, or put the current register contents after the cursor or below the line |
| `u`, Ctrl-r, `.` | Undo, redo, or repeat the last change |
| `/pattern`, Enter, `n`, `N` | Search forward, accept the pattern, then repeat in the same or opposite direction. The example uses incremental search, highlighting, and smart case |
| `:w`, `:q`, `:wq`, `ZZ`, `:q!` | Save, quit, save and quit, write if changed and quit, or force quit without writing |
| `vim path`, `:e path` | Open a file from the shell or from inside Vim |
| Ctrl-o, Ctrl-i | Jump to an older or newer cursor location. Some terminals send the same key code for Ctrl-i and Tab |
| `:split [file]`, `:vsplit [file]` | Add a horizontal or vertical split |
| Ctrl-w followed by an arrow key | Move focus between split windows |
| `:tabe path`, `:tab split`, `:tabclose` | Open a file in a new tabpage, open the current buffer in a new tabpage, or close the current tabpage |

The example routes `x`, `dd`, `D`, `cc`, `C`, `s`, and `S` through Vim's black-hole
register (`"_`). For example, yank a line with `yy`, delete an unrelated line
with `dd`, and use `p` to paste the original yank. These are personal mappings
that can be omitted if you prefer Vim's usual register behavior.

| Configured key | Command or action |
| --- | --- |
| Ctrl-p | `:Files`, fuzzy file selection |
| `\r` | `:Rg`, text matches from ripgrep |
| `\t` | `:Tags`, project tag selection |
| `\j` | `:Jumps`, the jump list |
| Ctrl-k / Ctrl-l | Previous / next tabpage |
| F3 | Show or hide the current Quickfix list |
| F5 | Rebuild and reload cscope |
| F6 / F7 | Save / load bookmarks in `.bookmark` in the working directory |
| F8 | `:TagbarToggle` |

The Leader key in this configuration is a plain backslash. The cscope
prefix is **Ctrl+backslash**. Hold Ctrl while pressing backslash, release
both keys, then enter the query letter. Place the cursor on a symbol for
symbol queries or on a filename for f and i.

| Query letter | Example command | Result |
| --- | --- | --- |
| `s` | `:cs find s demo_rx_poll` | Indexed symbol references |
| `g` | `:cs find g demo_rx_poll` | Global definition |
| `c` | `:cs find c demo_rx_poll` | Callers cscope recognizes |
| `t` | `:cs find t demo_rx_poll` | Text occurrences |
| `e` | `:cs find e demo_rx_.*` | Extended regular-expression matches |
| `f` | `:cs find f demo_driver.h` | Files with matching names |
| `i` | `:cs find i demo_driver.h` | Files that include the header |
| `d` | `:cs find d demo_rx_poll` | Functions called from the selected function |

The command form works even when a terminal intercepts Ctrl+backslash.
Vim accepts `:cs f t` as a shorter spelling of `:cs find t`.

## Use the fzf pickers

1. **Files**. Press **Ctrl-p** from the project root, type demo_rx, and
   press **Enter** on src/demo_rx.c. The supplied file listing uses rg,
   includes hidden files, excludes .git, and respects ignore rules.
2. **Tags**. Press `\t` or run `:Tags demo_rx_poll`. Choose the definition
   and press **Enter** to jump. Rebuild the tags file when definitions move.
   Vim's built-in :tag demo_rx_poll also uses the tags file.
3. **Jumps**. After several jumps, press `\j` and select a previous
   location. Use **Ctrl-o** and **Ctrl-i** for sequential travel through Vim's
   jump list.
4. **Rg**. Run `:Rg demo_rx_poll` to seed a ripgrep search, or press `\r`
   and narrow the picker. Use **Tab** on individual results or **Alt-a** for
   all matches in the filtered list. **Enter** sends a multi-selection to Quickfix in this
   configuration. **Alt-d** clears the selection. With generated files in
   scope, additional matches can appear in tags or other text artifacts.

## Follow the receive-path investigation

1. From the fixture root, run make to compile and make test to confirm
   the deliberate timeout failure. Open `src/demo_rx.c` through **Ctrl-p**.
   Press **F8**, move into the right-hand outline with **Ctrl-w** then
   **Right**, select `demo_rx_poll`, and press **Enter**. Press
   **F8** again to close the outline. This view describes the current C file.
2. Try :cs find c demo_rx_poll. The fixture yields no direct caller.
   Try :cs find s demo_rx_poll for references or :cs find t demo_rx_poll
   for textual occurrences. The text query returns three candidates in
   this fixture and takes you to the first. The t- entry in
   cscopequickfix replaces the active Quickfix list with the new text results.
3. Press **F3** and open the src/demo_probe.c entry with **Enter**. The
   other two entries are the declaration in include/demo_driver.h and the
   definition in src/demo_rx.c. The assignment .poll = demo_rx_poll in
   demo_probe.c is the callback registration. **F3** hides or shows this
   same list so you can revisit another result without running the query
   again. A later query or bookmark listing can change the active list.
4. Keep separate tabpages for the callback registration, the poll
   implementation, and the timeout branch. Use :tab split to retain the
   current file in another tabpage or :tabe src/demo_rx.c to open it directly.
   A tabpage retains its window layout. **Ctrl-k** and **Ctrl-l** switch
   between those layouts.
5. Run :cs find d demo_rx_poll to reach the call to demo_clean_rx_irq.
   Follow the normal path into demo_release_rx_buffer in src/demo_dma.c.
   Compare that cleanup with the allocation rollback in demo_refill_rx_ring
   and with the timeout branch in src/demo_rx.c. Use bookmarks to label the
   normal cleanup and the missing timeout cleanup.
6. In the disposable fixture, add the following line inside the marked
   timeout cleanup block, before the descriptor is marked free. Confirm
   that this path still owns the mapped buffer before applying the same
   idea to a real driver. In real DMA code, check the pairing, direction,
   length, device, and mapping state before unmapping.

   ~~~c
   demo_release_rx_buffer(adapter, desc);
   ~~~

7. Save the file. Review git diff -- src/demo_rx.c if the fixture is tracked.
   Build with make, then rerun make test. Expect
   PASS timeout cleanup released DMA buffer and descriptor.
   The video's Code, Build, and Test tabs keep these activities in separate
   workspaces. The same steps also work from one shell.

### Bookmark controls

| Keys | Action |
| --- | --- |
| `mm` | Toggle the bookmark on the current line |
| `mi` | Add or edit an annotation |
| `mn` / `mp` | Jump to the next / previous bookmark |
| `ma` | List bookmarks in Quickfix |
| `mc` / `mx` | Clear bookmarks for the current file / across all files |
| F6 / F7 | Save / reload the working directory's `.bookmark` file |

Use a stable working directory when saving and loading. Keep the .bookmark
file local when it contains private paths or annotations. Save explicitly
with **F6** before closing Vim.

## Verify and adapt the configuration

Run these from Vim after opening the fixture and building the indexes.

~~~vim
:echo $MYVIMRC
:scriptnames
:verbose nmap <C-p>
:verbose nmap <C-k>
:verbose nmap <C-l>
:verbose nmap <C-\>t
:verbose nmap <F5>
:verbose nmap mm
:set cscopequickfix? tags?
:set paste? autoindent? softtabstop? showmatch? ruler?
:cs show
:echo executable('fzf') executable('rg') executable('ctags') executable('cscope')
~~~

- Check the last defining file in :verbose nmap if an older plugin or
  local autocmd changes a key. Then restart Vim and test the mapping in
  Normal mode in the affected filetype.
- If indentation or rulers behave differently, check :set paste?. The
  example starts with nopaste. You can run :set paste, inspect the
  affected options, then run :set nopaste and verify that your normal
  settings return.
- If :Files or :Rg is missing, confirm that both fzf's Vim runtime and
  fzf.vim loaded. If the commands exist but fail, check the fzf and rg
  executables, their versions, and the current directory.
- If Tagbar is empty, check :set filetype? and ctags --version. If
  :Tags is empty, check :set tags? and rebuild the project tags file.
  Tagbar generates a current-file outline on demand.
- If cscope outputs no results, verify :cs show and inspect cscope.files
  for the missing source. Rebuild the database following scope changes.
  Check both direct calls and references before drawing conclusions.
- To customize the setup, edit the key mappings and Leader in your own
  vimrc, your file selection rules in the index command, and your package
  revisions in your plugin manager or native package directories. Test one
  change at a time using the commands above.

## Read the evidence

Tagbar gives you a file outline. A cscope definition or reference shows what
is present in the indexed source. A callback assignment shows where the
function is registered. Verify build inclusion against the active Kconfig,
Makefile, and actual build artifacts. Verify runtime execution with a test,
log, trace, or debugger. In the exercise, make test calls the registered
callback and checks cleanup after a timeout.

## Sharing the setup

Keep the bundled packages' notices and license files with their source.
See [THIRD_PARTY.md](THIRD_PARTY.md) for which dependencies are bundled
and which are fetched from their upstream repositories.
