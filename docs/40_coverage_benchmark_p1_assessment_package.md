# Coverage Benchmark P1 Assessment Package

## 結論

`FAM08 Immediate Visibility Review` でProceed寄りになった場合、次に売り物として試すべき最小単位はこれ。

> **EPS Diagnostic / Robustness Coverage Benchmark P1 Assessment**

これはSaaSでもHILツールでもなく、2-4週間の固定費assessmentである。
目的は、`FAM08 stop-start low-speed` だけでなく、`FAM02 low-speed high-effort` と `FAM11 software/failsafe` に同じrow構造を適用し、Coverage Benchmarkがprogram横断の業務成果物になるかを判定すること。

## 市場需要

市場ではEPSのdriver-visible painが繰り返し出る。
ただし、個別caseのRCAを当てるだけではスケールしない。

P1の市場需要は、より上流に置く。

> 公開市場で繰り返すEPS pain familyを、サプライヤEPSの診断coverage、HILS/bench coverage、software release gateでどこまでcoverしているかを、program横断で説明したい。

## 未解決の痛み

現状の痛みは、資料がないことではない。

むしろ逆で、DTC仕様、HILS test plan、calibration release checklist、過去不具合、品質報告が分散している。
そのため、以下が見えにくい。

- 市場pain familyごとに、既存DTC/freeze frameで何が説明できるか
- 既存HILS/bench testが市場painを本当にcoverしているか
- software/failsafe release gateがdriver-visible painと接続しているか
- 複数programでcoverage差分を比較できるか
- 既存reviewと何が違うのか

## 仮説

P1 assessmentの仮説はこれ。

> FAM08/FAM02/FAM11の3 familyに同じcoverage row構造を適用できれば、Coverage Benchmarkは個別RCAよりスケールし、diagnostic engineering / validation / software release gate向けの短期assessmentとして成立する可能性がある。

逆に、3 familyでrow構造が崩れる、または既存HILS/DTC reviewの焼き直しならKillでよい。

## 解決策

P1で作る成果物は3つ。

| Artifact | File |
|---|---|
| P1 assessment plan | [data/coverage_benchmark_p1_assessment_plan.tsv](../data/coverage_benchmark_p1_assessment_plan.tsv) |
| Family reuse matrix | [data/coverage_benchmark_family_reuse_matrix.tsv](../data/coverage_benchmark_family_reuse_matrix.tsv) |
| P1 decision rubric | [data/coverage_benchmark_p1_decision_rubric.tsv](../data/coverage_benchmark_p1_decision_rubric.tsv) |

## 初期提供物

### P1 workstreams

| Workstream | Output | Timebox | Kill risk |
|---|---|---:|---|
| Kickoff / scope | P1 scope sheet | 0.5 day | 対象familyやreview workflowがない |
| Artifact intake | Artifact availability map | 1 day | DTC/HILS/reader資料が出ない |
| FAM08 fill | FAM08 filled matrix | 1-2 days | ほぼUnknown |
| FAM02 fill | FAM02 filled matrix | 1-2 days | FAM08形式を再利用できない |
| FAM11 fill | FAM11 filled matrix | 1-2 days | release/safety reviewの焼き直し |
| Gap classification | Gap classification table | 1 day | actionable gapがない |
| Workflow fit | Workflow fit decision | 0.5-1 day | 会議体に貼れない |
| Multi-program check | Reuse scorecard | 1-2 days | programごとに個別設計 |
| Business decision | P1 decision memo | 0.5 day | 既存reviewの言い換え |

## 買い手/利用者

| Role | P1で見る価値 |
|---|---|
| Diagnostic engineering | 既存DTC/freeze frame/extended dataが市場painを説明できるか |
| Validation / HILS | 市場painがnamed test caseとして評価planに入っているか |
| Software calibration / failsafe | release gateがdriver-visible painと接続しているか |
| Program / platform lead | 複数program間でcoverage差分を比較できるか |
| Customer quality | 必要時にdownstream summaryへ転記できるか |

## Family Reuse

P1で一番重要なのは、FAM08の表をFAM02/FAM11へ横展開できるかである。

