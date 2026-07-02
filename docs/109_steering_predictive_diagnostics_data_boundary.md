# Steering Predictive Diagnostics Data Boundary

## 結論

Phase 3では、Proceed候補5件について、必要データと権限境界を切った。

結論は、操舵系predictive diagnosticsはまだ残る。
ただし、EPSサプライヤ単独で言える範囲は、主に「操舵系stateの意味」「診断読み順」「EPS内部故障と外部contextを混同しない説明境界」「言ってはいけないこと」である。

RUL、交換時期、failure prediction、保証費削減、安全保証へ進むには、修理結果、再発有無、車両全体ログ、service workflow、fleet/OEM feedback loopが必要になる。
したがって、Phase 3時点では、`steering predictive diagnostics data boundary` としてはProceedできるが、`steering remaining lifetime / replacement date prediction` としてはProceedしない。

データ境界表は [data/steering_predictive_diagnostics_data_boundary.tsv](../data/steering_predictive_diagnostics_data_boundary.tsv) に置く。

## 何を判断しているか

判断しているのは、Proceed候補が「どのデータがあれば説明できるのか」と「どこから先はOEM/fleet/platformなしでは言ってはいけないのか」である。

対象は次の5件である。

1. SPD002: 低/高電圧または過温度によるreduced assist
2. SPD004: 電気接続 / harness / network由来の複合症状
3. SPD003: 外部信号または通信validity異常
4. SPD001: 熱保護に近い状態
5. SPD007: DTC履歴とreduced assistの再発監視

## Rule Check

