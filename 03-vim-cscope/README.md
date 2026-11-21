# 第 03 集｜用 Vim 和 cscope 追 C 程式

[English](README.en.md)

重走影片的 Vim、fzf、Tagbar、cscope、Quickfix 和書籤操作。練習用的 C 驅動範例可在本機編譯和測試。

請準備支援 `+cscope`、`+quickfix`、`+terminal` 的終端版 Vim，以及 cscope、Universal Ctags、ripgrep、Git、make 和 C 編譯器。安裝腳本會從上游下載 Gruvbox 與 fzf 的執行檔和 Vim runtime。

把教材放在完整路徑沒有空格的目錄，從本目錄執行。

```sh
sh bootstrap.sh
cd demo-driver
make index
vim -Nu ../.vimrc -i NONE -n
```

這個 Vim 指令載入教材附的設定，並停用 viminfo 和 swap 檔。進入 Vim 後按 **Ctrl-p**，搜尋 `demo_rx`，開啟 `src/demo_rx.c`。

[中文操作手冊](usage.zh-TW.md) 包含鍵位速查和完整的追查練習。[English guide](usage.md) 提供英文版。第三方插件的版本與授權見 [THIRD_PARTY.md](THIRD_PARTY.md)。
