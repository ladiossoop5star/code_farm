# 用 git bisect 找出 completion ring 的回歸

[English](README.en.md)

使用 Git、Python 3、POSIX shell 及 C 編譯器，在開發主機重建兩份獨立的練習 repo。C 模型固定提供 8 個槽位，滿佇列應回報 8 筆待處理。v06 將計數遮罩從 4 位元改成 3 位元，滿佇列的結果因此變成 0。

從此目錄執行以下命令。兩個 repo 都放在新暫存目錄，外部測試腳本從同一份來源讀取。

```sh
fixture_dir=$(pwd)
lab_dir=$(mktemp -d)
python3 prepare.py "$lab_dir/ring-clean"
python3 prepare.py --broken-build "$lab_dir/ring-skip"
cd "$lab_dir/ring-clean"
```

## 核對兩端，手動標記

```sh
git switch --detach demo-good
sh "$fixture_dir/check-ring.sh"
git switch --detach demo-bad
sh "$fixture_dir/check-ring.sh"
git switch main
git bisect start demo-bad demo-good
```

每輪先跑 `sh "$fixture_dir/check-ring.sh"`，再依照結果標記。線性練習歷史上的順序如下。

| 提交 | 滿佇列結果 | 標記 |
| --- | ---: | --- |
| v08 | 0 | `git bisect bad` |
| v04 | 8 | `git bisect good` |
| v06 | 0 | `git bisect bad` |
| v05 | 8 | `git bisect good` |

Git 回報 v06 是第一筆壞提交。先保存操作紀錄，再回到起點。

```sh
git bisect log > "$lab_dir/ring-manual.log"
git bisect reset
```

## 自動查找

```sh
git bisect start demo-bad demo-good
git bisect run sh "$fixture_dir/check-ring.sh"
git bisect log > "$lab_dir/ring-auto.log"
git bisect reset
```

腳本以 0 表示通過，1 表示確認重現指定回歸，125 表示此版本無法編譯，128 表示環境或其他測項出現問題，需要中止檢查。先用已知兩端核對建置及腳本行為，再開始自動查找。 [Git bisect run 的結束碼規則](https://git-scm.com/docs/git-bisect#_bisect_run)

## 跳過無法編譯的版本

```sh
cd "$lab_dir/ring-skip"
git bisect start demo-bad demo-good
git bisect run sh "$fixture_dir/check-ring.sh"
git bisect log > "$lab_dir/ring-skip.log"
git bisect reset
```

v05 無法編譯，Git 回報 v05 和 v06 都是候選。可用 `git show` 對照提交，並將跳過原因與候選清單一起保留。需要確定第一筆壞提交時，先補足舊版本的建置環境，才能用同一支測試驗證 v05。

## 核對第一筆壞提交

```sh
cd "$lab_dir/ring-clean"
git switch --detach 'demo-v06^'
sh "$fixture_dir/check-ring.sh"
git switch --detach demo-v06
sh "$fixture_dir/check-ring.sh"
git show demo-v06 -- ring.c
git switch main
```

父提交回報 8，v06 回報 0。用 `git show` 查看同一次提交裡把計數遮罩減到三位元的修改。

在一個新的練習 worktree 放回上一版的遮罩，再跑同一支測試。

```sh
git worktree add --detach "$lab_dir/ring-fix" demo-v06
git -C "$lab_dir/ring-fix" restore --source='demo-v06^' -- ring.c
(cd "$lab_dir/ring-fix" && sh "$fixture_dir/check-ring.sh")
```

滿佇列重新回報 8。這輪證明的是模型裡同一組輸入的行為，實際硬體的計數器與取樣方式依裝置規格確認。
