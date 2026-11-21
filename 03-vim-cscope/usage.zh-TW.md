# 用 Vim 和 cscope 追查 C 專案

[English guide](usage.md) · [回教材首頁](README.md)

這份手冊從 [Vim 設定檔](.vimrc) 和 [C 驅動練習](demo-driver/) 出發，依序找到接收函式的註冊位置、正常清理路徑和逾時分支。

## 準備工具

使用支援 `+cscope`、`+quickfix` 和 `+terminal` 的終端版 Vim。原練習已用 Vim 9.1、cscope 15.9、Universal Ctags 5.9.0、ripgrep 14.1.0 和 fzf 0.75.0 驗證。編譯練習還需要 make 和 C 編譯器。

```sh
vim --version | grep -E 'cscope|quickfix|terminal'
cscope -V
ctags --version
rg --version
sh bootstrap.sh
```

確認版本輸出是 **Universal Ctags**。如果發行版把它命名為 `ctags-universal`，產生索引時改用該名稱，也可在 Vim 裡以 `let g:tagbar_ctags_bin = '/path/to/ctags-universal'` 指定執行檔。

安裝腳本會從上游取回 fzf 和 Gruvbox。其他插件已放在 `.vim/pack/workbench/start/`。fzf.vim 提供檔案、文字、標籤和跳轉記錄的選擇器，Tagbar 顯示當前檔案的符號大綱，Airline 顯示狀態列與分頁，vim-bookmarks 提供書籤。版本和授權見 [THIRD_PARTY.md](THIRD_PARTY.md)。要放入日常設定，可以先備份 `~/.vimrc`，再把需要的插件和鍵位合併進去。

## 建立和更新索引

從教材目錄開始，使用完整路徑沒有空格的工作目錄。可執行 `make index`，也可以自己產生檔案清單。

```sh
cd demo-driver
find include src tests -type f \( -name '*.c' -o -name '*.h' \) |
  LC_ALL=C sort > cscope.files
cscope -Rbq
ctags -L cscope.files
vim -Nu ../.vimrc -i NONE -n
```

`cscope.files` 可直接檢查索引範圍。cscope 的 `-b` 建立資料庫，`-q` 加上快速索引，`-R` 可依適用範圍遞迴。索引 Linux 核心這類自帶標頭檔的專案時，可用 `-k` 略過系統預設的 include 目錄。`ctags -L cscope.files` 為 `:tag` 和 `:Tags` 產生標籤。練習的 `make index` 用 `cscope -bqk -i cscope.files` 後再建立標籤。

- 在 Vim 執行 `:cs show` 查看索引連線，用 `:pwd` 核對工作目錄。如果先開了 Vim 再建索引，從專案根目錄執行 `:cs add cscope.out` 或按 **F5**。
- 改完已在清單裡的檔案後按 **F5**。設定裡用 `-u` 強制重建，檔案在同一秒內存檔也會被索引。
- 新增、移動或刪除檔案後，先更新 `cscope.files`，再建 cscope 和 tags。已開著 Vim 時可執行 `:cs reset`。
- 可按調查範圍選擇來源目錄。切換分支或 worktree 時，讓各個 checkout 用自己的索引。

## 鍵位速查

下列為教材的 Normal mode 鍵位，先按 **Esc** 回到 Normal mode。教材把 `x`、`dd`、`D`、`cc`、`C`、`s`、`S` 指向黑洞暫存器，想沿用 Vim 預設行為時可移除這些個人映射。

| 鍵位或指令 | 用途 |
| --- | --- |
| `i`、`a`、`o`，或 `I`、`A`、`O` | 從游標、行首、行尾或新行開始編輯 |
| `x`、`dd`、`yy`、`p` | 刪字、刪行、複製行、貼上 |
| `u`、Ctrl-r、`.` | 復原、重做、重複上一次修改 |
| `/pattern`、`n`、`N` | 搜尋及前後跳轉 |
| `:w`、`:q`、`:wq`、`ZZ`、`:q!` | 儲存或離開 |
| `:e path`、`:split`、`:vsplit` | 開檔、水平或垂直分割 |
| Ctrl-w 再按方向鍵 | 切到相鄰視窗 |
| `:tabe path`、`:tab split`、`:tabclose` | 開啟、複製或關閉分頁配置 |
| Ctrl-p | 用 fzf 選檔 |
| `\r`、`\t`、`\j` | 搜尋文字、選標籤、開跳轉記錄 |
| Ctrl-o／Ctrl-i | 沿跳轉清單往回／往前 |
| Ctrl-k／Ctrl-l | 切到前一個／下一個分頁 |
| F3 | 顯示或收起當前 Quickfix 清單 |
| F5 | 重建並重新連線 cscope |
| F6／F7 | 從工作目錄儲存／載入 `.bookmark` |
| F8 | 開關 Tagbar |

