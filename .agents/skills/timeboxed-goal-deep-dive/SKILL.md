---
name: timeboxed-goal-deep-dive
description: Use when the user creates or requests a Goal with an explicit timebox, Safety window, time budget, or deep-dive instruction, especially for research, market validation, hypothesis testing, item-by-item conclusions, evidence gathering, or reports. Prevents stopping after a shallow first pass; guides Codex to use remaining time on weak points, counterevidence, source expansion, and explicit early-stop justification.
---

# Timeboxed Goal Deep Dive

## Purpose

Use this skill to treat a timeboxed Goal as an iterative deep dive, not as permission to stop after the first plausible answer.

The timebox is a safety ceiling. It is not a target to waste, and it is not an excuse to finish in a few minutes when meaningful unresolved questions remain.

## Trigger Interpretation

If the user says `Goal`, `2h`, `10分`, `Safety`, `時間余ったら`, `深堀`, `探索`, `エビデンス集め`, or asks for item-by-item conclusions under a time budget:

1. Create or acknowledge the Goal.
2. State the assumed timebox and deliverables.
3. Produce an initial answer quickly.
4. Continue deepening weak points until the timebox is no longer useful, the deliverables are genuinely complete, or a blocker appears.

## Required Loop

### 1. Define the work surface

Write the items being explored before researching.

For each item, keep:

- item id
- plain-language question
- current conclusion
- evidence found
- confidence
- next weak point
- kill / proceed impact

### 2. First pass is not completion

The first pass only creates a map.

Do not mark the Goal complete immediately after:

- finding a few sources
- writing a draft table
- producing a partial report
- answering only at the overall-conclusion level

After the first pass, identify the weakest 2-4 cells and deepen those.

### 3. Spend remaining effort on weak points

Prioritize follow-up in this order:

1. Claims that decide Proceed / Kill
2. Claims with Low or Unknown confidence
3. Buyer, budget, or workflow ownership
4. Data access or permission assumptions
5. Existing alternative / competitor coverage
6. Counterevidence that would weaken the thesis
7. Additional source diversity

### 4. Early-stop gate

Only stop early if all are true:

- requested artifacts exist
- each item has an explicit conclusion, confidence, evidence, and next action
- the remaining weak points are named and are either blocked or lower value than stopping
- the final response explains why stopping before the timebox is acceptable

If any of these is false, continue.

### 5. Final report shape

For timeboxed research, include:

```markdown
## Item Conclusions

| Item | Conclusion | Confidence | Evidence | Weak point | Next action |
|---|---|---|---|---|---|

## Deepened Points

...

## What Changed

...

## Still Weak

...

## Stop / Continue Judgment

...
```

## Repo-Specific Rule

For this repository, every business or EPS/ECU conclusion must still follow:

1. Market demand
2. Unresolved pain
3. Hypothesis
4. Solution
5. Buyer / user
6. Initial artifact
7. Validation method
8. Kill criteria

Also preserve the EPS supplier lens:

- what an EPS / SbW supplier can sell
- what it can actually do
- what it must not claim
- what belongs to OEM, fleet, or service platform territory
- which supplier department should see the next result

## Common Failure To Avoid

Do not collapse item-level work into one overall conclusion.

Bad:

> Overall, the theme is worth continuing.

Good:

> Item 1 is partially supported, Item 2 is supported but points to OEM fleet service rather than supplier direct sales, Item 3 is the main Kill gate, Item 4 is supported, and Item 5 is supported but threatened by existing remote diagnostics platforms.

## Good Enough Definition

A timeboxed deep dive is good enough when it leaves the user with a better decision than before:

- which items are supported
- which items are weak
- which exact item should be investigated next
- what would kill the theme
- whether more time is worth spending
