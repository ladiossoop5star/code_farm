---
name: adversarial-review
description: Independently review one Git commit's diff for reachable ways the changed code can violate a requirement or caller contract. Use for static code review with traceable findings, open questions, and a record of paths checked.
---

# Adversarial code review

## Start with the change

Pin one commit. Work from its full patch, the requirement, and the interface promises that still apply. Read the commit message for intent and form a judgment from the source before considering the author's diagnosis. Look for unrelated changes that might otherwise go unnoticed.

Only changed behavior is in scope. Read nearby code at the reviewed revision to establish a relevant caller, contract, or path. Use read-only Git and source inspection. When given an exported patch, read the file and its commit ID. Leave builds, test runs, measurements, and automated analysis to the implementer outside the review.

## Trace a possible counterexample

For each meaningful change, say what must stay true. Find an allowed input, failure, or operation order that could violate it. Start at a changed line, check that the trigger can happen, and follow the actual code until a caller-visible result or state breaks the promise.

Check each question against the diff and record when it does not apply.

1. **Correctness.** Does the computation or branch still produce the required result?
2. **Boundaries.** Which valid inputs are at the limits of the changed behavior?
3. **Failures.** Which operations can fail halfway through, and what state remains?
4. **Ownership and concurrency.** Who holds each resource, and which operations can overlap?
5. **Security.** Does each relevant path respect the same authorization and data boundaries?
6. **Compatibility.** Can existing callers still rely on the interface's defined behavior?
7. **Performance.** Did the change add work to a hot path or lengthen a critical section?
8. **Test code.** Can the changed inputs and assertions distinguish the promised behavior from an incorrect result? Mark this check inapplicable when the patch changes no test code.

## Make the evidence checkable

Report the commit and intended behavior. Give one verdict: **request changes**, **no blocking findings**, or **conditional** with the exact condition the reader needs to resolve. If key context is missing, say what would resolve the question.

For each finding, verify the file and line in the reviewed revision. State the trigger, code path, impact, and a direction for correction when evident. Order by severity, considering both the scenario and its consequence. State confidence based on the source trace. Keep a concern with an unproven trigger as an open question. Record the areas checked even when there are no findings. Keep style-only observations outside the report. For re-review, trace the reported behavior against the replacement commit.