| Benchmark row | FAM08 | FAM02 | FAM11 | Reuse |
|---|---|---|---|---|
| Market pain fit | stop-to-launch assist loss | low-speed high-effort | software/failsafe assist loss | High |
| Scenario state | standstill / launch / steering input | low-speed / high steering / driver torque | operating mode / fault trigger | Medium |
| Assist delivery | command vs current vs limit | command vs current vs limit | assist enabled / limited / unavailable | High |
| Control/failsafe state | assist, derating, failsafe, latch | assist mode/state under high effort | failsafe entry/recovery | High |
| DTC/freeze frame | speed, voltage, current, assist state | speed, angle, torque, thermal, assist state | DTC, failsafe, software version | High |
| HILS/bench evidence | stop-launch test | low-speed high-effort test | failsafe/fault injection test | High |
| Program comparison | Program A/B comparison | Program A/B comparison | Program A/B comparison | High |
| Workflow fit | program / release gate | diagnostic / validation review | software release / safety review | Medium-High |

この表から見る限り、**row構造はかなり再利用できる可能性がある**。
ただし、実データで埋めるとsignal名やreview ownerはfamilyごとに変わる。
したがって、現時点の判断は `Proceed to P1 design validation` であり、ビジネス成立の証明ではない。

## Decision Rubric

P1のProceed条件は厳しめに置く。

| Criterion | Proceed | Kill |
|---|---|---|
| Actionable coverage gaps | 3 family合計で3件以上 | 0件、または既存資料で解決済み |
| Workflow fit | 既存会議体に貼れる | 貼る場所がない |
| Family reuse | row構造70%以上再利用 | 40%未満 |
| Supplier control | supplier-owned資料/信号/評価が70%以上 | OEM依存が強すぎる |
| Existing review duplication | 既存reviewを補完する | 完全に焼き直し |
| Decision owner | diagnostic/validation/program leadが明確 | owner不在 |
| Downstream-only risk | diagnostic/validation/release gate価値が主 | RCA/8D転記だけ |

## 検証方法

P1 assessmentを実施する前に、以下を確認する。

1. 対象EPSのHILS test listを1つ取得する
2. DTC spec / freeze frame / extended data listを1つ取得する
3. reader DID listを1つ取得する
4. release gateまたはdiagnostic design reviewの既存templateを1つ取得する
5. FAM08/FAM02/FAM11の3 familyでrow構造を試し埋めする

この5つができない場合、P1はHold。

## Kill条件

以下ならCoverage Benchmark仮説はKill寄り。

- FAM08/FAM02/FAM11のrow構造が再利用できない
- 既存HILS test planに同等scenarioとdiagnostic checkがすでにある
- DTC/freeze frame/extended dataで主要factがすでに十分説明できる
- workflow fitがなく、資料の置き場所がない
- RCA/8D転記だけが価値になる
- ownerが不明

## Chain-of-Verification

| Question | Evidence check | Confidence | Impact |
|---|---|---:|---|
| FAM08だけで商品になるか | 1 familyだけでは個別NREに近い。 | High | 3 family reuseへ広げる |
| FAM02/FAM11へ同じrow構造を使えるか | market pain, scenario state, assist delivery, DTC/freeze frame, HILS evidence, program comparisonは共通化可能。 | Medium | P1 assessment化の条件 |
| 既存reviewの焼き直しではないか | これは最大リスク。P1 rubricでduplicationをKill条件にする。 | High | Kill条件に明記 |
| ビジネス価値は証明済みか | まだ未証明。実資料で埋め、workflow fitを確認する必要がある。 | Low | P1設計止まり |
| EPSサプライヤの主語に戻っているか | DTC/HILS/reader/release gateが中心で、OEM fleet dataを初期前提にしていない。 | Medium-High | Keep |

## EPSサプライヤとしての結論

次に実施すべきことは、追加の公開市場調査ではない。

> FAM08/FAM02/FAM11の3 familyで、同じcoverage row構造が実資料に対して使えるかを確認するP1 assessment packageを試す。

これで見えること:

- Coverage Benchmarkがプログラム横断で使えるか
- 既存HILS/DTC reviewの言い換えか
- validation / diagnostic / release gateのどこに入るか
- 事業としてP2へ進む余地があるか

このP1で差分が出なければ、Coverage Benchmark仮説はかなりKill寄りでよい。
