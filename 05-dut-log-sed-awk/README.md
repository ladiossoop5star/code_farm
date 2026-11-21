# 用 sed 和 awk 整理 DUT 測試 log

[English](README.en.md)

用影片中的 QEMU 電源鍵自測紀錄練習選行、替換、取欄位與分組計數。每輪都有自己的原始 console log。整理後的明細保留來源路徑，遇到意外結果時可以直接回查。

在本目錄內操作。範例使用 `sh`、GNU `sed`、`awk` 與 `diff`，直接讀取提供的 log。

## 先拿一份 log 試

```sh
sed -n '3p' raw/before/01.log
sed -n 's/^DT status=/status=/p' raw/before/01.log
sed -n 's/^DT status=/status=/p' raw/before/01.log | awk -F= '{print $2}'
```

終端依序顯示 `DT status=disabled`、`status=disabled`、`disabled`。最後一行的 `-F=` 指定用等號分欄，`$2` 取第二欄。原始 log 保留錄製時的 CRLF，批次用的 `normalize.sed` 會先移除行尾的回車。

## 整理兩批測試

`runs.tsv` 每列記錄一次啟動，兩欄分別為批次與原始 log 路徑。`build-ledger.sh` 逐份用 `normalize.sed` 整理自測結果，輸出批次、狀態、原始路徑。`summarize.awk` 再按批次及狀態計數。

```sh
sh build-ledger.sh runs.tsv > ledger.tsv &&
awk -f summarize.awk ledger.tsv > summary.tsv &&
diff -u expected/ledger.tsv ledger.tsv &&
diff -u expected/summary.tsv summary.tsv
```

兩個 `diff` 都沒有輸出，表示與預期相符。

| 批次 | 總輪數 | PASS | NO_DEVICE | NO_EVENT | NO_RESULT | REVIEW |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| before | 3 | 0 | 3 | 0 | 0 | 0 |
| after | 3 | 2 | 0 | 1 | 0 | 0 |

- `PASS` 表示收到了模擬電源鍵。
- `NO_DEVICE` 表示找不到輸入裝置。
- `NO_EVENT` 表示已進入等待階段，最後沒有收到電源鍵。
- `NO_RESULT` 表示本輪的 log 沒有自測結果列。
- `REVIEW` 表示自測結果格式未知，或同一輪出現多筆結果。

從明細找到變更後那筆 `NO_EVENT` 的來源，再核對原始內容。

```sh
awk -F '\t' '$1 == "after" && $2 == "NO_EVENT" {print $3}' ledger.tsv
grep -En '^DUT (READY|SELFTEST)' raw/after/02.log
```

## 加入擷取中斷的那輪

[`raw/after/04.log`](raw/after/04.log) 在印出 `DUT READY: waiting for KEY_POWER` 時中斷擷取。測試清單仍記得有這一輪，摘要會把它列為 `NO_RESULT`。

```sh
sh build-ledger.sh runs-with-interruption.tsv > ledger-with-interruption.tsv &&
awk -f summarize.awk ledger-with-interruption.tsv > summary-with-interruption.tsv &&
diff -u expected/ledger-with-interruption.tsv ledger-with-interruption.tsv &&
diff -u expected/summary-with-interruption.tsv summary-with-interruption.tsv
```

`before` 維持三輪。`after` 的總輪數變成四，分別是兩輪 `PASS`、一輪 `NO_EVENT`、一輪 `NO_RESULT`。四輪都能從明細回到原始 log。