Leader 是反斜線。cscope 查詢按 **Ctrl+反斜線**，放開後再按下列字母。若終端攔截組合鍵，直接輸入右欄的指令。

| 字母 | 指令範例 | 查什麼 |
| --- | --- | --- |
| `s` | `:cs find s demo_rx_poll` | 符號的引用 |
| `g` | `:cs find g demo_rx_poll` | 全域定義 |
| `c` | `:cs find c demo_rx_poll` | cscope 能辨識的呼叫者 |
| `t` | `:cs find t demo_rx_poll` | 文字出現的位置 |
| `e` | `:cs find e demo_rx_.*` | 延伸正規表示式 |
| `f` | `:cs find f demo_driver.h` | 檔案名稱 |
| `i` | `:cs find i demo_driver.h` | 哪些檔案包含這個標頭 |
| `d` | `:cs find d demo_rx_poll` | 這個函式會呼叫誰 |

`:cs f t` 是 `:cs find t` 的簡寫。可用 Ctrl-p 找 `demo_rx.c`，用 `:Tags demo_rx_poll` 找定義，或用 `:Rg demo_rx_poll` 搜同名文字。fzf 結果可用 **Tab** 多選，**Alt-a** 選目前篩選出的全部結果，**Alt-d** 清除選取。這套設定會在按 **Enter** 後把多選結果送進 Quickfix。

## 重走接收路徑的調查

1. 在 `demo-driver` 執行 `make` 和 `make test`。練習預設保留逾時清理錯誤，自測會先失敗。在 Vim 用 Ctrl-p 開 `src/demo_rx.c`，再用 F8 開 Tagbar。切到右側大綱，選 `demo_rx_poll` 並按 Enter。
2. 試 `:cs find c demo_rx_poll`。接著用 `:cs find s demo_rx_poll` 或 `:cs find t demo_rx_poll` 查引用。文字搜尋會找到標頭宣告、實作，以及 `src/demo_probe.c` 的 `.poll = demo_rx_poll`。那行就是 callback 註冊。
3. 按 F3 打開 Quickfix，在 `src/demo_probe.c` 結果上按 Enter。用分頁保留註冊、函式實作與逾時分支。F3 可以來回顯示同一份清單。再次查詢或列出書籤可能會換掉目前清單。
4. 執行 `:cs find d demo_rx_poll`，沿正常路徑從 `demo_clean_rx_irq` 追到 `src/demo_dma.c` 的 `demo_release_rx_buffer`。對照 `demo_refill_rx_ring` 的配置回滾和 `src/demo_rx.c` 的逾時分支。
5. 在練習專案的逾時清理區塊加上這行，放在程式將 descriptor 標為可回收之前。把同樣做法用到實際驅動前，先核對 buffer 歸屬、DMA map 與 unmap 配對、方向、長度、裝置和狀態。

   ```c
   demo_release_rx_buffer(adapter, desc);
   ```

6. 儲存，執行 `make test`，確認輸出 `PASS timeout cleanup released DMA buffer and descriptor`。若專案已納入 Git，可用 `git diff -- src/demo_rx.c` 核對修改。練習的 `make reset` 可還原預設的錯誤。

### 書籤

`mm` 切換本行書籤，`mi` 編輯註記，`mn`／`mp` 前後跳轉，`ma` 把書籤送進 Quickfix，`mc`／`mx` 清除目前檔案／所有書籤。用 F6 儲存前先核對工作目錄，之後回到相同目錄按 F7 載入。

## 看出查詢提供了哪種證據

Tagbar 提供檔案的大綱。cscope 顯示索引裡有的定義與引用。Callback 指派提供註冊位置。要驗證有沒有編進當前映像，還要看組態、Makefile 和建置產物。要驗證實際執行時有沒有走到，就用自測、log、trace 或 debugger。這份練習的自測會呼叫已註冊的 callback，確認逾時後 DMA buffer 和 descriptor 都已釋放。

Vim 找不到映射時，可執行 `:verbose nmap <F5>` 查看哪個檔案設了鍵位，並用 `:scriptnames` 核對插件是否載入。若 `:Files` 或 `:Rg` 失敗，查 fzf 和 rg 是否可執行，以及目前在哪個目錄。若 Tagbar 或索引結果空白，先查 `:set filetype?`、ctags 版本、`:cs show` 和 `cscope.files`。完整診斷指令也收錄在 [英文手冊](usage.md#verify-and-adapt-the-configuration)。
