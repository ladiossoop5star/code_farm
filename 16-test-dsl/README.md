# 第 16 集｜Test DSL

[English](README.en.md)

一個 block 表示在同一台機器上連續做的一段操作。用 `machine` 寫設備名稱，把平常在終端下的命令逐行放進 `commands`。換機器才開新 block。要讓服務到背景繼續跑，在 shell 命令尾端加 `&`，再依本輪的 log 確認它已就緒。

| 範例 | block 順序 |
| --- | --- |
| [直接送流量](two-blocks.toml) | 接收端開 server 並等監聽 → 發送端送 3 秒流量 |
| [經 DUT 轉送](relay.toml) | 接收端等待監聽 → DUT 等待轉送就緒 → 發送端送流量並探測 DUT |

`machine` 指的是執行命令的機器。本機直接執行，遠端先用 SSH 連上再執行。遠端位址、帳號和跳板可以放在 SSH 別名設定裡。需要操作 UART 或 USB 時，由接著裝置的那台機器執行對應的命令或腳本。例如 UART 接在本機，就在本機跑 `tm_set_cmd`。接在遠端，就 SSH 到那台機器跑同一個工具。

測試計畫記錄操作順序和本輪驗收條件。本集用範例解釋語法，後續各集才接上 Edward 和 Alphonse。

## 手動對照範例

這 2 份範例都在同一台電腦上練習，用不同終端扮演各個角色。準備 Linux、Bash、iperf 2.x 與 GNU `stdbuf`，並把第 08 集的 `wait-ready` 放到 `PATH`。每輪用 `mktemp -d` 建立目錄，讓參與的終端都將 `TEST_ROUND` 指到同一路徑。按文件順序在對應的終端執行 `commands`，上一段等到就緒才切到下一段。

直接流量範例在本機用 loopback 測試，預設 port 為 `55106`。若已被使用，在接收與發送端都設定同一個未使用的 `IPERF_PORT`。轉送範例以第 15 集的 `relay.py` 作為 DUT 模擬程序。各終端在 Python 檔所在目錄操作，並把 `TEST_VARIANT` 一起設為 `forward`、`drop` 或 `crash`。用接收端量測與 DUT 的探測結果讀回 `pass_criteria`。取證後，回到啟動服務的終端，結束本輪的背景程序。

[第 08 集 wait-ready](https://github.com/ladiossoop5star/code_farm/blob/main/08-ai-cli-tools/bin/wait-ready) · [第 15 集 relay.py](https://github.com/ladiossoop5star/code_farm/blob/main/15-ai-test-loop/relay.py)
