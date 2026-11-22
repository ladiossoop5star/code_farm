# Git worktree 與 reflog 練習

[English](README.en.md)

從一個改到一半的 firmware 工作目錄開出舊版 hotfix，重現 BUSY 逾時卻回報 READY 的錯誤。修補提交後，讓 hotfix 分支誤指舊版，再用該分支自己的 reflog 找回修補。

需要有 Git、Python 3.11 以上、GNU Make 和 C 編譯器。手動步驟使用 Bash 和 GNU sed。範例使用本機 C 程式模擬裝置狀態。

## 一次重跑並驗證

在教材目錄執行下列命令。它會自行建立臨時 Git repo，跑完後清除這次建立的練習目錄。

```sh
python3 verify.py
```

輸出會列出舊版的 `FAIL`、修補後的 `PASS` 與救援後的 `PASS`。也會核對切回 hotfix 時已經回到舊版、修補從 `git log --all` 消失、reflog 找回同一筆提交，以及清理後主工作目錄的 diff 和執行檔都保留。

## 跟著影片操作

從教材目錄開始，以下各段在同一個 Bash 工作階段執行。練習中的強制移動與移除都作用在這裡新建的示範目錄。

### 1. 保留原本的改動，開出舊版 worktree

```sh
lab_dir=$(mktemp -d)
python3 verify.py --prepare "$lab_dir"
cd "$lab_dir/firmware"

git status --short --branch
git diff -- wait.c
ls -l out/selftest
git worktree add -b hotfix/ready-timeout ../firmware-hotfix release/1.x
git worktree list
```

原目錄是 `feature/probe-log`，其中一行未提交的修改用來印出 probe log。舊版 hotfix 從 `release/1.x` 開始。

### 2. 重現、修補、提交

```sh
cd ../firmware-hotfix
if make test; then
    echo "Expected the old version to fail" >&2
    exit 1
fi
sed -i '/^    return READY;$/s/READY/TIMEOUT/' wait.c
git diff -- wait.c
make test
ls -l out/selftest ../firmware/out/selftest
git add wait.c
git commit -m "Return TIMEOUT when DUT stays BUSY"
git log -1 --oneline
```

第一輪印出 `FAIL: DUT stayed BUSY but wait_ready returned READY`。改掉迴圈耗盡時的回傳值後，同一組測試印出 `PASS: READY after polling, TIMEOUT when BUSY`。兩份 `out/selftest` 各自留在所屬目錄。

### 3. 讓 hotfix 分支誤指舊版

先暫時離開 hotfix，Git 才能移動該分支。這次只移動臨時 repo 的 `hotfix/ready-timeout`。

```sh
git switch --detach release/1.x
git branch -f hotfix/ready-timeout release/1.x
git branch -v
git switch hotfix/ready-timeout
git log -1 --oneline
git log --all --oneline
```

`git branch -v` 仍列出 hotfix，但它現在指向 `Add firmware READY self-test`。從 hotfix 的歷史與 `git log --all` 都找不到 `Return TIMEOUT when DUT stays BUSY`。

### 4. 找回提交，再做一次測試

```sh
git reflog show -2 hotfix/ready-timeout
git show 'hotfix/ready-timeout@{1}' -- wait.c
git switch -c rescue/ready-timeout 'hotfix/ready-timeout@{1}'
git log -1 --oneline
make -B test
```

`@{1}` 是這次練習中分支移動前的位置。先用 `git show` 核對提交訊息與 diff，找到從 `READY` 改成 `TIMEOUT` 的那一行。救援分支建立後，普通的 `git log` 再次看得到修補，重新編譯後的測試也通過。

### 5. 收掉 hotfix 工作目錄

```sh
printf 'make test: PASS\n' > run-note.txt
git status --short --branch
cd ../firmware
if git worktree remove ../firmware-hotfix; then
    echo "Expected Git to refuse the untracked file" >&2
    exit 1
fi
git worktree remove --force ../firmware-hotfix
git worktree list
git show rescue/ready-timeout -- wait.c
git status --short --branch
git diff -- wait.c
ls -l out/selftest
```

第一次移除時，Git 會因為 `run-note.txt` 還在而拒絕。範例裡這份記錄和 hotfix 建置產物都可丟棄，因此直接加 `--force`。最後清單只剩主工作目錄。救援分支仍有修補，主工作目錄也仍有原本的改動和編譯產物。
