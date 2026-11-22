# 日常 CLI 小工具

[English](README.en.md)

這份範例有四個可獨立執行的小工具，涵蓋文字替換、查回 DUT 的 IP、等待就緒和保存 log。測試流程中的裝置狀態與自測結果由本機腳本模擬，IP 範例取自隔離區網的 ARP 回應。需要 Linux、Bash、Python 3.9 以上、GNU coreutils 及 awk。

在本目錄執行下列指令，驗證文字替換、兩份 ARP 結果、等待的各種狀態、原始 log 和失敗摘要。驗證會在暫存目錄工作。

```bash
python3 verify.py
```

## 先用便宜的模型試做

寫這類小工具，先講清楚輸入、預期輸出和出錯時該怎麼做。用手上便宜的模型先寫一版，再用同一組成功與失敗的範例驗證。GPT-6.1 Terra、Claude Haiku、Gemini Flash、DeepSeek 和 MiniMax 都可以拿來試。通過測試就留下腳本，把高階模型的額度留給難查的問題。

想在終端裡做，可以用 OpenCode CLI。偶爾寫幾支腳本，先試有每日請求額度的免費模型。用量大一點，再看 OpenCode Go。影片錄製時的月費為 10 美元，DeepSeek V4.1 Flash 的可用量以當時方案與實際請求為準。 [OpenCode CLI 官方文件](https://opencode.ai/docs/) · [免費模型與 Go 方案](https://opencode.ai/console/go)

把小工具放在獨立的測試目錄，並限制 Agent 的檔案存取範圍。只帶入需求、預期結果和測試用假資料，例如這份教材的 `sample/session.log`。公司的原始碼、真實 log 和金鑰留在原本的環境。 [可複製的需求提示](prompts.md)

## 用 MAC 找回 DUT 的 IP

在本目錄執行以下指令。兩份檔案是同一台虛擬 DUT 改 IP 前後的 ARP 回應，包含 IPv4 與 MAC。`--from` 可以直接重跑這個例子。

```bash
mac=02:00:00:00:08:42
bin/dut-ip --from sample/arp-before.tsv "$mac"
bin/dut-ip --from sample/arp-after.tsv "$mac"
```

兩次依序印出 `192.0.2.42` 和 `192.0.2.57`。匹配用完整 MAC，可用大寫或小寫。有多個對應 IPv4 時會各列一行。成功回傳 `0`，沒找到回傳 `1`，指令或資料讀取出錯回傳 `2`。

現場查詢用 `bin/dut-ip --interface lab0 "$mac"`。把 `lab0` 換成接到 DUT 區網的網卡名稱，把 `mac` 換成先前記的位址。這個模式呼叫本機的 `arp-scan`，需要它具備送 ARP 封包的權限。ARP 查詢限同一個二層區網。跨路由時可從 DUT 所在網段查，或在 DHCP 伺服器上按 MAC 找租約。 [arp-scan 官方手冊](https://github.com/royhills/arp-scan/blob/master/arp-scan.1.dist)

## 把測試用的三個工具跑一次

先把範例複製到暫存目錄，避免修改教材中的原檔。以下指令可以在同一個 Bash 順序執行。

```bash
work=$(mktemp -d)
cp -r bin sample "$work/"
cd "$work"
cp sample/test-profile.conf 'test profile.conf'
cp sample/smoke-profile.conf 'smoke profile.conf'

bin/replace-text 'test profile.conf' './logs/staging' './logs/run-01'
bin/replace-text 'smoke profile.conf' './logs/smoke' './logs/run-02'
```

兩次都會印出第 2 行的新內容。引號讓有空白的檔名保持為同一個引數。工具依字面比對，保留原本的換行格式。替換前先在可丟棄的副本驗證。

```bash
bin/wait-ready --every 1 --timeout 5 -- sample/query-ready delayed ready.state
bin/wait-ready --timeout 2 -- sample/query-ready never
echo "$?"
bin/wait-ready --timeout 5 -- sample/query-ready error
echo "$?"
bin/wait-ready --timeout 2 -- sample/query-ready hanging
echo "$?"
```

第一條會印兩次 `WAITING` 和一次 `READY`。逾時與卡住的例子回傳 `124`，查詢出錯回傳 `2`。再測第一次的等待流程前，使用新的狀態檔名。把自己的查詢程式放進雙減號後面時，讓它以 `0` 表示就緒、`1` 表示未就緒，其餘狀態表示查詢出錯。

```bash
first=$(bin/snap-log --out logs sample/session.log)
printf '%s\n' "$first"
cat "$first/failures.tsv"
sed -n '2p' "$first/raw.log"
bin/snap-log --out logs sample/session.log
cmp sample/session.log "$first/raw.log" && echo 'RAW MATCH'
```

失敗摘要會列出原始第 2 行的事件。兩次會建立不同的子目錄。`RAW MATCH` 代表保存的原始檔與輸入逐位元組相同。範例依行首的 `DUT SELFTEST FAIL:` 產生摘要。

## 接成一輪測試

```bash
out=$(sed -n 's/^capture_dir=//p' 'test profile.conf')
for scenario in pass fail timeout query-error; do
    sample/run-round "$scenario" "$out"
    printf 'exit=%s\n' "$?"
done
```

| 情境 | 退出碼 | 原始 log | 摘要 |
| --- | ---: | --- | --- |
| pass | 0 | READY 後有自測 PASS | 表頭 |
| fail | 1 | READY 後有自測 FAIL | 一筆失敗，原始第 4 行 |
| timeout | 124 | TIMEOUT 後跳過測試 | 表頭 |
| query-error | 2 | QUERY_ERROR 後跳過測試 | 表頭 |

每輪會印出自己的 `Saved:` 路徑，目錄內有 `raw.log` 和 `failures.tsv`。

## 放到個人的 PATH

如果希望從其他工作目錄直接叫這些指令，先用 `command -v` 檢查是否已有同名工具，再把需要的工具複製到 `~/.local/bin`。用 `cp -i` 避免直接覆寫同名檔案。

```bash
mkdir -p "$HOME/.local/bin"
cp -i bin/replace-text bin/dut-ip bin/wait-ready bin/snap-log "$HOME/.local/bin/"
export PATH="$HOME/.local/bin:$PATH"
cd sample
command -v wait-ready
wait-ready --timeout 5 -- ./query-ready delayed ../installed-probe.state
```

`export` 只影響當前 shell 及其子程序。確認運作後，可依自己使用的 shell 加入啟動設定。常用旗標可以先用 alias 保存。需要接不同參數或由別的測試呼叫時，可以留成獨立工具，並提供 `--help`。

[給 AI 的需求提示](prompts.md)
