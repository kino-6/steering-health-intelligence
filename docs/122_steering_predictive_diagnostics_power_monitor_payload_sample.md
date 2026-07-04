# Power Monitor Payload Sample

## 結論

power monitorの次の作業は、既存monitorで残る情報と、残らない可能性があるsoft contextを、同じ表で確認することである。

この確認で見るべき最小項目は5つである。

1. under-voltage DTCに残る項目
2. reset logに残る項目
3. freeze frame / extended dataに残る項目
4. assist mode / limit stateと電圧contextの同時性
5. DTC未満eventのkey cycle recurrence

現時点の判断は、**判定保留付きの限定Proceed** である。
既存monitorでこの5項目が十分に残るなら、SPD008 power monitorは新規価値が薄く、HoldまたはStopへ下げる。
一方、DTC未満の短い電圧dip、near-reset、assist制限との同時性、key cycle recurrenceのいずれかが既存monitorだけでは残らず、原因断定なしに状態説明へ変換できるなら、power monitorは続ける価値がある。

詳細表は [data/steering_predictive_diagnostics_power_monitor_payload_sample.tsv](../data/steering_predictive_diagnostics_power_monitor_payload_sample.tsv) に置く。

## 何を判断しているか

判断しているのは、vehicle health向けに渡すべきpayloadを作れるかではない。
先に判断するのは、payloadを作るだけの差分があるかである。

つまり、次の順で見る。

1. 既存monitorで十分か
2. 不足するsoft contextがあるか
3. それをEPSが観測した状態説明として言えるか
4. その状態説明が、診断、品質、顧客技術説明、vehicle healthのどれに転記できるか
5. 原因断定や交換時期予測に見えないか

## Rule Check

今回の判断では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Kaggle / Public Proxy Predictive Value Rule`
5. `Steering Predictive Diagnostics Value Rule`
6. `Mandatory Rule Check Before Stop / Kill / Archive`

確認結果:

- 市場需要は、故障確定前または原因未確定の段階で、EPSが観測したpower contextを早く知りたいことである
- EPS製品全体E2Eではなく、power monitorという内部重要モジュール単位に限定している
- payload作成を最終目的にしていない
- EPS交換時期、RUL、安全保証、root cause、保証費削減を主張していない
- 既存monitorで十分ならHoldまたはStopにする
- 内部事実不足だけを主Kill理由にせず、既存monitorとの差分と部署成果物への転記で判断する

## Market Demand

市場需要は、車両電源の原因をEPS側で断定することではない。

実務上ほしいのは、次の判断である。

1. reduced assistや警告表示の近傍で、EPSが短い電源不安定を観測していたか
2. そのcontextが既存DTCやreset logだけで後から読めるか
3. 読めないなら、EPS側でどの最小情報を残すべきか
4. その情報を、vehicle health側へ「操舵側power contextの状態説明」として渡せるか

## Retained Field Checklist

| Check item | 見たいこと | 既存monitorで十分な状態 | 差分が残る状態 |
|---|---|---|---|
| under-voltage DTC | DTC閾値、継続時間、発生時電圧、status | 短いdipもDTCまたはextended dataで十分に説明できる | DTCに至らないshort dipがassist制限近傍で消える |
| reset log | reset成立、reset counter、key cycle | near-resetまで含めて文脈が残る | reset未満のnear-reset contextが残らない |
| freeze frame / extended data | voltage、assist mode、DTC status、time / key cycle | DTC未満event近傍でもsnapshotが残る | DTCが立たないためsnapshotが残らない |
| assist mode / limit state | assist limitation、reduced assist、fallback / limit state | voltage contextと同一eventで紐づく | assist制限だけ残り、power contextとの近接が消える |
| key cycle recurrence | 同一key cycleまたは近いkey cycleでの再発 | DTC履歴やevent memoryで再発が見える | DTC未満eventの繰り返しが残らない |

## Minimum Payload Candidate

既存monitorだけでは不足がある場合、vehicle health向けの最小payloadは次に限定する。

| Field | Example value | Purpose |
|---|---|---|
| component | steering / EPS | どの部品側観測かを示す |
| observed_context | short supply-voltage instability observed by EPS | EPSが観測したcontextを示す |
| relation_to_function | near assist limitation / reduced assist | 機能状態との近接を示す |
| monitor_status | below hard fault threshold / no permanent under-voltage DTC | hard fault確定ではないことを示す |
| recurrence | same key cycle / recent key cycles / unknown | 繰り返しか一過性かを示す |
| retained_fields | voltage min/max, dip duration class, reset counter delta, assist mode, DTC status | 判断に使った項目を明示する |
| confidence | low / medium | 断定しないための信頼度表現 |
| recommended_read | EPS DTC status, reset context, supply voltage context, assist mode, recurrence | 次に読む順序を示す |
| boundary | not power root cause, not EPS no-fault, not replacement timing, not safety guarantee | 禁止主張を明示する |

## Vehicle Health State Text

英語での最小表現:

> EPS observed short supply-voltage instability near assist limitation. This is a steering-side power-context observation below hard fault confirmation and is not a power root cause decision.

日本語での最小表現:

> EPSが、assist制限の近傍で短い電源不安定を観測した。これは操舵側から見たpower contextの状態説明であり、hard fault確定や電源原因断定ではない。

この表現で言えること:

- EPSが観測した事実
- assist limitationとの近接
- hard fault確定ではないこと
- 電源原因断定ではないこと

この表現で言えないこと:

- バッテリー、発電機、ハーネス、車両電源制御が原因である
- EPSが悪くない
- EPS交換時期が分かる
- 安全保証ができる
- 保証費削減できる

## Decision Gate

Proceed:

- 5項目のうち少なくとも2項目で、既存monitorだけでは残らないsoft contextがある
- そのsoft contextが、原因断定なしにvehicle health向け状態説明へ変換できる
- 診断企画、品質改善、顧客技術説明のうち2部署以上で使い道がある

Hold:

- soft contextは残るが、部署成果物に転記できるか不明
- 既存monitorとの差分が1項目だけで、誤解リスクが大きい
- recurrenceが残らず、一過性eventとしてしか見えない

Stop:

- 既存monitorで5項目が十分に残る
- DTC未満eventが残らない
- 状態説明にするには、電源原因断定、EPS無罪、交換時期、安全保証、root cause、保証費削減が必要になる

## EPSサプライヤとしての言い方

言ってよいこと:

> EPSが観測した短い電源不安定とassist制限の近接を、hard fault未満のpower contextとして説明できるか確認する。

まだ言ってはいけないこと:

> 電源原因が分かる。

> EPSが悪くない。

> EPS交換時期が分かる。

> 安全保証できる。

> 保証費削減できる。

## 次の作業

次は、このpayload candidateを使って、対象programで確認する質問表を作る。

質問表では、各項目について次を聞く。

1. 既存DTC / reset log / freeze frame / extended dataに残るか
2. DTC未満eventでも残るか
3. assist mode / limit stateと紐づくか
4. key cycle recurrenceが残るか
5. 既存資料だけで状態説明できるならHold / Stop
6. 足りなければ、minimum payloadをsupporting artifactとして残す
