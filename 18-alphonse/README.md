# 第 18 集｜Alphonse 多窗格測試

Alphonse 是一份給 AI Agent 的操作說明。Agent 讀 1 份 TOML，依固定規則開 Herdr 窗格，再依序送命令，讀本輪輸出後判 PASS 或 FAIL。 [窗格規則](skills/alphonse/SKILL.md#fixed-pane-layout)

## 準備

1. 準備 2 個 Linux 測試端點。接收端同時是 DUT，兩端都裝 iperf 2，發送端還需要 `ping`。讓發送端可以連到接收端的測試 IP。
2. 用 [SSH 設定範例](ssh-config.example) 配置主控機。將 `HostName` 和 `User` 改成測試環境的值。`receiver` 和 `dut-console` 是同一台裝置的不同登入。設好金鑰，核對主機指紋，再分別以 `ssh receiver`、`ssh sender`、`ssh dut-console` 確認能進入 Bash，無須輸入遠端登入密碼。TOML 命令中的 `192.0.2.10` 是示例測試 IP，請換成實際的接收端位址。它可以和 SSH 位址不同，只要 DUT 綁得上、發送端能到達。
3. 主控機需要 Python 3.11 以上，供窗格配置工具讀取 TOML。在 Herdr 開啟 Agent，載入 [Alphonse Skill](skills/alphonse/SKILL.md)。例如在此教材目錄內啟動 `pi --skill ./skills/alphonse/SKILL.md`。確認 Agent 可讀檔及執行 shell 命令。

## 跑一次

> 請用 Alphonse 跑一次 iperf-pass.toml，依 pass_criteria 判定，並引用本輪接收端、發送端與 console 的輸出。

- 接收端以前景執行 server。這格印出 `Server listening` 時，Agent 繼續操作發送端。
- 發送端跑 3 秒 iperf，結束後 ping DUT。另一格跑 `uname -r`，確認傳輸後還能從 DUT 的 console 取得輸出。
- 收集本輪輸出後，用 Ctrl+C 停掉這輪開的 server。只留修正迴圈需要的判定與證據。想留窗格供人查看可以在提示詞寫清楚。
- 將提示詞的檔名換成 [iperf-fail.toml](iperf-fail.toml) 再跑一輪。這份只發送 128 KiB。即使 ping 和 console 都有回應，接收端缺少 3 個完整的正吞吐量區間仍是 FAIL。

`ready` 用於要留在前景的單一程序。普通 block 等 shell 完成該做的動作，再移到下一個 block。跑自家測試時，用同樣方式替換機器與命令，有需要可以呼叫已備好的小腳本。時間敏感的啟動與取樣，可交給同一支腳本控制。
