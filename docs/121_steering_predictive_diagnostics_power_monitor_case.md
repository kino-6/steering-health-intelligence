# Power Monitor Predictive Value Case

## 結論

power monitorで見るべき1ケースは、**短い電圧dipまたはnear-reset contextが、assist limitation / reduced assistの近傍で繰り返すが、permanent under-voltage DTCには至らないケース**である。

このケースで判断することは、電源原因を当てることではない。
判断することは、既存monitorだけでは残らない可能性があるsoft contextを、EPSがruntimeで観測したpower contextの状態説明として残せるかである。

現時点の結論は、**限定Proceed** である。
ただし、商品化Proceedではない。
既存voltage DTC / reset logで同じ説明ができるなら、この方向はHoldまたはStopに落とす。

詳細表は [data/steering_predictive_diagnostics_power_monitor_case.tsv](../data/steering_predictive_diagnostics_power_monitor_case.tsv) に置く。

## 何を判断しているか

この1ケースでは、次を判断している。

1. 既存monitorで残る情報は何か
2. 既存monitorでは残らない可能性があるsoft contextは何か
3. そのsoft contextは、vehicle health向けの状態説明になるか
4. EPSサプライヤとして、製品価値、診断価値、品質改善価値、顧客技術説明価値のどれに変わるか
5. どこからが原因断定、交換時期予測、安全保証、保証費削減に見えるため禁止か

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
- 診断読み順、追加ログ、品質feedback、顧客説明を最終目的にしていない
- EPS交換時期、RUL、安全保証、root cause、保証費削減を主張していない
- 既存voltage DTC / reset logで十分ならHoldまたはStopにする
- 内部事実不足だけを主Kill理由にせず、既存monitorとの差分と部署成果物への転記で判断する

## Market Demand

市場需要は、EPS交換時期を知ることではない。

実務で困るのは、次のような場面である。

1. reduced assistや警告表示が出たが、permanent under-voltage DTCは残っていない
2. サービス側が、EPS内部故障、車両電源、ハーネス、バッテリー、発電機を短絡的に疑う
3. 品質側が、fieldで同じようなnear-threshold power contextが繰り返しているかを見たい
4. 顧客技術説明で、原因断定せずに「EPSが何を観測したか」を説明したい
5. vehicle health基盤へ、EPS componentから見たpower contextの状態説明を渡したい

この需要に対して、EPSサプライヤが持てる手札は、EPSが観測した電圧、reset context、assist mode、DTC status、key cycle recurrenceである。

## Case Definition

想定する1ケースは次である。

> 低速取り回し中、assist limitationまたはreduced assistが一時的に出る。近傍で短いsupply voltage dipまたはnear-reset contextがあり、同じkey cycleまたは近いkey cycleで再発する。ただし、permanent under-voltage DTCは残っていない。

このケースで見るのは、電源原因ではない。
見るのは、EPS componentが観測したpower contextとassist availabilityの関係である。

## Existing Monitor Comparison

| Item | 既存monitorで残る可能性 | 既存monitorでは残らない可能性 | SPD008で見る意味 |
|---|---|---|---|
| under-voltage DTC | 閾値と継続時間を超えれば残る | 閾値未満または継続時間不足なら残らない | DTC未満の短いdipを状態説明へ使えるか |
| reset log | resetが成立すれば残る | near-resetやreset直前contextは残らない可能性 | resetに至らない不安定さを見られるか |
| power supply fault | hard faultなら残る | transient instabilityは残らない可能性 | hard fault未満の繰り返しを見られるか |
| freeze frame / extended data | DTC発生時のsnapshotとして残る可能性 | DTCが立たないevent近傍は残らない可能性 | assist limitation近傍のpower contextを残せるか |
| assist mode / limit state | DTCやeventに紐づけば残る可能性 | voltage dipとの同時性までは残らない可能性 | power contextとassist availabilityの近接を説明できるか |
| key cycle recurrence | DTC履歴で一部残る可能性 | DTC未満eventの再発頻度は残らない可能性 | 繰り返しを状態説明として扱えるか |

## Minimum Vehicle Health Payload

vehicle healthへ渡すなら、最小payloadは次でよい。

| Field | Meaning |
|---|---|
| component | steering / EPS |
| observed_context | supply-voltage instability observed by EPS |
| event_relation | near assist limitation or reduced assist |
| severity_language | context observed / monitor below hard fault threshold |
| recurrence | same key cycle or recent key cycles |
| confidence | low / medium, depending on retained fields |
| recommended_read | check EPS DTC status, reset context, supply voltage context, assist mode, recurrence |
| boundary | not power root cause, not EPS no-fault, not replacement timing, not safety guarantee |

vehicle health向けの状態説明文は、次にする。

> EPS observed short supply-voltage instability near assist limitation. This is a steering-side power-context observation, below or outside hard fault confirmation, and is not a power root cause decision.

日本語では次である。

> EPSが、assist制限の近傍で短い電源不安定を観測した。これは操舵側から見たpower contextの状態説明であり、hard fault確定や電源原因断定ではない。

## Business Value Check

| Value type | 判断 |
|---|---|
| 製品価値 | 可能性あり。EPSがpower contextに対して、故障断定ではない状態説明を持てることを示せる |
| 診断価値 | 可能性あり。reduced assistをEPS内部故障へ短絡する前に、EPSが観測したpower contextを読む順番を作れる |
| 品質改善価値 | 可能性あり。near-threshold power contextとassist limitationのfield trendを集計できる |
| 顧客技術説明価値 | 可能性あり。電源原因断定を避けながら、EPSが観測した事実を説明できる |
| vehicle health contribution | 可能性あり。ただしroot cause decisionではなくcomponent-side contextとしてだけ渡す |

## Judgment

この1ケースは、**限定Proceed** とする。

理由は、既存monitorとの差分が比較的確認しやすく、EPSサプライヤが観測できる項目も比較的明確だからである。

ただし、価値はまだ仮説である。
次のどちらかが分かれば判断が決まる。

Proceed:

- voltage min/max、dip duration、near-reset、assist mode、key cycle recurrenceのうち、既存DTCやreset logでは十分に残らない項目がある
- その項目を、原因断定なしにvehicle health向け状態説明へ変換できる
- 診断企画、品質改善、顧客技術説明の少なくとも2部署で使い道がある

Hold:

- 既存voltage DTC、reset log、freeze frame / extended dataで、同じ状態説明が十分にできる
- DTC未満eventは残せるが、部署成果物に転記できない
- recurrenceがノイズになり、説明価値より誤解リスクが大きい

Stop:

- power contextが残らない
- 既存monitorで完全に足りる
- 価値説明に、電源原因断定、EPS無罪、交換時期、安全保証、root cause、保証費削減が必要になる

## What Not To Claim

まだ言ってはいけないこと:

> 電源原因が分かる。

> EPSが悪くないと断定できる。

> EPS交換時期が分かる。

> RULが分かる。

> 安全保証ができる。

> 保証費削減につながる。

> root causeを断定できる。

## Next Action

次は、power monitorの確認項目をさらに1段具体化する。

見る項目は次である。

1. under-voltage DTCに残る項目
2. reset logに残る項目
3. freeze frame / extended dataに残る項目
4. assist mode / limit stateと電圧contextの同時性が残るか
5. DTC未満eventのkey cycle recurrenceが残るか
6. 上記が既存資料で十分ならHold / Stop
7. 不足があるなら、minimum vehicle health payloadをsample化する