今回の判断では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Kaggle / Public Proxy Predictive Value Rule`
5. `Mandatory Rule Check Before Stop / Kill / Archive`

この文書では、Stop / Kill / Archiveを主結論にしていない。
ただし、各stateで言ってはいけないことを切るため、次を確認する。

- 市場需要は、停止前または問題拡大前に整備・診断・説明行動を決めたいことである
- Boschの予測語は正面から扱う
- EPS内部状態やrepair feedbackが公開されていないことだけで候補を落とさない
- 不足データは、RUL、交換時期、安全保証、root cause断定を禁止する境界として扱う
- EPSサプライヤの手札は、state定義、診断意味、説明境界、禁止主張、必要データ定義である

## Phase 3で分かったこと

### 1. SPD002は最初にdata boundaryを作る価値がある

低/高電圧または過温度によるreduced assistは、必要データが比較的はっきりしている。

必要なのは、電圧、温度、reduced assist / manual mode、key cycle継続、DTC / freeze frame / extended dataである。
EPSサプライヤは、電源系や充電系の修理結果を持たない可能性が高い。
しかし、操舵系が電源・温度contextでどう制限され、EPS内部故障とどう区別すべきかは定義できる。

言えること:

> Voltage or thermal context may affect steering assist; inspect power/thermal context before EPS component judgment.

言ってはいけないこと:

> 電圧や過温度の履歴だけで、EPS remaining lifetimeやreplacement dateが分かる。

### 2. SPD004はvehicle healthに近いが、車両全体データが必要

電気接続 / harness / network由来の複合症状は、Bosch型のvehicle healthやcloud diagnosticsに近い。
理由は、操舵assist低下を単独で見ず、複数ECU症状、電源event、harness点検結果、network DTCと束ねるからである。

EPSサプライヤが持てる価値は、EPS交換前に何を疑うべきかの境界説明である。
ただし、車両全体ログ、複数ECU DTC、修理結果なしでは、component localizationやroot causeは言えない。

言えること:

> Steering symptom appears with vehicle-level electrical/network compound symptoms; prioritize power/harness/network diagnosis before steering replacement.

言ってはいけないこと:

> 複合症状があるので、EPSが原因ではない / harnessが原因である、と断定する。

### 3. SPD003は誤交換回避と責任境界に強い

外部信号または通信validity異常は、EPS内部故障ではない。
しかし、操舵表示やassist説明へ影響するため、diagnostic triageとして強い。

EPSサプライヤは、操舵系が依存する外部signal、そのsignalがinvalidになった場合の表示やassist影響、EPS内部故障と外部signal異常の境界を定義できる可能性がある。

言えること:

> Steering assist message may be driven by external signal validity; validate external ECU/signal context before steering component judgment.

言ってはいけないこと:

> 外部信号異常が見えたので、EPS側には問題がない / 外部ECUがroot causeである、と断定する。

### 4. SPD001は操舵系固有だが、整備actionは軽い

熱保護に近い状態は、操舵系固有性が強い。
操舵角反復、motor current、温度、assist limit、thermal protectionは、component-specific load featureとして説明しやすい。

一方で、整備actionは冷却、復帰確認、再発条件確認、使用条件確認、不要交換回避が中心である。
このため、maintenance forecastよりも、説明・診断・誤交換回避に向く。

言えること:

> Steering load and thermal protection context observed; verify cooling/recovery and recurrence before component replacement.

言ってはいけないこと:

> 熱保護に近い状態があるので、部品寿命が短い / 交換時期が近い。

### 5. SPD007は予測らしさが強いが、feedback loop依存が最大

DTC履歴とreduced assistの再発監視は、maintenance forecastに最も近づく可能性がある。
ただし、DTC履歴、発生頻度、再発間隔だけでは危険である。

修理結果、再発有無、部品交換有無、作業時間、service feedback loopがないと、DTC履歴を交換時期予測へ短絡しやすい。

言えること:

> Reduced assist recurrence pattern can be monitored; connect recurrence and service outcome before maintenance forecast.

言ってはいけないこと:

> DTC履歴だけで交換時期や故障発生時期が分かる。

## Data Boundary Summary

| State | EPSサプライヤが定義できること | OEM/fleet/platformなしでは言えないこと | Phase 3判定 |
|---|---|---|---|
| SPD002 | 電源・温度contextとassist制限の意味、診断読み順 | 修理結果、key cycle継続、fleet運行可否、RUL | Proceed to one-case reading order |
| SPD004 | EPS交換前の電源/harness/network確認境界 | 車両全体root cause、component localization、保証責任 | Proceed to fault grouping map |
| SPD003 | 外部signal依存、invalid時の操舵説明境界 | 外部ECU root cause、責任部署断定、修理結果 | Proceed to signal dependency table |
| SPD001 | thermal protectionの意味、正常保護と故障の境界 | 実使用条件断定、寿命、交換時期 | Proceed to explanation template |
| SPD007 | DTC履歴の読み方、再発監視の境界 | maintenance forecast、RUL、交換時期、保証費削減 | Proceed only with feedback dependency |

## CoVe

| 検証質問 | 回答 | Confidence | 反映 |
|---|---|---:|---|
| 必要データはEPSサプライヤ単独で揃うか | No。DTCや診断意味は定義できるが、修理結果や車両全体eventはOEM/fleet/platform依存である。 | High | data boundaryに分離 |
| それでもProceed候補は残るか | Yes。RULではなく、診断読み順、vehicle health説明、誤交換回避、必要データ定義として残る。 | Medium-High | Phase 3判定に反映 |
| SPD002は最初に進めるべきか | Yes。必要データと整備actionが最も具体的である。 | Medium-High | 次artifactの優先順位1位 |
| SPD007はProceedか | Conditional。feedback loopがある場合だけmaintenance forecast候補。なければHold。 | Medium | dependency扱い |
| 内部事実不足をKill理由にしていないか | していない。不足はRUL/交換時期/原因断定を禁止する境界として扱った。 | High | Rule Checkに反映 |

## EPSサプライヤとしての言い方

言ってよいこと:

> EPSサプライヤは、操舵系stateごとに、DTC、freeze frame、extended data、limit state、温度、電源、通信contextのどれが必要かを定義できる可能性がある。これにより、EPS内部故障と外部contextを混同しない診断読み順やvehicle health説明を作れる。

まだ言ってはいけないこと:

> EPSサプライヤ単独で、Bosch型のremaining lifetime、replacement date、failure prediction、fleet operation decisionを出せる。

## 次のTask

次はPhase 4へ進む。

Phase 4では、今回のdata boundaryを、EPSサプライヤ内の部署別成果物へ転記できるかを見る。
最初に見る部署は、診断企画、品質改善、顧客技術説明、service / aftermarket連携でよい。
