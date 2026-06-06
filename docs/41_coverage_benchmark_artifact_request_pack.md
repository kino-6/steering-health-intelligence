# Coverage Benchmark Artifact Request Pack

## 結論

P1 assessmentを実行するには、いきなり大量の内部資料を要求しない。
まずは、**10個の最小artifact** だけでProceed / Hold / Killを切る。

この資料要求で分かることは、Coverage Benchmarkの価値そのものではなく、以下である。

> 実資料を使ってFAM08/FAM02/FAM11のcoverage matrixを埋められるか。  
> 既存HILS/DTC/release reviewの焼き直しか。  
> program横断で使えるか。

## 市場需要

Coverage Benchmarkの市場需要は、追加ログやRCA代行ではない。
市場で繰り返すEPS pain familyを、診断coverage、評価coverage、release gateへ変換したいという需要である。

しかし、この需要が本当にあるかは、実務artifactに入るかで決まる。
したがって、P1の最初の仕事は「資料収集」ではなく、**資料を見ればすぐ判定できる設計になっているか** の確認である。

## Artifact Request

TSV:

- [data/coverage_benchmark_artifact_request_pack.tsv](../data/coverage_benchmark_artifact_request_pack.tsv)

| ID | Artifact | Request to | Time | Why |
|---|---|---|---:|---|
| REQ01 | Target EPS operation profile | Program / validation lead | 15-30 min | FAM08/FAM02/FAM11が対象EPSに適用できるか |
| REQ02 | HILS / bench test list | Validation / HILS lead | 30-60 min | 既存HILS test planの焼き直しか |
| REQ03 | DTC specification | Diagnostic engineering | 60-120 min | 既存診断で説明できるか |
| REQ04 | Freeze frame / extended data list | Diagnostic engineering | 60-120 min | 主要factが残るか |
| REQ05 | Engineering reader / DID list | Diagnostic / service tool owner | 60 min | readerでcoverage matrixを埋められるか |
| REQ06 | Motor control monitor list | Motor control lead | 60-120 min | assist delivery explainabilityを見る |
| REQ07 | Power-stage / reset monitor | Power electronics / diagnostics | 60-120 min | power transient / voltage文脈を見る |
| REQ08 | Software / calibration release checklist | Software calibration lead | 30-60 min | FAM11とcalibration mappingを見る |
| REQ09 | Review / release gate template | Program / quality / diagnostic lead | 30-60 min | business workflow fitを見る |
| REQ10 | Two-program comparison candidate | Platform lead | half day | reuseとスケール性を見る |

## 重要な設計

各artifactは、完全版を要求しない。
最初はplaceholderでよい。

例:

- DTC specが出せないなら、related DTC listだけでよい
- Freeze frame詳細が出せないなら、field namesだけでよい
- HILS scriptが出せないなら、test case titlesだけでよい
- release checklistが出せないなら、見出しだけでよい

これでさえ出ないなら、P1はHoldでよい。
逆に、placeholderだけで「既存reviewと同じ」と分かるならKillでよい。

## Proceed / Hold / Kill

| Result | Condition |
|---|---|
| Proceed | 主要artifactの70%以上が入手でき、3 familyで3件以上のactionable gapがあり、既存reviewに貼れる |
| Hold | artifact不足でcoverage判定できない |
| Kill | 既存HILS/DTC/release reviewで十分、またはworkflowに貼れない |

## 買い手/利用者

このartifact requestは営業資料ではなく、買い手探索でもある。

| Request target | 見たいこと |
|---|---|
| Program / validation lead | FAM08/FAM02/FAM11が対象programに関係するか |
| Validation / HILS lead | HILS test planに入る余地があるか |
| Diagnostic engineering | 既存DTC/freeze frameとの差分があるか |
| Motor control / power electronics | assist delivery / power transientの説明gapがあるか |
| Software calibration | release gateとmarket painが接続できるか |
| Platform lead | 2 program比較でスケールするか |

## Kill条件

この段階で以下が見えたら、P1へ進まない。

- 3 familyすべて対象EPSに適用できない
- HILS test planに同等scenarioとdiagnostic checkが既にある
- DTC/freeze frame/extended dataで主要factが十分説明できる
- review / release gate templateに貼る場所がない
- 2 program比較の候補がなく、単発NREにしかならない
- RCA/8D転記しか用途がない

## EPSサプライヤとしての結論

次の実行単位は、P1本体ではなくartifact requestである。

> 10個の最小artifactを要求し、Coverage Benchmarkが既存レビューの焼き直しか、program横断のassessmentにできるかを先に切る。

ここでProceedしないなら、P1を売りに行くのは早い。
