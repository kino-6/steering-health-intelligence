# Steering Predictive Diagnostics Proceed Deep Dive

## 結論

Proceed候補を深掘りすると、最も前へ進めるべき順番は次である。

1. 低/高電圧または過温度によるreduced assist
2. 電気接続 / harness / network由来の複合症状
3. 外部信号または通信validity異常
4. 熱保護に近い状態
5. DTC履歴とreduced assistの再発監視

この5件は、いずれもEPS交換時期予測としてProceedではない。
Proceedの意味は、操舵系の状態を、整備action、vehicle health output、diagnostic triage、quality / warranty investigationへ変換できる可能性があるため、次のPhaseで必要データと権限境界を切る価値がある、という意味である。

一番強いのは、低/高電圧または過温度によるreduced assistである。
理由は、状態、整備action、診断読み順、言ってはいけないことが比較的はっきりしているためである。

深掘り表は [data/steering_predictive_diagnostics_proceed_deep_dive.tsv](../data/steering_predictive_diagnostics_proceed_deep_dive.tsv) に置く。

## 何を判断しているか

判断しているのは、Proceed候補を次の調査へ進める価値があるかである。

ここでいう次の調査とは、次の切り分けである。

1. そのstateを説明するために必要なDTC、freeze frame、extended data、limit stateは何か
2. EPSサプライヤが定義できる説明境界は何か
3. OEM、fleet、platform、service feedbackがないと言えないことは何か
4. predictive maintenance actionやvehicle health outputへ本当に接続できるか
5. remaining lifetime、replacement date、failure predictionと言ってよい条件があるか

## Rule Check

