# SPD008 First Samples

## 結論

SPD008を次の本線候補として進めるなら、最初にsample化するのは2つでよい。

1. `power monitor`: DTCに至らない短い電圧dipやnear-reset contextが、assist limitationやreduced assistと同時に出る場合
2. `communication input validity`: 外部signalのintermittent invalidやtimeoutが、操舵表示やfallback contextと同時に出る場合

この2つを先に見る理由は、比較条件を切りやすく、診断読み順、品質feedback、顧客説明へ転記しやすいためである。
`motor / inverter response` は伸びしろがあるが、外部操舵負荷を内部異常として誤読しやすいため、最初のsampleからは外す。

詳細表は [data/steering_predictive_diagnostics_spd008_first_samples.tsv](../data/steering_predictive_diagnostics_spd008_first_samples.tsv) に置く。

## 何を判断しているか

判断しているのは、SPD008のruntime deviationを、実際にsampleとして書けるかである。

ここで見るのは、故障判定ではない。
DTC未満または原因未確定のsoft contextを、追加ログ、診断読み順、品質feedback、顧客説明へ転記できるかである。

## Rule Check

今回の判断では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Kaggle / Public Proxy Predictive Value Rule`
5. `Mandatory Rule Check Before Stop / Kill / Archive`

この文書では、Hold / Stop境界を明示するため、次を確認する。

- 市場需要は、故障後ではなく、DTC未満または原因未確定の段階で診断、品質、顧客説明の行動を決めたいことである
- EPS製品全体E2Eではなく、内部重要モジュール単位に限定している
- EPS交換時期、RUL、安全保証、root cause、保証費削減へ戻していない
- 既存monitorで十分かどうかを明示的に見る
- 不足データは、言ってはいけないことを切る境界として扱う
- EPSサプライヤとしての手札を、信号整合、既存monitor、追加ログtrigger、診断読み順、品質feedbackへ限定する

## Market Demand

市場側の需要は、故障が確定してからDTCを読むことだけではない。

実務では、次を早く決めたい。

1. DTC未満のcontextを追加ログとして残すべきか
2. reduced assistや操舵表示の前後で、電源や通信contextをどう読むべきか
3. 品質側へ、同じようなfield patternが繰り返しているかを返せるか
4. 顧客へ、故障断定せずに何を説明できるか

SPD008のfirst samplesは、この需要に対して、power contextとcommunication dependency contextを保存・説明できるかを見る。

## Sample 1: Power Monitor

### 想定event

Assist limitationまたはreduced assistが出た近傍で、短い電圧dipまたはnear-reset contextがある。
ただし、permanent under-voltage DTCは残っていない、またはDTC persistence thresholdには届いていない。

### 捕まえるsoft deviation

- repeated short voltage dips
- near-reset context
- assist limitとの同時性
- key-cycle recurrence

### 既存monitorとの境界

既存のunder/over-voltage DTC、reset monitor、power supply faultで十分なら、SPD008としての追加価値は薄い。

価値が残るのは、hard DTCにはならないが、assist limitationの説明や診断読み順に使えるvoltage contextが残せる場合である。

### 追加ログtrigger

次の組み合わせが繰り返す場合に、extended snapshotとして保存する。

- voltage min/max
- dip duration class
- reset counter delta
- assist mode
- DTC status
- key cycle
- recurrence count

### 診断読み順

1. event summary
2. EPS DTC status
3. voltage dip context
4. assist mode / limit state
5. key-cycle recurrence
6. repair feedback requirement

### 転記先

診断企画:

- reduced assistをEPS内部故障へ短絡する前に、near-threshold voltage contextを読む順番へ入れる

品質改善:

- assist limitationとnear-threshold voltage eventの同時性をfield trendとして見る

顧客技術説明:

- 電源contextがassist availabilityに影響しうるため、EPS component judgment前に電源contextを確認する、と説明する

### 判定

`power monitor` は、SPD008のfirst sampleとしてProceedでよい。

ただし、これは電源原因断定ではない。
EPSが悪くないという断定でもない。
あくまで、診断読み順と説明境界に使うsoft contextである。

## Sample 2: Communication Input Validity

### 想定event

Steering messageまたはassist fallbackが、外部signalのintermittent invalid、timeout、alive counter異常の近傍で出る。
ただし、hard communication DTCが安定して残っているとは限らない。

### 捕まえるsoft deviation

- intermittent invalid flag
- timeout counter increase
- repeated fallback entry
- mismatch between signal validity and steering message

### 既存monitorとの境界

既存のtimeout DTC、bus-off、invalid value DTCで十分なら、追加価値は薄い。

価値が残るのは、hard DTCにはならないが、操舵表示やfallback説明に必要なdependency contextが残せる場合である。

### 追加ログtrigger

次の組み合わせをdependency snapshotとして保存する。

- dependency signal name
- validity status
- timeout / alive counter
- fallback state
- steering message
- related DTC
- key-cycle recurrence

### 診断読み順

1. event summary
2. steering DTC / message
3. dependency signal status
4. timeout / alive counter
5. fallback state
6. related external / network DTC
7. explanation boundary

### 転記先

診断企画:

- 操舵DTCだけでなく、依存signalとfallback contextを読む順番へ入れる

品質改善:

- service confusionや顧客苦情につながるdependency instabilityをfield patternとして見る

顧客技術説明:

- EPS response may depend on external signal validity と説明し、外部ECU root cause断定やEPS無罪断定を避ける

### 判定

`communication input validity` も、SPD008のfirst sampleとしてProceedでよい。

ただし、EPSサプライヤが依存signal、fallback behavior、steering-side effectを定義できない場合はStopである。

## Comparison Of The Two Samples

| Field | Power monitor | Communication input validity |
|---|---|---|
| 初期実証しやすさ | 高い | 中から高い |
| 診断読み順への転記 | 強い | 強い |
| 品質feedback | 中から強い | 中から強い |
| 顧客説明 | 強い | 強い |
| 既存monitor重複リスク | voltage DTC / reset logと重複 | timeout / invalid DTCと重複 |
| Stop境界 | voltage historyが残らない、または既存DTCで十分 | dependency signal / fallbackを定義できない |

## Required Conclusion Fields

| Field | Content |
|---|---|
| Market demand | DTC未満または原因未確定のcontextを、追加ログ、診断読み順、品質feedback、顧客説明へ使いたい |
| Unresolved pain | hard DTCにはならないsoft contextが残らず、後から説明や品質分析に使えない可能性がある |
| Hypothesis | power monitorとcommunication input validityなら、内部モジュール単位でsoft deviationをsample化できる |
| Solution / artifact | SPD008 first samples: power monitor and communication input validity |
| Buyer / user | 診断企画、品質改善、顧客技術説明、製品企画 |
| Why EPS supplier can play | 電源context、依存signal、fallback、assist stateとの関係を定義できる |
| Proceed condition | 既存monitorでは完結しないsoft contextを追加ログや説明境界へ転記できる |
| Hold condition | 既存DTC / reset / timeout monitorで十分、またはsoft contextが保存できない |
| Stop / Kill boundary | 部署成果物へ転記できない、または原因断定・交換時期・安全保証が必要になる |
| What not to claim | 電源原因断定、外部ECU root cause、EPS無罪、交換時期、安全保証、保証費削減 |
| Next action | 2 sampleを診断企画向けの1枚schemaに落とす |
| Confidence | Medium-High |

## Deepened Weak Points

### 既存monitorとの差分

2つのsampleは、どちらも既存monitorとの重複リスクがある。

差分は、DTC判定ではなく、DTC未満またはhard fault未満のcontextを、後から説明・診断・品質feedbackに使えるよう残す点に置く。

### Baseline不安定

power monitorは、voltage band、dip duration、key cycle recurrenceに限定する。
communication input validityは、dependency signal、timeout / alive counter、fallback stateに限定する。

全条件を対象にしない。

### 外部負荷誤読

この2 sampleは、motor / inverter responseより外部操舵負荷の誤読リスクが低い。
そのため、first sampleとして適切である。

## EPSサプライヤとしての言い方

言ってよいこと:

> SPD008のfirst sampleでは、DTC未満のpower contextとcommunication dependency contextを、追加ログ、診断読み順、品質feedback、顧客説明境界へ転記できるかを見る。

まだ言ってはいけないこと:

> power contextから電源原因を断定できる。

> communication contextから外部ECU root causeを断定できる。

> どちらかでEPS交換時期、安全保証、保証費削減が分かる。

## 次のTask

次は、この2 sampleを診断企画向けの1枚schemaへ落とす。

見る項目は次である。

1. trigger condition
2. snapshot fields
3. reading order
4. explanation boundary
5. quality feedback requirement
6. Stop条件
