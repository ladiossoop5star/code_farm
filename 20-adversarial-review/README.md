# 第 20 集｜用 Git diff 做對抗性審查

對抗性審查是獨立的靜態程式碼審查。一次審一個 commit，從 diff 出發，找一個需求允許、程式卻會處理錯的情境。周邊程式碼只供確認這次改動的契約、呼叫路徑和觸發條件。

## 審自己的改動

1. 選定要審的 commit，把需求、改動意圖和必須維持的契約交給獨立的 reviewer。實作者的修法理由留到初審回來再對照。
2. 用下列指令讀取要審的改動。若要審的是其他 commit，將第一行的 `HEAD` 換成該 commit 的雜湊。

   ```sh
   review_commit=$(git rev-parse --verify HEAD)
   git show --no-ext-diff --no-textconv --format=fuller --patch "$review_commit"
   ```

3. 從改動的行出發，沿著實際程式路徑檢查預期行為。報告記下範圍、查過的路徑，以及每個發現的觸發條件和影響。

審查提示可以直接用，也可以將 [對抗性審查 Skill](adversarial-review/SKILL.md) 交給能讀取 Git diff 和周邊程式碼的 Agent。

> 請獨立靜態審查這個 commit 的 diff。從需求找出這次改動可能破壞的行為，提出能沿程式碼推到結果的反例。周邊程式碼只用來確認改動的契約和呼叫路徑。請列出已查的路徑。每項缺陷附上檔案行號、觸發條件、程式路徑與影響，證據不足的部分列為問題。

影片用 Herdr 開一個獨立的 reviewer，交給它 Skill、需求和完整的 commit diff。Skill 裡列出八項讀碼問題，回報時每項都記下有沒有檢查到問題，或為什麼不適用。

## 短練習

先讀 [介面需求](example/REQUIREMENTS.md) 和 [候選 diff](example/candidate.diff)。需要時查看 [改動後的程式](example/sensor-power.c) 和 [硬體介面模型](example/hw-model.c)，用靜態閱讀推導一次上電失敗會留下什麼狀態。

<details>
<summary>參考審查發現</summary>

**應退回修正。** 在 [sensor-power.c 第 13 行](example/sensor-power.c#L13)，新的 `return restore_config(sensor);` 會在電源、時脈成功啟用後直接回傳設定逾時錯誤。該路徑少了停用時脈，也跳過下方的電源清理。呼叫端收到失敗時，裝置仍持有兩個啟用引用，違反介面要求。修正方向是保留設定錯誤碼，並先停用時脈、再停用電源。

</details>

[English](README.en.md)