今回の判断では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Kaggle / Public Proxy Predictive Value Rule`
5. `Mandatory Rule Check Before Stop / Kill / Archive`

この文書では、Stop / Kill / Archiveを主結論にしていない。
ただし、Proceedを深掘りするため、次を確認する。

- Proceedを外販商品化の意味にしない
- Boschの予測語を正面から扱うが、EPS交換時期予測へ戻さない
- EPS内部状態や修理結果が公開されていないことだけを主Kill理由にしない
- 内部事実不足は、RUL、交換時期、安全保証、root cause断定を禁止する境界として扱う
- EPSサプライヤとして売る/実施する候補は、操舵系state、診断意味、整備action境界、vehicle health説明に置く

## 市場需要

Boschの予測ビジネスが示している需要は、車両が止まった後に読む診断ではなく、止まる前または問題が大きくなる前に、整備、入庫、部品、保証、品質対応を決めたいことである。

操舵系に置き換えると、需要は次のように読める。

1. EPSをすぐ交換すべきかではなく、まず電源、温度、外部信号、通信、複合電気症状をどう読むべきか知りたい
2. reduced assistや警告表示が出たとき、EPS内部故障、外部信号、電源、熱、networkのどれを先に疑うべきか知りたい
3. 同じ症状が再発しているのか、一時的な保護動作なのか、修理後も再発しているのかを分けたい
4. 顧客、service、品質、設計へ説明してよいことと言ってはいけないことを分けたい

## Proceed候補の深掘り

### 1. 低/高電圧または過温度によるreduced assist

これは最有力である。

理由は、低/高電圧、過温度、reduced assist、manual modeという流れが、整備actionに直結しやすいためである。
EPSサプライヤは、電源や温度そのものを車両全体で支配するわけではない。
しかし、操舵系がその条件でどう制限され、何を読めばEPS内部故障と区別できるかは説明できる可能性がある。

EPSサプライヤが定義できるもの:

- 電源・温度・assist制限・reduced assist / manual modeの意味
- DTC、freeze frame、extended dataで見るべき項目
- EPS内部故障と電源/熱contextを混同しない説明境界
- 交換時期ではなく、次に読むべき診断情報と整備確認

OEM / fleet / platformがないと言えないもの:

- 実車event capture
- key cycleをまたいだ継続性
- 修理結果
- 充電系や電源系の整備結果
- fleetの運行可否判断

現時点の深掘り判定:

`Proceed first`

次に作るべきもの:

- 電源/温度/reduced assistのdata boundary row
- 1ケースのdiagnostic reading order

### 2. 電気接続 / harness / network由来の複合症状

これはBosch型のvehicle healthに最も近い。

理由は、操舵assist低下だけでなく、複数ECU症状、電源、harness、network症状を束ねるためである。
Boschのcloud diagnosticsが言うfault groupingやcomponent localizationに近い。

EPSサプライヤが定義できるもの:

- 操舵症状をEPS単体故障と短絡しない説明
- EPS交換前に確認すべき電源、harness、networkの読み順
- 複合症状を見たときの禁止主張
- 操舵系が影響を受ける側か、原因側かを分ける説明境界

OEM / fleet / platformがないと言えないもの:

- 複数ECU DTCの全体取得
- 電源eventの時系列
- harness点検結果
- 修理結果
- 車両全体ログ
- service workflow

現時点の深掘り判定:

`Proceed second`

次に作るべきもの:

- fault grouping map
- EPSサプライヤとしてのboundary statement

### 3. 外部信号または通信validity異常

これは誤交換回避と責任境界に強い。

理由は、公開TSB上、外部ECU信号や通信値のinvalidが操舵側の表示やassist説明に影響し、steering gear交換回避につながる例があるためである。
EPSサプライヤは外部ECUを所有しない。
しかし、サプライヤEPSがどの外部信号に依存し、その信号がinvalidになった場合に何を言えるかは定義できる可能性がある。

EPSサプライヤが定義できるもの:

- 操舵系が依存する外部signal
- invalid時の表示やassist影響
- EPS内部故障と外部signal異常の責任境界
- DTC読み順

OEM / fleet / platformがないと言えないもの:

- 外部ECU DTC
- CAN signal validity
- 車両network状態
- service toolの読み取り権限
- 修理結果

現時点の深掘り判定:

`Proceed third`

次に作るべきもの:

- signal dependency table
- diagnostic triage example

### 4. 熱保護に近い状態

これは操舵系固有性が強い。

理由は、反復操舵、高負荷、motor current、温度、assist limit、thermal protectionが、操舵系のcomponent-specific load featureとして説明しやすいためである。
一方で、整備actionは「冷却、再発確認、使用条件確認、不要交換回避」に寄るため、SPD002やSPD004ほど強い事業出力にはなりにくい。

EPSサプライヤが定義できるもの:

- 操舵角反復
- motor current
- 温度
- assist limit
- thermal protection動作の意味
- 正常保護と故障の説明境界

OEM / fleet / platformがないと言えないもの:

- 実車使用条件
- 温度時系列
- DTC / freeze frame / extended data
- repair feedback
- 顧客利用context

現時点の深掘り判定:

`Proceed fourth`

次に作るべきもの:

- thermal state data boundary
- 顧客説明template

### 5. DTC履歴とreduced assistの再発監視

これは予測らしさが一番強いが、依存も一番大きい。

理由は、DTC履歴、発生頻度、再発間隔、status aging、修理結果を結べれば、maintenance forecastに近づくためである。
しかし、修理結果feedbackがなければ、DTC履歴だけで交換時期や故障発生を言う危険がある。

EPSサプライヤが定義できるもの:

- current / historical DTCの読み方
- 発生頻度、再発間隔、status agingの意味
- reduced assist履歴を交換時期へ短絡しない境界

OEM / fleet / platformがないと言えないもの:

- 修理結果
- 再発有無
- 作業時間
- 部品交換有無
- fleet / OEM service feedback loop

現時点の深掘り判定:

`Proceed with dependency`

次に作るべきもの:

- recurrence feedback loop requirement

## CoVe

| 検証質問 | 回答 | Confidence | 反映 |
|---|---|---:|---|
| Proceedは外販開始の意味か | No。必要データと権限境界を切る価値があるというscreening上のProceedである。 | High | 結論で明記 |
| 低/高電圧・過温度stateは最有力か | Yes。状態、診断読み順、整備actionが比較的つながりやすい。 | Medium-High | 深掘り優先順位1位 |
| 複合電気症状はEPSサプライヤの主語で扱えるか | Partial。vehicle-level診断だが、EPS交換前の境界説明はサプライヤが持てる可能性がある。 | Medium | Proceed secondだがplatform依存を明記 |
| 外部signal異常は操舵系価値か | Yes。ただしEPS内部故障ではなく、責任境界と誤交換回避の価値である。 | Medium-High | Proceed third |
| 熱保護stateは事業出力に強いか | Partial。操舵系固有性は強いが、整備actionは軽めでcondition explanation中心。 | Medium | Proceed fourth |
| DTC履歴は予測に近いか | Yes。ただしrepair feedback loopなしでは交換時期予測にしてはいけない。 | Medium | Proceed with dependency |

## EPSサプライヤとしての言い方

言ってよいこと:

> 操舵系には、predictive diagnostics / predictive maintenance / vehicle healthの対象としてscreeningを続ける価値があるstateが残る。最初に見るべきは、低/高電圧または過温度によるreduced assist、電気接続 / harness / network由来の複合症状、外部信号または通信validity異常、熱保護に近い状態、DTC履歴とreduced assistの再発監視である。

まだ言ってはいけないこと:

> これらのstateでEPSのremaining lifetimeやreplacement dateが分かる。

> thermal / voltage / communication stateだけで安全保証やroot cause断定ができる。

> EPSサプライヤ単独でBosch型fleet predictive maintenance platformを売れる。

> DTC履歴だけで交換時期を予測できる。

## 次のTask

次のPhase 3結果は、[docs/109_steering_predictive_diagnostics_data_boundary.md](109_steering_predictive_diagnostics_data_boundary.md) と [data/steering_predictive_diagnostics_data_boundary.tsv](../data/steering_predictive_diagnostics_data_boundary.tsv) に置く。

対象は、まず次の5件に絞る。

1. SPD002
2. SPD004
3. SPD003
4. SPD001
5. SPD007

各stateについて、次を切る。

1. 必要DTC
2. freeze frame / extended data
3. limit state
4. 温度、電源、通信context
5. repair feedback loop
6. EPSサプライヤが定義できること
7. OEM / fleet / platformなしでは言ってはいけないこと
