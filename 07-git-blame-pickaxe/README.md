# Git blame 與 pickaxe 練習

[English](README.en.md)

用一段 DMA descriptor 程式追查 4 KiB 拆分的來源，再查清楚為什麼後來只對 Rev A 啟用。練習會建立四筆 Git 提交，依序包含初始實作、跨界拆分、revision 條件和縮排調整。

需要 Git、Python 3、GNU Make 和 C 編譯器。DMA 行為是本機模型，可以在自己的機器上重跑。

## 自動驗證

```sh
python3 prepare.py
```

腳本會在臨時目錄建立 Git 歷史，核對 blame、pickaxe、完整補丁與三個測試案例，再印出拆分、能力條件及縮排提交的短 hash。

## 建立一份可自己查閱的 Git 歷史

以下命令從教材目錄開始，在同一個 shell 依序執行。每次建立的提交 hash 可能和影片不同。

```sh
lab_dir=$(mktemp -d)
python3 prepare.py "$lab_dir/dma-demo"
cd "$lab_dir/dma-demo"
git log --oneline
```

## 用 blame 找到改過該行的提交

```sh
git blame -L '/if (crosses_4k(addr, len)/,+2' -- dma_submit.c
git blame -w -L '/if (crosses_4k(addr, len)/,+2' -- dma_submit.c
```

第一個查詢讓 if 那行指到縮排提交。加上 `-w` 後，該行會指到加入 `caps->split_at_4k` 的提交。

## 比對兩種 pickaxe 查詢

```sh
git log --oneline -S'crosses_4k(addr, len)' -- dma_submit.c
git log --oneline -G'crosses_4k\(addr, len\)' -- dma_submit.c
```

`-S` 查指定字串的出現次數是否改變，因此只找到第一次加入拆分的提交。`-G` 查新增或刪除行是否匹配正規表示式，這裡會找到拆分、能力條件與縮排三筆提交。

## 看完整補丁並重跑三個測試

```sh
split=$(git log -1 --format=%H -S'crosses_4k(addr, len)' -- dma_submit.c)
gate=$(git blame -w --porcelain -L '/if (crosses_4k(addr, len)/,+1' -- dma_submit.c | sed -n '1s/ .*//p')
git show "$split" -- dma_submit.c
git show "$gate"
make test
cat design-notes.md
```

完整能力補丁包含 `dma_caps.c`、`dma_submit.c` 和 `selftest.c`。在 DMA 位址 `0x1ff0` 下會看到三種結果。

| 裝置與長度 | 預期 descriptor |
| --- | --- |
| Rev A，32 bytes | 兩筆，各 16 bytes |
| Rev B，32 bytes | 一筆，32 bytes |
| Rev A，16 bytes | 一筆，16 bytes |

產生的 `design-notes.md` 是此案例的筆記示例。用教材裡的 [筆記範本](design-notes-template.md) 整理自己的案例時，可以把每個判斷連回補丁、版本條件和重跑結果。
