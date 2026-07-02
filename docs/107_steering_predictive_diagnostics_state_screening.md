# Steering Predictive Diagnostics State Screening

## 結論

Phase 1とPhase 2を実行した結果、操舵系で `predictive diagnostics / predictive maintenance / vehicle health` の対象としてscreeningを続ける候補は残る。

ただし、残る候補は「EPS交換時期を当てる」ものではない。
残るのは、熱、電源、温度、外部信号、通信、複合電気症状、DTC履歴を使い、操舵系の状態を先に読み、診断読み順、整備確認、vehicle health説明、誤交換回避、品質調査へつなげる方向である。

今回のscreeningでは、7件の既存候補のうち、4件を `Proceed`、2件を `Hold`、1件を `Proceed with dependency` とした。
最終的な外販可否はまだ判断しない。
次は、各stateに必要なデータと、EPSサプライヤが持てる範囲 / OEM・fleet・platform依存の範囲を切る。

Task 1の要求変換表は [data/steering_predictive_diagnostics_screening_requirements.tsv](../data/steering_predictive_diagnostics_screening_requirements.tsv) に置く。
Task 2のstate別screening表は [data/steering_predictive_diagnostics_state_screening.tsv](../data/steering_predictive_diagnostics_state_screening.tsv) に置く。

## 何を判断しているか

判断しているのは、Boschの予測ビジネスで使われている言葉を、操舵系で具体的な作業対象にできるかである。

Bosch側の言葉は、次である。

1. `predictive diagnostics`
2. `predictive maintenance`
3. `vehicle health`
4. `remaining lifetime`
5. `maintenance forecast`
6. `recommended replacement date`

操舵系側では、これらをそのままEPS交換時期予測へ移植しない。
まず、操舵系として予測診断の対象にできるstateがあるか、そしてそのstateが整備行動やvehicle health outputへ接続できるかを見る。

## Rule Check

