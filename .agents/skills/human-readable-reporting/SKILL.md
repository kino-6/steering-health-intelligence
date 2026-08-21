---
name: human-readable-reporting
description: Use this skill when Codex writes, rewrites, or reviews human-facing reports, strategy memos, business-model conclusions, market research summaries, EPS/ECU hypothesis documents, README guidance, or generated HTML/TSV report companions. Trigger it when the user asks for a report, conclusion, explanation, "自然言語で", "人間向け", "読めるように", "分かりやすく", "造語が多い", "単語だけで分からない", or when a draft uses labels such as P0/P1, Coverage Benchmark, Evidence Pack, Readiness, screening, RCA/8D, VHM, or other project-specific terms before explaining the underlying decision in plain language.
---

# Human Readable Reporting

## Purpose

Make repo reports understandable to a human reader before introducing project jargon.

Use this skill whenever a document is meant to persuade, explain a conclusion, summarize research, or decide Proceed / Hold / Kill. It is especially important for EPS / ECU business-model exploration, where technical labels can hide weak reasoning.

## Core Rule

Do not lead with coined names, phase labels, acronyms, product names, or internal shorthand.

First explain in natural language:

1. What decision is being made
2. Whose work or budget is affected
3. What evidence is available now
4. What is still unknown
5. What would make us proceed or stop
6. How this differs from existing work, existing diagnostics, or existing evaluation

Only after that, introduce labels such as `Coverage Benchmark`, `P0`, `P1`, `Evidence Pack`, `Readiness`, `screening`, `RCA/8D`, or `VHM`.

## Workflow

### 1. Plain-language lead

Start with a direct sentence a busy reviewer can understand.

Bad:

> P1 paid assessmentとしてCoverage BenchmarkはNo-Go。P0 ScreeningだけProceed。

Good:

> 現時点では、有償サービスとして売りに行く段階ではない。内部資料を使わない前提では、対象EPSのHILS試験名、関連DTC、freeze frame / extended data項目、既存レビュー会議体を見られず、既存レビューとの差分を示せないためである。これらの4項目は、内部資料を使える条件になった場合だけの再開条件として扱う。

### 2. Define the work before naming it

Before naming an artifact, write what it does.

Example:

> 市場で繰り返すEPSの困りごとに対して、サプライヤEPSの既存診断・既存評価・既存リリース確認で、どこまで説明または再現できているかを見る。

Then, if useful:

> この整理を以後 `Coverage Benchmark` と呼ぶ。

### 3. Translate labels into ordinary questions

Convert abstract labels into questions a stakeholder can answer.

| Label | Plain question |
|---|---|
| Coverage Benchmark | 既存診断・既存評価でこの市場painをどこまで説明できるか |
| Evidence Pack | 何が確認済みで、何が未確認で、何を推定してはいけないか |
| Readiness | 今ある資料で説明・評価・報告に使える状態か |
| P0 / P1 | いま売る話か、売る前に重複確認する話か |
| RCA / 8D | 原因断定ではなく、品質報告に転記できる確認済み事実か |

### 4. Separate conclusion levels

Do not collapse all decisions into one label.

Use explicit levels:

- Market need: exists / unclear / not supported
- Supplier control: can act / partly can act / OEM-dependent
- Business offer: sell now / do not sell yet / kill
- Next check: what exact field, artifact, or interview answer is needed

### 5. Make Stop conditions concrete

Write Kill / Stop criteria as observable facts, not broad judgments.

Bad:

> 差分がなければKill。

Good:

> 同等HILS試験があり、関連DTCとfreeze frameで速度・電圧・電流・assist state・failsafe stateが既に残り、既存レビュー会議体にも同じ確認欄があるなら、この方向は止める。

### 6. EPS supplier lens

End with what an EPS supplier can actually do.

Use this shape:

```markdown
EPSサプライヤとして言えること:
...

まだ言ってはいけないこと:
...

次に見る最小項目:
...
```

## Review Checklist

Before finalizing a report, check:

- Can a reader understand the conclusion without knowing project terms?
- Does the first paragraph say what is being judged?
- Are coined names introduced only after their meaning is explained?
- Does the report name the affected role or department?
- Does it distinguish "not sell yet" from "fully kill"?
- Are Proceed / Stop conditions observable?
- Does it avoid claiming fault prediction, warranty reduction, or root cause unless proven?
- Is the EPS supplier boundary explicit?

## Output Pattern

For this repo, a good human-facing report usually follows:

```markdown
## 結論
Plain-language conclusion.

## 何を判断しているか
The actual decision, without jargon.

## なぜ今そう判断するか
Evidence available and missing.

## 次に見る最小項目
Smallest inputs needed.

## 判定ルール
Proceed / Hold / Kill as observable conditions.

## EPSサプライヤとしての言い方
What to say, what not to say.
```
