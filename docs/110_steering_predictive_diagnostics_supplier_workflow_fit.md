# Steering Predictive Diagnostics Supplier Workflow Fit

## 結論

Phase 4では、Phase 3で切ったdata boundaryを、EPSサプライヤ内の部署別成果物へ転記できるかを確認した。

結論は、部署別成果物へ転記できる余地はある。
特に強いのは、診断企画、顧客技術説明、service / aftermarket連携、品質改善である。

ただし、ここでも売るものは「EPS交換時期予測」ではない。
売る、または社内で使う候補は、操舵系stateについて、どの診断情報を読み、どの外部contextを確認し、何を言ってはいけないかを整理する固定スコープassessmentである。

部署別整理表は [data/steering_predictive_diagnostics_supplier_workflow_fit.tsv](../data/steering_predictive_diagnostics_supplier_workflow_fit.tsv) に置く。

## 何を判断しているか

判断しているのは、操舵系predictive diagnosticsの候補が、EPSサプライヤ内の実際の業務成果物へ貼れるかである。

見る部署は次である。

1. 診断企画
2. 品質改善
3. 顧客技術説明
4. service / aftermarket連携
5. 製品企画 / システム設計
6. 評価企画 / HILS / bench評価

## Rule Check

今回の判断では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Kaggle / Public Proxy Predictive Value Rule`
5. `Mandatory Rule Check Before Stop / Kill / Archive`

この文書では、Stop / Kill / Archiveを主結論にしていない。
ただし、部署別にHold条件を書くため、次を確認する。

- 市場需要は、停止前または問題拡大前に整備・診断・説明行動を決めたいことである
- Boschの予測語を正面から扱う
- 部署別成果物を、EPS交換時期予測や安全保証へすり替えない
- EPSサプライヤの手札は、state定義、診断意味、説明境界、必要データ定義、禁止主張である
- OEM保証DB、fleet operation、service outcomeは、外部依存として明示する

## 部署別の見立て

### 1. 診断企画

最も強い。

診断企画には、DTC、DID、freeze frame、extended data、service diagnostic flowという既存成果物がある。
SPD002、SPD003、SPD004、SPD001、SPD007は、どれも診断読み順へ落とせる。

特に価値が出るのは、DTC単体ではなく、電源、温度、外部signal、複合症状をどう読むかを整理できる点である。

転記できる成果物:

- 操舵系predictive diagnostics reading order
- data boundary table
- DTC / freeze frame / extended data追加確認リスト
- service flowに入れる禁止主張

Hold条件:

- 既存DTC表やservice manualの整形にしかならない場合

### 2. 品質改善

強いが、repair feedback依存がある。

品質改善では、field issue分類、NTF、誤交換分析、再発監視、field-to-engineering feedbackへ転記できる可能性がある。
SPD004、SPD003、SPD007が特に強い。

ただし、修理結果や再発有無がないと、品質改善としては事実確認が弱い。
そのため、Phase 4時点では「品質改善に使える」と断定するより、「品質改善が必要とするfeedback項目を定義できる」と言うのが安全である。

転記できる成果物:

- quality investigation input map
- recurrence feedback requirement
- NTF / 誤交換を避ける確認観点

Hold条件:

- 既存の品質分類と同じ言葉にしかならない場合
- 修理結果feedbackが全く取れず、仮説確認ができない場合

### 3. 顧客技術説明

強い。

顧客技術説明では、予測診断という言葉を使いながら、EPSサプライヤが言えることと言ってはいけないことを切れる。
これは今回の探索と相性がよい。

特に、低/高電圧、外部signal、複合電気症状、熱保護については、顧客説明で誤解されやすい。
ここを自然言語で整理できるなら、既存DTC表の整形を超える価値がある。

転記できる成果物:

- OEM / customer explanation boundary sheet
- technical note
- 禁止主張リスト
- 問い合わせ回答template

Hold条件:

- 具体stateなしの一般論や免責文だけになる場合

### 4. service / aftermarket連携

中から強い。

Service noteやworkshop reading orderへ落とせる可能性がある。
SPD002とSPD004は特に相性がよい。

ただし、EPSサプライヤ単独でservice toolやworkshop operationを所有するわけではない。
したがって、提供できるのは「整備現場に出せる文書そのもの」ではなく、「service noteへ転記できる操舵系の読み順と境界」である。

転記できる成果物:

- service-facing triage note
- workshop reading order seed
- unnecessary replacement avoidance note

Hold条件:

- service現場に出せる具体行動がない場合
- OEM service tool権限がないと何もできない場合

### 5. 製品企画 / システム設計

中程度。

製品企画やシステム設計では、RFQ確認質問、diagnostic content requirement、vehicle health input requirementへ転記できる。
ただし、ここは一般的なRFQ質問や既存診断要求と重複しやすい。

価値が出るのは、予測診断に必要なDTC、freeze frame、extended data、limit state、external signal dependency、data capture triggerを、設計初期の確認質問へ変換できる場合である。

転記できる成果物:

- RFQ / design review question list
- diagnostic content requirement
- vehicle health input requirement

Hold条件:

- 質問が一般論だけになる場合
- OEM用途想定やfleet運用をサプライヤが代替定義する方向へ逸れる場合

### 6. 評価企画 / HILS / bench評価

中程度。

診断で残すべき情報を、評価で再現・確認する条件へ戻すことはできる。
SPD002、SPD001、SPD003が候補になる。

ただし、評価scenarioそのものを有償価値の本体にしてはいけない。
このRepoの本線は、評価時間短縮や評価自動化ではなく、predictive diagnostics outputを検証するための評価条件である。

転記できる成果物:

- diagnostic validation scenario seed
- HILS / benchで見るDTC / freeze frame再現条件

Hold条件:

- 評価scenario作成だけに閉じる場合
- 評価時間短縮テーマへ戻る場合

## Phase 4判定

部署別成果物への転記可能性は、次の通りである。

| Department | Fit | Reason |
|---|---|---|
| 診断企画 | Strong | DTC、freeze frame、extended data、診断読み順へ直接つながる |
| 顧客技術説明 | Strong | 言ってよいこと / 言ってはいけないことを切れる |
| service / aftermarket連携 | Medium-High | service noteやreading orderへ転記可能。ただしOEM service権限依存 |
| 品質改善 | Medium-High | 誤交換、NTF、再発監視へ使える。ただしrepair feedback依存 |
| 製品企画 / システム設計 | Medium | RFQ/設計確認質問へ転記可能。ただし一般論化しやすい |
| 評価企画 | Medium | 診断検証条件へ転記可能。ただし評価テーマへ逸れやすい |

このため、Phase 4の条件である「少なくとも2部署で具体用途が出る」は満たす。

## CoVe

| 検証質問 | 回答 | Confidence | 反映 |
|---|---|---:|---|
| 部署別成果物へ転記できるか | Yes。診断企画、顧客技術説明、service連携、品質改善で具体用途がある。 | Medium-High | Phase 4判定 |
| 既存DTC表の整形で終わるリスクはあるか | Yes。特に診断企画と製品企画である。外部contextと禁止主張まで切れるかが差分になる。 | Medium | Hold条件 |
| EPSサプライヤの主語は残るか | Partial。診断意味、state定義、説明境界は残るが、service outcomeやfleet operationは外部依存である。 | Medium | 結論に反映 |
| RULや交換時期に進めるか | No。Phase 4時点では進めない。 | High | 禁止主張に反映 |

## EPSサプライヤとしての言い方

言ってよいこと:

> 操舵系predictive diagnostics候補は、診断企画、顧客技術説明、service / aftermarket連携、品質改善へ転記できる余地がある。特に価値があるのは、電源、温度、外部signal、複合電気症状、DTC履歴を、EPS内部故障と混同しない診断読み順や説明境界へ変換することである。

まだ言ってはいけないこと:

> EPSサプライヤ単独で、workshop appointment、fleet dispatch、remaining lifetime、replacement date、failure prediction、保証費削減を提供できる。

## 次のTask

次はPhase 5として、screening全体の最終判断を出す。

現時点では、次の判断になりそうである。

- 固定スコープの内部/顧客技術向けassessmentとしてはProceed
- Bosch型fleet predictive maintenance platformとしてはNo
- EPS remaining lifetime / replacement date predictionとしてはNo
- repair feedback loopが取れる特定programでは、maintenance forecast候補として再検討
