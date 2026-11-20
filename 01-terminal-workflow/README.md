# 第 01 集｜終端機開發工作台速查

[English](README.en.md)

把編輯、編譯和測試放在固定開發主機上。操作端透過 SSH 接回主機。DUT 是實際執行韌體或驅動的受測裝置，依環境以 UART、GDB 或網路連到開發主機。

| 要做的事 | 放在哪裡 | 常用工具 |
| --- | --- | --- |
| 登入、切換電腦 | 操作端 | SSH、順手的終端機 |
| 保留編輯、建置與測試畫面 | 開發主機 | Herdr 或 tmux |
| 查大型 C 專案 | 開發主機 | Vim、cscope、ripgrep |
| 編譯、準備測試與保存 log | 開發主機 | GCC／Clang、make、Shell |
| 驗證驅動或韌體 | DUT | UART console、實際功能測試 |

## 選操作端

| 平台 | 可用的終端機 |
| --- | --- |
| Windows | Windows Terminal 搭配 PowerShell 或 WSL |
| Linux 桌面 | GNOME Terminal、Ghostty 或 Alacritty |
| macOS | 系統終端機或 iTerm2 |
| Android | Termux |

優先確認鍵盤操作、字型、捲動和 SSH 都合用。遠端主機上的編譯器、索引和測試工具可以由不同操作端共用。

## 檢查 SSH 設定

[ssh-config.example](ssh-config.example) 使用範例網域及帳號。先在本目錄執行這個指令，確認 OpenSSH 能解析設定。

```sh
ssh -F ssh-config.example -G dev-server | sed -n '/^hostname /p; /^user /p; /^serveralive/p'
```

應看到 `dev.example.com`、`developer`、心跳間隔 30 秒和上限 3 次。這個指令只顯示設定。把範例網域、帳號和金鑰路徑換成自己的值，再合併到 `~/.ssh/config`。

## 練習從另一個終端接回工作台

1. 連到自己的開發主機，在 Herdr 或 tmux 內開啟編輯器，另開一個 pane 執行 `sleep 120`。
2. 從操作端中斷連線，再用另一個終端登入同一台主機並接回會話。
3. 檢查編輯器和測試 pane 是否還在。會話可保留 SSH 斷線時仍在主機執行的程序。請另外保存重要工作和 log，主機重開機會終止原本的程序。

[OpenSSH 用戶端設定手冊](https://man.openbsd.org/ssh_config)
