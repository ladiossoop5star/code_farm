# 第 17 集｜Edward：用 1 條命令讓AI跑完多機測試

[English](README.en.md)

先寫能重現問題、取得本輪證據的最短測試。對這個測試台來說，接收端開 iperf 後等 2 秒就夠。Edward 把每個 block 的原始輸出即時印到終端，另存成 1 份暫存 report。AI 判讀完就刪掉。

## 準備 2 台測試機

在 Host 的 `~/.ssh/config` 設定 [`receiver` 和 `sender`](ssh-config.example)，填入各自的 SSH 位址和帳號。確認主機指紋，並設好金鑰登入。

```sh
ssh receiver hostname
ssh sender hostname
```

如果 SSH 還提示輸入帳號密碼，先完成金鑰設定。等 2 台都能直接回傳主機名稱，再跑 Edward。

兩端用 Linux、Bash 和 iperf 2.x。發送端另需要 `ping`。Host 用 Bash、GNU coreutils、OpenSSH client 和 Python 3.11 以上。把 2 份 TOML 裡的 `192.0.2.10` 換成發送端能連到的接收端測試 IP。這個練習以接收端作為 DUT，用 iperf 的預設 TCP port 5001。

## 先跑簡單版

```sh
./edward iperf-pass.toml
```

| Block | 機器 | 操作 |
| --- | --- | --- |
| 1 | `receiver` | 開 iperf server，輸出寫到 `/tmp/iperf-server.log`，接著 `sleep 2` |
| 2 | `sender` | 送 3 秒流量，再用 `ping` 探測 DUT |
| 3 | `receiver` | 用 `cat` 取回接收端輸出，讀取成功就刪掉遠端暫存檔 |

每段的 `commands` 整段交給該機器上的 Bash。換 block 就開新的 shell。寫 `machine = "local"` 時就直接在 Host 執行。前一段命令出錯也繼續收集後續輸出，讓 AI 看得到失敗的原因。

同一個測試台一次跑 1 輪。接收端 server 以 `-t 8` 限時運行，等它結束後再重跑。要看失敗對照，執行 `./edward iperf-fail.toml`，發送端會改成送 128 KiB。

## 交給 AI 跑

> 執行 `./edward iperf-pass.toml`。讀取終端最後印出的 Report 檔，按裡面的驗收條件判 PASS 或 FAIL。量測引用第 3 個 block 的接收端輸出，DUT 探測看第 2 個 block。判讀完就刪掉那份 report。

正式計畫要在接收端看到 3 個完整且有流量的 1 秒區間，且送完後 DUT 有回應 ping。失敗對照的 DUT 也能回應，但量測不足 3 秒。兩次用相同條件判讀。

## 進階參考

等 2 秒仍不夠穩、需要為遠端命令設逾時，或需要把每個 block 的輸出分開取證時，可參考[進階計畫](advanced/iperf-pass.toml)與[進階執行器](advanced/edward)。把進階計畫的測試 IP 換成自己的位址，在本教材目錄執行 `./advanced/edward advanced/iperf-pass.toml`。Host 另需要 `setsid`（util-linux）。
