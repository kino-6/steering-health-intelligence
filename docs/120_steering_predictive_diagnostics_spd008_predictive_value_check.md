# SPD008 Predictive Value Check

## 結論

SPD008の次の一手は、診断企画向け資料を作ることではない。

判断することは、EPS内部重要モジュールのruntime contextから、DTC未満または原因未確定の段階で「普段と違う状態」を検知、分類、説明できるかである。
その状態説明が、predictive diagnostics / vehicle healthへ渡せる部品側contributionになり、EPSサプライヤの製品価値、診断価値、品質改善価値、顧客技術説明価値のどれかに変わるなら、SPD008は次の本線候補として残せる。

2サンプルの現時点判断は次である。
ここでいう検証候補は、外販商品化の判断ではない。
固定スコープの内部/顧客技術向けassessmentで、既存monitorとの差分とruntime状態説明価値を確認する順番である。

| Sample | Judgment | Reason |
|---|---|---|
| Power monitor | First validation candidate | EPS側で電圧、reset context、assist limitとの同時性を比較しやすい。既存voltage DTCやreset logで十分かを最初に確認できる |
| Communication input validity | Second validation candidate | vehicle healthへの部品側contributionは見えやすいが、依存signal、network、fallback定義がOEM側に寄るため、初回はpower monitorより依存が強い |

したがって、次に作るべきものは、`power monitor` のpredictive value checkである。
`communication input validity` は同じ形式で続けるが、依存signalとfallback behaviorをEPSサプライヤが定義できる場合に限る。

詳細表は [data/steering_predictive_diagnostics_spd008_predictive_value_check.tsv](../data/steering_predictive_diagnostics_spd008_predictive_value_check.tsv) に置く。

## 何を判断しているか

判断しているのは、2サンプルが「診断に便利」以上の価値になるかである。

診断読み順、追加ログschema、品質feedback、顧客説明は副次artifactである。
本体の問いは、次の4つである。

1. runtimeで何を「普段と違う状態」と見るのか
2. 既存monitorやDTCで十分ではないのか
3. vehicle healthやpredictive diagnosticsに渡せる部品側状態説明になるのか
4. EPSサプライヤとして何を売る、内部実施する、言ってはいけないか

## Rule Check

