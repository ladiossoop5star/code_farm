# 重播查找紀錄

[English](replay.en.md)

依[練習步驟](README.md)在 `ring-clean` 完成手動查找，保存 `ring-manual.log`，再回到 `main`。在同一份 Git 歷史執行以下指令。

```sh
git bisect replay "$lab_dir/ring-manual.log"
git bisect log
git bisect reset
```

重播會再次回報 v06 是第一筆壞提交。要重新驗證行為，可用練習中的外部測試腳本重跑。交接時將好壞提交、測試條件、操作紀錄與測試輸出一起附上。 [Git bisect log 與 replay](https://git-scm.com/docs/git-bisect#_bisect_log_and_bisect_replay)
