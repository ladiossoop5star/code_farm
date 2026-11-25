# Episode 20 | Adversarial code review with Git diff

Adversarial review is an independent static review of one commit's diff. Try to find a condition the requirements allow where the new code would behave incorrectly. Read surrounding source when it is needed to establish the changed behavior's contract or reachability.

## Review a commit

1. Give an independent reviewer the commit ID, requirements, intended change, and behavior callers still depend on. Have the reviewer form a judgment before sharing the implementer's reasoning.
2. Read the exact change. Replace `HEAD` with the target commit ID to review a different commit.

   ```sh
   review_commit=$(git rev-parse --verify HEAD)
   git show --no-ext-diff --no-textconv --format=fuller --patch "$review_commit"
   ```

3. Trace the code from a changed line through a reachable condition to a concrete effect. Record the scope, paths checked, findings, and open questions.

Use the prompt below or give the [adversarial review Skill](adversarial-review/SKILL.md) to an agent that can read the diff and relevant source.

> Perform an independent static review of this commit's diff. Find a case allowed by the requirements where changed code would violate expected behavior. Read nearby source only to establish the contract or trace a relevant path. List the paths you checked. For each finding, give the file and line, trigger, code path, and impact. Record unresolved questions with the details needed to settle them.

The video opens an independent reviewer in Herdr and hands it the Skill, requirements, and full commit diff. The Skill gives eight questions to check against the patch. Record the result of each check, including areas that do not apply.

## Short exercise

Read the [interface requirements](example/REQUIREMENTS.md) and the [candidate diff](example/candidate.diff). Consult the [changed code](example/sensor-power.c) and the [hardware model](example/hw-model.c) as needed. Trace what state a failed power-on leaves behind.

<details>
<summary>Example review finding</summary>

**Request changes.** At [sensor-power.c, line 13](example/sensor-power.c#L13), the new `return restore_config(sensor);` can return a configuration timeout after the supply and clock were enabled. That path skips both cleanup operations, leaving two enable references outstanding when the caller receives an error. Preserve the configuration error and release the clock before the supply.

</details>

[繁體中文](README.md)