今回の判断では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Kaggle / Public Proxy Predictive Value Rule`
5. `Steering Predictive Diagnostics Value Rule`
6. `Mandatory Rule Check Before Stop / Kill / Archive`

確認結果:

- 市場需要は、故障確定前または原因未確定の段階で、状態変化を早く知りたいことである
- EPS製品全体E2Eではなく、内部重要モジュール単位に限定している
- 診断読み順、追加ログ、品質feedback、顧客説明を最終目的にしていない
- EPS交換時期、RUL、安全保証、root cause、保証費削減を主張していない
- 既存monitorで十分ならHoldまたはStopにする
- 内部事実不足だけを主Kill理由にせず、価値説明や既存業務との差分で判断する

## Market Demand

市場需要は、EPSが壊れる日を当てることではない。

製品企画、診断企画、品質改善、顧客技術説明、vehicle health基盤側では、次のような状態を早く知りたい。

1. hard DTCにはならないが、通常とは違う電源contextや通信依存contextが繰り返している
2. reduced assistや操舵表示の近傍に、後から説明できるcontextが残っていない
3. service側や顧客側が、EPS内部故障、電源系、外部signal依存を短絡的に混同する
4. vehicle health側へ、EPS componentから見た「状態説明」を渡したいが、故障原因断定や交換時期予測にはしたくない

SPD008が価値を持つのは、このような場面で、EPSサプライヤが部品側で持てるcontextを整理できる場合である。

## Sample 1: Power Monitor

### runtimeで普段と違う状態として見るもの

見るのは、電源原因の断定ではない。
見るのは、EPSが受け取った電源contextとassist availabilityの関係である。

具体的には、次の組み合わせを「普段と違う状態」の候補にする。

1. short voltage dipが繰り返す
2. reset counterやnear-reset contextが動く
3. assist limitationまたはreduced assistの近傍で起きる
4. permanent under-voltage DTCには至っていない
5. 同じkey cycleまたは近いkey cycleで再発する

### 既存monitorとの差分

既存のunder-voltage DTC、over-voltage DTC、reset monitor、power supply faultで、上のcontextが十分に残るなら、SPD008としての差分は小さい。

差分が残るのは、hard fault判定では落ちない短い電圧dipやnear-reset contextが、assist limitationとの同時性として残せる場合である。
この場合、価値は「電源が原因」と言うことではなく、EPS component側から見たpower context sensitivityを説明できることにある。

### vehicle healthへの部品側contribution

vehicle healthへ渡せる可能性があるのは、次のような状態説明である。

> Steering assist availability was limited near repeated short supply-voltage instability observed by the EPS. This is a steering-side power-context observation, not a root cause decision.

日本語で言えば、次である。

> EPSが観測した短い電源不安定とassist制限が近接している。これは操舵側から見た電源contextの状態説明であり、電源原因の断定ではない。

この形なら、vehicle health側は「steering componentが見たpower context」を扱える。
一方で、バッテリー、ハーネス、発電機、車両側電源制御のどれが原因かは言わない。

### 事業上の出力

製品価値:

- 電源contextに対して、EPSがどこまで状態説明を持てるかを製品価値として示せる

診断価値:

- reduced assistをEPS内部故障へ短絡する前に、EPSが観測したpower contextを確認する順番を作れる

品質改善価値:

- fieldで繰り返すnear-threshold power contextとassist limitationの同時性を集計できる

顧客技術説明価値:

- 電源原因断定を避けながら、EPS componentが観測した事実と確認順序を説明できる

### 判断

Power monitorは、SPD008の第一検証候補としてProceedでよい。

ただし、これは外販商品としてProceedという意味ではない。
固定スコープの内部/顧客技術向けassessmentで、既存monitorとの差分と状態説明価値を確認する、という意味である。

Hold条件:

- voltage min/max、dip duration、reset counter、assist mode、key cycle recurrenceが残らない
- 既存voltage DTCやreset logだけで、同じ状態説明が十分にできる
- 電源原因断定なしでは顧客価値を説明できない

Stop条件:

- power contextが部署成果物へ転記できない
- 価値説明に、交換時期、安全保証、root cause、保証費削減が必要になる

## Sample 2: Communication Input Validity

### runtimeで普段と違う状態として見るもの

見るのは、外部ECU root causeの断定ではない。
見るのは、EPSが依存する外部signalのvalidityやtimeout contextと、steering message / fallback behaviorの関係である。

具体的には、次の組み合わせを「普段と違う状態」の候補にする。

1. intermittent invalid flagが出る
2. timeout / alive counterが増える
3. fallback entryが繰り返す
4. steering messageやassist fallbackの近傍で起きる
5. hard communication DTCが安定して残っていない

### 既存monitorとの差分

既存のtimeout DTC、bus-off、invalid value DTCで、依存signal、fallback state、steering-side effectまで十分に残るなら、SPD008としての差分は小さい。

差分が残るのは、hard communication DTCに至らない揺らぎが、EPS側のfallbackや操舵表示と結びつけて説明できる場合である。
この場合、価値は「外部ECUが悪い」と言うことではなく、EPS componentが依存signal validityをどう見て、どの状態に入ったかを説明できることにある。

### vehicle healthへの部品側contribution

vehicle healthへ渡せる可能性があるのは、次のような状態説明である。

> Steering function entered or approached fallback context while EPS-observed dependency signal validity was unstable. This is a steering-side dependency observation, not an external ECU root cause decision.

日本語で言えば、次である。

> EPSが観測した依存signalのvalidityが不安定な近傍で、操舵機能がfallback contextに入った、または近づいた。これは操舵側から見た依存関係の状態説明であり、外部ECU原因の断定ではない。

この形なら、vehicle health側は「steering componentが見たdependency context」を扱える。
一方で、外部ECU、通信bus、gateway、network負荷、上位制御のどれが原因かは言わない。

### 事業上の出力

製品価値:

- by-wire / motion-domain時代に、操舵機能が外部signal依存をどう扱うかをcomponent boundaryとして説明できる

診断価値:

- 操舵DTCだけでなく、依存signal validity、timeout / alive counter、fallback stateを読む必要性を示せる

品質改善価値:

- service confusionや顧客苦情につながるdependency instability patternを整理できる

顧客技術説明価値:

- EPS単独故障にも外部ECU原因にも短絡せず、操舵側で観測した依存contextを説明できる

### 判断

Communication input validityは、SPD008の第二検証候補としてProceed寄りのHoldである。

power monitorよりvehicle healthらしさは強い。
一方で、依存signal、fallback behavior、steering-side effectの定義がOEM programや車両architectureに寄るため、EPSサプライヤ単独で一般化しにくい。

Proceed条件:

- EPSサプライヤが、依存signal、validity status、timeout / alive counter、fallback state、steering-side effectを定義できる
- 既存communication DTCでは残らないdependency contextがある
- vehicle health側へ、外部原因断定なしの部品側状態説明として渡せる

Hold条件:

- dependency signal listやfallback stateがOEM側に閉じている
- 既存communication DTCとservice manualで十分に説明できる
- EPS component側の状態説明ではなく、network root cause調査になってしまう

Stop条件:

- EPSサプライヤが依存signal、fallback behavior、steering-side effectを定義できない
- 価値説明に、外部ECU root cause、保証責任、交換時期、安全保証が必要になる

## Comparison

| Field | Power monitor | Communication input validity |
|---|---|---|
| 最初に検証する順番 | 1 | 2 |
| runtime状態説明 | EPSが観測したpower contextとassist availabilityの関係 | EPSが観測したdependency signal validityとfallback contextの関係 |
| 既存monitorとの差分 | short dip / near-reset / recurrenceがDTC未満で残るか | intermittent invalid / timeout / fallback近傍がDTC未満で残るか |
| vehicle health fit | 中。power context observationとして使える | 中から強。dependency context observationとして使える |
| EPSサプライヤの支配範囲 | 比較的強い。EPS supply, reset, assist modeを持ちやすい | 中。依存signalやfallback定義がOEM architectureへ寄る |
| 初期買い手 / 利用部署 | 診断企画、品質改善、顧客技術説明、製品企画 | 製品企画、診断企画、顧客技術説明、品質改善 |
| 最大リスク | 既存voltage DTC / reset logで十分 | OEM/network領域に入りすぎる |
| 判断 | First validation candidate | Second validation candidate / Proceed-leaning Hold |

## Required Conclusion Fields

| Field | Content |
|---|---|
| Market demand | 故障確定前または原因未確定の段階で、EPS内部重要モジュールが普段と違う状態に入りつつあるかを知りたい |
| Unresolved pain | hard DTCやservice manualだけでは、短いpower contextやintermittent dependency contextが状態説明として残らない可能性がある |
| Hypothesis | power monitorとcommunication input validityなら、DTC未満のcontextをruntime状態説明として扱い、vehicle healthへの部品側contributionにできる可能性がある |
| Solution / artifact | SPD008 predictive value check and supporting artifact list |
| Buyer / user | 製品企画、診断企画、品質改善、顧客技術説明。vehicle health platform側は初期買い手ではなく接続先 |
| Why EPS supplier can play | EPSが観測するpower context、dependency validity、fallback state、assist mode、既存monitor、設計上の期待応答を定義できる |
| Proceed condition | 既存monitorとの差分があり、原因断定なしにruntime状態説明として部署成果物またはvehicle healthへ渡せる |
| Hold condition | 必要contextが残らない、既存monitorで十分、またはOEM architecture依存が強い |
| Stop / Kill boundary | 部署成果物へ転記できない、または交換時期、安全保証、root cause、保証費削減、外乱原因断定が必要になる |
| What not to claim | EPS RUL、交換時期、故障発生時期、安全保証、root cause、保証費削減、EPS無罪、外部ECU原因断定 |
| Next action | power monitorの1ケースについて、既存monitorで残る項目と残らない項目を比較し、vehicle health向け状態説明文とsupporting artifact listを作る |
| Confidence | Medium |

## CoVe: 検証で修正した点

初期案では、2サンプルとも同じ強さでProceedに見えた。
しかし、検証すると違いがある。

Power monitorは、EPSサプライヤが観測できる電源context、reset context、assist modeを比較的持ちやすいため、第一検証に向く。
ただし、既存voltage DTCやreset logで十分なら価値は消える。

Communication input validityは、vehicle healthに近いが、依存signalやfallback behaviorがOEM architectureへ寄る。
したがって、第二検証候補またはProceed寄りのHoldに置く。

## Supporting Artifact List

価値仮説を検証するためにだけ、次の副次artifactを作る。

Power monitor:

- trigger condition: short voltage dip / near-reset / assist limitation co-occurrence / recurrence
- snapshot fields: voltage min/max, dip duration class, reset counter delta, assist mode, DTC status, key cycle, recurrence count
- explanation boundary: EPS observed power context; no power root cause decision
- quality feedback: recurrence after power-system inspection or repair, assist limitation recurrence

Communication input validity:

- trigger condition: intermittent invalid / timeout / alive counter increase / fallback context
- snapshot fields: dependency signal name, validity status, timeout / alive counter, fallback state, steering message, related DTC, key cycle recurrence
- explanation boundary: EPS observed dependency context; no external ECU root cause decision
- quality feedback: recurrence after network / external ECU inspection, service confusion pattern

## 次の作業

次は、power monitorを1ケースだけさらに具体化する。

見る項目は次である。

1. 既存monitorで残る項目
2. 既存monitorでは残らない可能性がある項目
3. runtime状態説明文
4. vehicle healthへ渡す場合の最小payload
5. EPSサプライヤとして言ってよいこと
6. 言ってはいけないこと
7. Hold / Stop条件
