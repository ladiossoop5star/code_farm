# 15｜讓 AI 自己把問題修到好，測試才是真正的關鍵

[English](README.en.md) · [自主迭代流程圖](workflow.md)

這個本機案例用 iperf 把流量送過 1 個 TCP 轉送程序。請先寫下這輪的通過條件，再看接收端和程序存活的證據。

需要 Linux、Python 3 和 iperf 2.x（命令為 `iperf`）。在這個目錄執行以下命令。測試只使用 `127.0.0.1`，程序終了後會清理暫存資料。

```sh
python3 relay-demo.py crash
python3 relay-demo.py drop
python3 relay-demo.py drop    # 補強驗收條件後，用同一版再測
python3 relay-demo.py forward
```

| 情境 | 接收端證據 | DUT 證據 | 判定 |
| --- | --- | --- | --- |
| `crash` | 只有第 1 個完整區間 | 刻意注入的程序退出，探測無法連線 | FAIL |
| `drop` | 沒有量測區間 | 程序還能回應，但轉送了 0 bytes | 只查存活可能判 PASS，補強後判 FAIL |
| `forward` | 0–1、1–2、2–3 秒皆有大於 0 的吞吐量 | 完成傳輸且存活探測成功 | PASS |

練習把驗收條件寫成 AI 可以檢查的自然語言。交代在哪一端找證據、完整期間怎麼算、哪些條件要一起成立。再用 `drop` 試試看，只檢查「DUT 沒 crash」會得到什麼答案？
