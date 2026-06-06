# FAM08 Immediate Visibility Review

## 結論

`FAM08 stop-start low-speed` の価値は、**全部がすぐ見えるわけではない**。

ただし、以下はかなり早く見える。

> 既存HILS test plan、DTC / freeze frame / extended data仕様、reader DID、software/calibration release checklistを見れば、Coverage Benchmarkが新規価値か、既存レビューの言い換えかは1日以内にかなり判定できる。

つまり「すぐ見える」の正体はこれ。

- 市場painが対象EPSに適用できるか
- 既存HILS/benchに同等scenarioがあるか
- 既存DTC/freeze frameで主要factが残るか
- release gate / diagnostic design reviewに貼る場所があるか
- program横断で同じchecklistを使えるか

## Quick Answer

| Question | すぐ見えるか | 必要資料 | 判定 |
|---|---:|---|---|
| FAM08が対象EPSの使用条件に入るか | Yes | vehicle operation profile / validation scope | 入らなければKill |
| 既存HILS test planに同等scenarioがあるか | Yes | HILS test list / bench scripts | 同等かつ診断確認込みならKill寄り |
| 既存DTC/freeze frameで主要factが残るか | Mostly | DTC spec / extended data / reader | 主要factが残るなら追加価値は弱い |
| assist command/current/limitが比較できるか | Mostly | motor control monitor / extended data | 見えなければgap候補 |
| power transient/reset/overvoltage文脈が残るか | Mostly | power-stage monitor / reset history | 見えなければgap候補 |
| state transitionやoccurrenceが残るか | Partly | state machine / DEM / NvM / reader | ここは内部依存が強い |
| program横断に使えるか | Partly | 2 program分の診断/HILS資料 | 横展開できなければNRE止まり |
| ビジネス価値があるか | Not immediately | 実務担当レビュー | 既存会議体に貼れなければ弱い |

## Immediate Triage

TSV:

- [data/fam08_immediate_visibility_triage.tsv](../data/fam08_immediate_visibility_triage.tsv)

| Area | What should be visible now | Quick decision |
|---|---|---|
| Market pain fit | 対象EPSがstop-to-launch / low-speed assist demandを持つか | 対象外ならFAM08 Kill |
| HILS scenario duplication | 既存HILS/benchに同等testがあるか | 同等testが診断確認込みならKill寄り |
| Diagnostic snapshot sufficiency | speed/standstill/voltage/current/assist/failsafe/calibrationが残るか | 十分なら新規価値は薄い |
| Assist delivery explainability | assist command/current/current limit/trackingを比較できるか | 見えなければcoverage gap |
| Power transient explainability | overvoltage/reset/brownoutが残るか | 見えなければcoverage gap |
| Control-state transition visibility | assist/failsafe transitionやoccurrenceが低帯域で残るか | 見えなければ差別化余地 |
| Calibration mapping | version-to-behaviorがrelease gateで追えるか | 追えなければrelease gate価値 |
| Program reuse | 2 program以上に同じchecklistを使えるか | 使えなければスケール弱い |
| Workflow fit | program review / diagnostic review / release gateに貼れるか | 貼れなければ売れにくい |

## Decision Rule

即時判定はこのルールにする。

| Result | Condition | Action |
|---|---|---|
| Proceed | coverage gapが3つ以上あり、既存review/release gateに貼れる | P1 assessment化を検討 |
| Hold | 内部資料がなく、gap有無が判定できない | 必要artifactを要求 |
| Kill | 既存HILS test planとDTC/freeze frameで十分、またはworkflowに貼れない | FAM08を止め、FAM02/FAM11または仮説修正へ |

ここで重要なのは、`gapがあること` だけではProceedにしないこと。
gapがあっても、既存reviewやrelease gateに貼れないなら、ビジネス価値になりにくい。

## What Is Visible Today

今日すぐ見える可能性が高いもの:

- 対象EPSにstop-start / launch / low-speed assist exposureがあるか
- HILS test planに同等scenarioがあるか
- DTC / freeze frame / extended dataにspeed、voltage、current、assist stateが入っているか
- reader DIDでsoftware/calibration versionが読めるか
- release gateやdiagnostic reviewの既存資料にmatrixを貼れるか

今日すぐには見えにくいもの:

- state transition edgeを低帯域factで残せるか
- command-vs-currentが品質/診断説明で本当に使えるか
- program横断で同じchecklistが使えるか
- 顧客がNREを払うか

## Required Internal Artifacts

この検証に必要な資料は、最小で以下。

| Artifact | Purpose |
|---|---|
| HILS / bench test list | FAM08が既存評価にあるか見る |
| DTC spec | 関連DTCと発火条件を見る |
| Freeze frame / extended data list | 既存snapshotで説明できるfactを見る |
| Engineering reader / DID list | returned unitやbenchで読めるfactを見る |
| Motor control monitor list | assist command/current/current limitが見えるか見る |
| Power-stage monitor / reset history | voltage / overvoltage / reset文脈を見る |
| Calibration ID / software version DID | release versionとbehaviorを紐づける |
| Review / release gate template | このmatrixを貼る業務成果物があるか見る |

## EPS Supplier Conclusion

このNextActionで見えるのは、`FAM08が売れるか` そのものではない。

見えるのはこれ。

> Coverage Benchmarkが既存HILS/DTC/diagnostic reviewの焼き直しか、それとも評価・診断・release gateに入る余地があるか。

判断はかなり早い。

- 既存HILS/DTC資料で十分ならKill
- 資料が足りず判定不能ならHold
- gapがあり、既存reviewに貼れるならProceed

## Next If Proceed

Proceedなら、次はP1 assessmentの最小構成を作る。

- FAM08 coverage matrixを対象EPSの実資料で埋める
- FAM02 low-speed high-effortにも同じ形式を適用する
- FAM11 software/failsafeにも同じ形式を適用する
- 3 familyで同じrow構造が使えるか確認する

3 familyで横展開できれば、初めて `Coverage Benchmark` として事業仮説が少し立つ。
