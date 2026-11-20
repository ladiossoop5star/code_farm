# 第 02 集｜Herdr 工作區與操作速查

[English](README.en.md)

在開發主機依照官方文件安裝 Herdr TUI。用同一個 Space 放一項工作，再用 Tab 區別用途，Pane 放實際程序。 [Herdr TUI 安裝與使用說明](https://herdr.dev/tui/docs/)

| 影片中的工作 | 建議位置 |
| --- | --- |
| 查驅動程式碼、看 diff | Code tab |
| 編譯及留建置輸出 | Build tab |
| 跑自測、看 UART console | Test tab 的兩個 pane |
| 處理插隊的工作 | 另一個 Space |

## 操作練習

1. 執行 `herdr`，從側欄建立名為 `dma-driver-debug` 的 Space。新增 Code、Build、Test 三個 Tab。右鍵可在 Test 拆分 pane，拖曳邊界可調整大小。
2. 在 Build 或 Test 執行 `sleep 120` 當作長任務。切到另一個 Space，再回到同一個 Tab，原來的程序應仍在原位。
3. 從目前終端 detach 或結束 SSH 連線，再登入原主機，以同一帳號重新執行 `herdr` 接回。主機和背景服務必須仍在執行。
4. 有 Agent 時，可從側欄狀態跳進正在等待確認的 pane。狀態依 Agent 的整合支援而異。

預設前綴鍵是 `Ctrl+b`。按前綴再按 `?` 可看當前的鍵位，`c` 新增 Tab，`q` 離開 TUI 並保留背景會話。 [官方鍵盤說明](https://herdr.dev/tui/docs/keyboard/)

## 試用設定

[config.toml.example](config.toml.example) 保留看片時用的滑鼠操作與新 Tab 命名提示。Linux 或 macOS 可先在暫存設定目錄驗證。

```sh
config_root=$(mktemp -d)
mkdir "$config_root/herdr"
cp config.toml.example "$config_root/herdr/config.toml"
XDG_CONFIG_HOME="$config_root" herdr config check
```

本範例以 Herdr 0.8.0 檢查通過。要納入自己的設定，可從 `herdr --help` 確認目前設定檔位置，再合併需要的欄位。 [官方設定參考](https://herdr.dev/tui/docs/configuration/)