今回の判断では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Kaggle / Public Proxy Predictive Value Rule`
5. `Mandatory Rule Check Before Stop / Kill / Archive`

この文書では、Stop / Kill / Archiveを主結論にしていない。
ただし、screeningで候補を落とす可能性があるため、次を確認する。

- 市場需要は、fleet/OEM/serviceが停止前に整備や診断行動を決めたいことである
- Boschの予測語を避けず、ただしEPS単体の交換日予測へ狭めない
- EPS内部状態や修理結果が公開されていないことだけを主Kill理由にしない
- EPSサプライヤとして売る/実施する可能性は、操舵系state、診断意味、整備action境界、vehicle health説明に置く
- safety guarantee、root cause断定、保証費削減断定、公開情報だけのEPS RULは言わない

## 市場需要

Boschの公式情報では、fleetやOEMが、予期しない故障や車両停止を避け、整備計画、部品手配、入庫判断、保証・品質判断を早く行いたい需要が示されている。
Boschはこれを `predictive diagnostics`、`predictive maintenance`、`vehicle health` として商材化している。

操舵系に置き換えると、市場需要は「EPSがいつ壊れるかを単独で当てたい」ではない。
より手前に、操舵assist低下、熱保護、電源/温度/通信由来の状態、複合症状、DTC履歴を見て、診断や整備の行動を早く決めたい需要がある。

## Task 1: Bosch要求を操舵系screening要求へ変換

Task 1では、Boschの予測ビジネスを10個の作業要求へ変換した。

要点は次である。

| 要求 | 操舵系で見ること | 判断 |
|---|---|---|
| fleet predictive maintenance | 操舵系stateが整備優先度や次回運行前確認を変えるか | 残す |
| cloud diagnostics | DTC、freeze frame、extended data、limit stateを診断読み順へ変換できるか | 残す |
| predictive diagnostics | 操舵系固有のload featureとdiagnostic featureがあるか | 残す |
| remaining lifetime / maintenance forecast | condition explanation止まりか、maintenance forecastまで言えるか | 境界を切る |
| vehicle health | 品質改善、保証調査、field-to-engineering feedbackへ転記できるか | 残す |
| Uptake / ecosystem | platformではなくdomain contentとして何を渡せるか | 残す |
| battery SoH | 操舵系に直接測れるhealth stateがあるか | 注意して使う |
| brake pad RUL | 操舵系に直接摩耗量があるか | RUL転用はしない |
| powertrain lifecycle | stateからrecommendationへのeffect chainがあるか | 残す |
| connectivity | 必要信号、event trigger、取得権限を切れるか | 残す |

結論として、Boschの予測ビジネスは操舵系screeningへ変換できる。
ただし、batteryやbrake padのような直接劣化/RULの強さは、操舵系にはまだ確認できていない。

## Task 2: 操舵系state候補のscreening

### Proceed候補

#### SPD001: 熱保護に近い状態

反復した大舵角操作や高負荷操舵により、熱保護やassist制限に近づく状態である。
これは操舵系固有のload featureとdiagnostic featureに近く、predictive diagnostics候補として残す。

使い道:

- thermal protection正常作動と故障の切り分け
- 冷却、再発確認、使用条件確認
- 誤交換回避
- 顧客説明

まだ言ってはいけないこと:

- EPS寿命
- 交換日
- root cause断定

#### SPD002: 低/高電圧または過温度によるreduced assist

低電圧、高電圧、過温度によりreduced assistやmanual modeに近づく状態である。
これは整備actionへ最もつながりやすい。

使い道:

- 電源系確認
- 充電系確認
- 温度再発確認
- 入庫優先度
- steering assist availability contextの説明

まだ言ってはいけないこと:

- 低電圧や過温度が出ればEPS故障である
- 交換時期が分かる
- 安全保証できる

#### SPD003: 外部信号または通信validity異常

外部ECU信号や通信値がinvalidになり、操舵側の表示やassist説明へ影響する状態である。
これはEPS内部故障ではないが、vehicle health outputとdiagnostic triageでは強い。

使い道:

- steering gear交換回避
- 外部ECU DTCの先読み
- signal validity確認
- 責任境界整理

まだ言ってはいけないこと:

- Steering Assist ReducedをEPS内部故障と短絡する
- 外部信号異常だけでroot causeを断定する

#### SPD004: 電気接続 / harness / network由来の複合症状

操舵assist低下に加え、複数ECU症状、電源、harness、network症状が同時に出る状態である。
これはBosch型のcloud diagnosticsが扱うfault groupingやcomponent localizationに近い。

使い道:

- EPS交換前に電源/harness/network確認へ誘導
- 複数ECU症状のvehicle health output
- 診断読み順の変更
- field trendとしての品質調査

まだ言ってはいけないこと:

- 複合症状をEPS単体故障と断定する
- root causeや保証責任を断定する

### Proceed with dependency候補

#### SPD007: DTC履歴とreduced assistの再発監視

現在または過去DTC、発生頻度、再発間隔、status agingからreduced assistの再発や整備確認を扱う状態である。
これは予測らしさが強いが、修理結果feedbackや発生頻度への依存が大きい。

使い道:

- recurrence monitoring
- Techline escalation
- 追加点検
- repair feedback loop確認
- quality investigation

まだ言ってはいけないこと:

- DTC履歴だけで交換時期を予測できる

### Hold候補

#### SPD005: steering gear thermal exposure

特定の熱環境や部品配置によりsteering gearが高温にさらされ、thermal protectionやassist低下へつながる状態である。
材料としては有用だが、特定recall依存が強い。
汎用screeningではSPS001/002より弱い。

#### SPD006: DTC coverage / fallback / degraded state boundary

DTC coverage、warning、fallback、degraded state、安全要求の対応関係である。
これは土台として重要だが、単体では予測ビジネスの価値になりにくい。
既存safety case、FMEA、DTC表を超える業務成果物になるかを次に確認する。

## 現時点のscreening結果

| 判定 | 件数 | 対象 |
|---|---:|---|
| Proceed | 4 | SPD001, SPD002, SPD003, SPD004 |
| Proceed with dependency | 1 | SPD007 |
| Hold | 2 | SPD005, SPD006 |
| Stop | 0 | なし |

この結果は、操舵系predictive diagnostics候補が残ることを示す。
ただし、残る価値は、RULや交換日ではなく、整備action、vehicle health output、diagnostic triage、quality/warranty investigationへの接続である。

## EPSサプライヤとしての結論

EPSサプライヤとして次に実施できることは、5件の候補について必要データと権限境界を切ることである。

優先順位は次である。

1. SPD002: 低/高電圧または過温度によるreduced assist
2. SPD004: 電気接続 / harness / network由来の複合症状
3. SPD003: 外部信号または通信validity異常
4. SPD001: 熱保護に近い状態
5. SPD007: DTC履歴とreduced assistの再発監視

この順にした理由は、Bosch型のbusiness outputに近い順である。
SPD002とSPD004は、整備actionとvehicle health outputに直接つながりやすい。
SPD003は、誤交換回避と責任境界に強い。
SPD001は操舵系固有だが、整備actionがやや軽い。
SPD007は予測らしさが強いが、repair feedback loop依存が大きい。

## まだ言ってはいけないこと

次は言ってはいけない。

1. Boschが操舵系EPSのremaining lifetimeやreplacement dateを公開情報で確認済みである
2. EPSサプライヤが単独でfleet predictive maintenance platformを売れる
3. thermal / voltage / communication stateだけで安全保証できる
4. DTC履歴だけで交換時期を予測できる
5. batteryやbrake padのRUL事例をEPSへ直接転用できる

## 次のTask

次はPhase 3を実施する。

各stateについて、次を切る。

1. 必要なDTC
2. 必要なfreeze frame / extended data
3. 必要なlimit state
4. 必要な温度、電源、通信context
5. 必要なrepair feedback loop
6. EPSサプライヤが定義できるもの
7. OEM / fleet / platformなしでは言ってはいけないもの
