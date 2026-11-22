# AI Agent Self Workflow

```mermaid
flowchart LR
    INPUT["Input<br/>Problem Description"] --> TEST{"Test"}
    TEST -->|Initial PASS or post-re-review PASS| DONE["Done<br/>Problem Resolved"]
    TEST -->|Retest PASS · Review pending| REVIEW{"Adversarial Review"}
    TEST -->|FAIL · Retest debug trace| ANALYZE["Analyze Problem"]
    ANALYZE --> COMPILE["Compile"]
    COMPILE --> TEST
    REVIEW -->|PASS| DONE
    REVIEW -->|FAIL| FIX["Fix"]
    FIX --> RECHECK{"Re-review"}
    RECHECK -->|FAIL| FIX
    RECHECK -->|PASS · Retest same revision| TEST
```

Use the same Test node for each run. When Re-review passes, retest that exact revision. A PASS goes directly to Done. A FAIL returns to Analyze Problem. Any subsequent code change needs test and review evidence for the new revision.
