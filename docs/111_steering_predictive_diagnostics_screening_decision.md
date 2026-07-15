# Steering Predictive Diagnostics Screening Decision

## 結論

Phase 1からPhase 5まで実施した結果、操舵系predictive diagnosticsは、固定スコープの内部/顧客技術向けassessmentとしてProceedである。

ただし、Proceedするのは、EPSのremaining lifetimeやreplacement dateを予測する商品ではない。
また、Bosch型のfleet predictive maintenance platformをEPSサプライヤ単独で売る話でもない。

Proceedする対象は、自然言語で言うと次である。

> 操舵系で、電源、温度、外部信号、通信、複合電気症状、DTC履歴をどう読み、EPS内部故障と外部contextを混同しないために、どの診断情報、説明境界、禁止主張を用意すべきかを短期間で整理する。

この整理を、この文書では `Steering predictive diagnostics readiness assessment` と呼ぶ。

判断表は [data/steering_predictive_diagnostics_screening_decision.tsv](../data/steering_predictive_diagnostics_screening_decision.tsv) に置く。

## Rule Check

今回の判断では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Kaggle / Public Proxy Predictive Value Rule`
5. `Mandatory Rule Check Before Stop / Kill / Archive`

この文書では、Proceedだけでなく、Proceedしない範囲も明示する。
そのため、Rule Checkを本文に明示する。

- 市場需要から始めている
- 自然言語で、誰のどの業務の話かを説明している
- EPSサプライヤとして売る / 実施する / 言ってはいけないことに戻している
- Kill/Stop理由を、EPS内部状態やrepair feedbackが公開されていないことだけにしていない
- 不足データは、remaining lifetime、replacement date、failure prediction、安全保証、root cause断定を禁止する境界として扱っている
- 再開条件と次の検証質問を具体化している

## Market Demand

市場需要は、故障後の診断だけではなく、停止前または問題が大きくなる前に、整備、入庫、部品、保証、品質対応を決めたいことである。

Boschは、これを `predictive diagnostics`、`predictive maintenance`、`vehicle health` として扱っている。
そのため、このブランチでは予測語を正面から扱う。

操舵系で見るべき需要は、EPSがいつ壊れるかを単独で当てることではない。
reduced assist、警告表示、外部signal異常、電源/温度context、複合電気症状、DTC履歴が出たとき、診断企画、service、品質改善、顧客技術説明が、何を先に読み、何を言ってはいけないかを決めたい、という需要である。

## 未解決の痛み

未解決の痛みは、DTCや警告表示を見ても、次が混ざりやすいことである。

1. EPS内部故障
2. 電源や温度のcontext
3. 外部ECU signalや通信validity
4. harness / network / 複数ECU症状
5. 一時的な保護動作
6. 再発監視が必要な状態

これらが混ざると、EPS交換判断、service説明、顧客説明、品質分類、再発監視がぶれる。
ここに、EPSサプライヤが関与できる余地がある。

## Hypothesis

仮説は次である。

> EPSサプライヤは、操舵系stateについて、必要な診断情報、外部context、読み順、説明境界、禁止主張を整理することで、Bosch型のpredictive diagnostics / predictive maintenance / vehicle health文脈に入れる可能性がある。

この仮説は、EPS交換時期予測ではない。
また、fleet operationやworkshop appointmentをサプライヤが単独で決める話でもない。

## Solution

初期提供物は、5点に絞る。

1. Data boundary table
2. Diagnostic reading order
3. Fault grouping map
4. Signal dependency table
5. Explanation boundary sheet

最初のdemoは、SPD002の1ケースがよい。
低/高電圧または過温度によるreduced assistについて、DTC、voltage、temperature、assist mode、key cycle、repair feedback requirementを1枚にする。

## Buyer / User

初期利用者は、外部fleet operatorではない。

初期利用者は、EPSサプライヤ内の次の部署である。

1. 診断企画
2. 顧客技術説明
3. service / aftermarket連携
4. 品質改善
5. 製品企画 / システム設計
6. 評価企画

Phase 4では、少なくとも診断企画、顧客技術説明、service / aftermarket連携、品質改善に具体用途が出た。

## Why Supplier Can Play

EPSサプライヤが持てる手札は、fleet platformやOEM保証DBではない。

持てる手札は次である。

1. 操舵系stateの意味
2. DTC、freeze frame、extended data、limit stateの意味
3. 電源、温度、外部signal、通信contextが操舵説明へ与える影響
4. EPS内部故障と外部contextを混同しない境界
5. 顧客技術説明で言ってよいこと / 言ってはいけないこと

この手札は、Bosch型platformを代替しない。
しかし、Bosch型platformやOEM serviceが操舵系を扱うときに必要なdomain contentにはなりうる。

## EPS Supplier Conclusion

EPSサプライヤとしての判断は次である。

### 売る / 実施する

固定スコープの内部/顧客技術向けassessmentとしてProceedする。

内容:

- 操舵系state候補を3-5件に絞る
- 必要DTC、freeze frame、extended data、limit state、温度・電源・通信contextを切る
- 診断読み順を作る
- service / 顧客技術説明へ転記できる説明文を作る
- 言ってはいけないことを明記する

### まだ売らない

次は、現時点では売らない。

- EPS remaining lifetime prediction
- EPS replacement date prediction
- Bosch型fleet predictive maintenance platform
- warranty cost reduction service
- safety guarantee service

### 条件付きで再検討

特定programで、repair feedback loop、再発有無、作業結果、部品交換有無が取れる場合だけ、SPD007をmaintenance forecast候補として再検討する。

## Demo

最初のdemoは、SPD002の1ケースで作る。

テーマ:

> 低/高電圧または過温度によるreduced assistを、EPS内部故障と短絡せず、電源・温度context、assist mode、DTC履歴、repair feedback requirementへ分けて読む。

Demoで見せるもの:

1. Event summary
2. 必要DTC
3. freeze frame / extended data
4. reduced assist / manual mode
5. 電源・温度context
6. 読む順番
7. 言ってよいこと
8. 言ってはいけないこと
9. repair feedbackがないと進めない判断

## What Not To Claim

次は言ってはいけない。

1. 公開情報だけでEPS remaining lifetimeやreplacement dateが分かる
2. DTC履歴だけで故障発生時期が分かる
3. thermal / voltage / communication stateだけで安全保証できる
4. 複合症状からroot causeや保証責任を断定できる
5. EPSサプライヤ単独でfleet dispatchやworkshop appointmentを決められる
6. Boschのbatteryやbrake padのRUL事例を、そのままEPSへ転用できる

## Kill Criteria

この方向を止める条件は次である。

1. SPD002の1ケースdemoが、既存service manualやDTC表の要約にしかならない
2. 診断企画、顧客技術説明、service連携、品質改善のうち、2部署以上に転記できない
3. 価値説明に、remaining lifetime、replacement date、安全保証、root cause断定、保証費削減が必要になる
4. 必要データがOEM/fleet/platformに完全依存し、EPSサプライヤが定義できるstateや説明境界が残らない
5. 汎用テレマティクス、ADAS、IDS、路面分類、一般電装診断と区別できない

重要なのは、次である。

> EPS内部状態、repair feedback、fleet dataが公開情報だけで見えないこと自体は、この方向の主Kill理由にしない。

それらは、RUL、交換時期、root cause、保証費削減を言わないための境界である。

## Final Decision

最終判断:

> Proceed as fixed-scope steering predictive diagnostics readiness assessment.

Proceedの範囲:

- data boundary
- diagnostic reading order
- fault grouping map
- signal dependency table
- explanation boundary
- not-to-claim list

Proceedしない範囲:

- EPS RUL
- EPS replacement date
- fleet predictive maintenance platform
- safety guarantee
- root cause / warranty cost reduction

次に実施する最小作業:

> SPD002の1ケースdiagnostic reading orderを作る。

その後の追加議論では、SPD002だけに閉じず、既存継続候補とユーザー提案の内部重要モジュールruntime deviation案を並列に深掘りした。
この結果は [docs/112_steering_predictive_diagnostics_parallel_continuation_deep_dive.md](112_steering_predictive_diagnostics_parallel_continuation_deep_dive.md) と [data/steering_predictive_diagnostics_parallel_continuation.tsv](../data/steering_predictive_diagnostics_parallel_continuation.tsv) に置く。
