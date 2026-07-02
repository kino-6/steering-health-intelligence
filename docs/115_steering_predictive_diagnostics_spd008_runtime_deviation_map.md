# SPD008 Internal Module Runtime Deviation Map

## 結論

SPD008は、次の本線候補として残す価値がある。

ただし、狙うのは「EPS製品全体のE2E挙動から、外乱込みで普段と違う状態を当てること」ではない。
それでは、路面、タイヤ、運転者、アライメント、積載、温度、電源、外部ECU signalが混ざりすぎる。

狙うべきものは、EPS内部の重要モジュールごとに、規定範囲内だが自己履歴、標準範囲、信号間整合からズレる状態を見つけ、それを追加ログ、診断読み順、品質feedback、顧客説明境界へ転記できるかである。

今回のmapでは、5つの内部モジュールを見た。

1. torque / angle sensor plausibility
2. motor / inverter response
3. power monitor
4. thermal derating
5. communication input validity

一定の結論としては、SPD008は **Proceed to concept artifact** である。
ただし、最初から商品化や故障予測へ進める段階ではない。
次に確認すべきことは、既存diagnostic monitorで十分なのか、それともDTC未満のdeviationを追加ログや品質feedbackに残す価値があるのかである。

詳細表は [data/steering_predictive_diagnostics_spd008_runtime_deviation_map.tsv](../data/steering_predictive_diagnostics_spd008_runtime_deviation_map.tsv) に置く。

## 何を判断しているか

判断しているのは、EPS内部モジュールのruntime deviationが、EPSサプライヤの業務成果物へ転記できるかである。

ここでいうruntime deviationは、故障ではない。
規定範囲内で、まだDTCにも至らないが、通常パターンや信号間整合から見て「残しておくと診断・品質・説明に役立つ可能性がある状態」である。

## Rule Check

今回の判断では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Kaggle / Public Proxy Predictive Value Rule`
5. `Mandatory Rule Check Before Stop / Kill / Archive`

この文書では、Hold / Stop境界を明示するため、次を確認する。

- 市場需要は、故障後ではなく、DTC未満または原因未確定の段階で、診断、品質、顧客説明の行動を決めたいことである
- EPS製品全体E2Eではなく、内部重要モジュール単位に限定している
- EPS交換時期、RUL、安全保証、root cause、保証費削減へ戻していない
- EPS内部状態が見えるからといって、故障時期や交換時期を言っていない
- 不足データは、言ってはいけないことを切る境界として扱っている
- EPSサプライヤとしての手札を、内部モジュール、信号整合、既存monitor、追加ログtrigger、品質feedbackへ限定している

## Market Demand

市場側の需要は、故障が確定してからDTCを読むことだけではない。

実務では、DTCが出ていない、またはDTCが出ても原因を断定できない段階で、次を決めたい。

1. 何を追加でログ保存すべきか
2. どの順番で診断情報を読むべきか
3. 品質側へどのfield patternを戻すべきか
4. 顧客へ、故障と断定せずに何を説明できるか

SPD008は、この需要に対して、DTC未満のdeviationを追加ログや説明境界へ転記できるかを見る。

## Unresolved Pain

既存diagnostic monitorは、基本的には安全・故障検出の閾値を持つ。
一方で、現場や品質側が困るのは、その閾値に達していないが、あとから見返すと「普段と違う」状態だった可能性がある場合である。

ただし、この発想には大きなリスクがある。
EPS全体のE2E挙動で見れば、外乱が多すぎる。
したがって、SPD008は内部モジュール単位に限定し、既存monitorとの差分がある場合だけ残す。

## Hypothesis

EPS内部の重要モジュールについて、規定範囲内だが通常と違う信号関係を、DTC未満の追加ログtriggerとして定義できれば、診断企画、品質改善、顧客技術説明に価値が残る。

この仮説は、故障時期や交換時期を当てるものではない。
価値は、後から説明・診断・品質feedbackに使える状態を、消える前に残すことである。

## Module Map

| Module | Initial judgment | Why |
|---|---|---|
| power monitor | strongest near-term | voltage dipやnear-reset contextはreduced assistの診断読み順に直結しやすい |
| communication input validity | strong practical | 外部signal依存とfallback contextを説明境界へ転記しやすい |
| thermal derating | useful but overlap risk | thermal protection説明と重複しやすいが、margin/recovery履歴は使える可能性がある |
| torque / angle sensor plausibility | possible but monitor overlap risk | hard plausibility monitorと重複しやすい。DTC未満trendが品質feedbackになるかが鍵 |
| motor / inverter response | high value but hardest | 機能価値に近いが、外部負荷の影響を誤読しやすい |

## 1. Torque / Angle Sensor Plausibility

見るもの:

- driver torque sensor
- steering angle sensor
- motor angle or rack position proxy
- plausibility residual
- offset trend
- noise / drift indicator

既存monitor:

- range check
- dual sensor plausibility
- stuck / open / short
- hard DTC threshold

deviation候補:

- 規定範囲内のoffset drift
- noise increase
- intermittent mismatch below DTC threshold
- temperature-correlated residual growth

追加価値:

- DTC未満のsensor disagreementを追加ログとして残せれば、品質feedbackや再発監視に使える可能性がある

弱点:

- safety-relevantなplausibilityは既存monitorがすでに厚い可能性が高い
- trendが安定しないと、追加ログがノイズになる

判定:

- **Hold unless trend changes diagnostic or quality action**

## 2. Motor / Inverter Response

見るもの:

- assist command
- phase current
- DC bus voltage
- rotor position
- motor speed
- temperature
- current response
- response delay
- current ripple

既存monitor:

- current limit
- over-current
- over/under-voltage
- phase fault
- thermal protection
- control error hard threshold

deviation候補:

- 同じcommand bandで必要currentが増える
- response delay
- ripple increase
- temperature-sensitive response shift

追加価値:

- 既存DTCより前に、command-response marginの変化を追加ログとして残せれば、機能価値に近い

弱点:

- 外部操舵負荷の影響を受けやすい
- 比較条件をそろえられないと、内部deviationではなく外乱を読んでしまう

判定:

- **Promising but hardest**

## 3. Power Monitor

見るもの:

- ECU supply voltage
- DC bus voltage
- reset counter
- voltage dip duration
- assist command during dip

既存monitor:

- under/over-voltage DTC
- reset detection
- power supply fault
- brownout protection

deviation候補:

- repeated short voltage dips near assist limitation
- transient voltage instability below DTC persistence threshold
- near-reset context with reduced assist

追加価値:

- 電圧contextを追加ログに残せれば、reduced assistをEPS内部故障と短絡しない診断読み順に直結する

弱点:

- voltage DTCやreset logで十分な場合は差分が小さい

判定:

- **Strongest near-term module**

## 4. Thermal Derating

見るもの:

- motor temperature
- inverter temperature
- ECU temperature
- estimated winding temperature
- assist limit state
- cool-down behavior

既存monitor:

- over-temperature DTC
- thermal protection threshold
- assist limit state
- recovery after cool-down

deviation候補:

- comparable demandでtemperature riseが早い
- repeated near-derating
- slow recovery
- frequent soft limit entry

追加価値:

- margin / recovery historyを残せれば、顧客説明、評価feedback、不要交換回避に使える

弱点:

- thermal protection説明の焼き直しになりやすい
- 寿命や交換時期を言いたくなるが、そこは言えない

判定:

- **Useful if margin and recovery history differ from existing monitor**

## 5. Communication Input Validity

見るもの:

- external signal validity
- timeout
- counter
- alive signal
- vehicle speed / yaw / ADAS request validity
- fallback state

既存monitor:

- timeout DTC
- bus-off
- invalid value DTC
- signal substitution / fallback
- communication fault threshold

deviation候補:

- intermittent invalid
- delayed update
- repeated fallback entry
- mismatch between signal validity and steering message

追加価値:

- dependency signal statusとfallback contextを保存できれば、外部signal異常とEPS内部故障を混同しない説明に使える

弱点:

- signal dependencyをEPSサプライヤが定義できない場合は進まない

判定:

- **Strong practical module**

## Proceed / Hold / Stop

Proceed条件:

- 少なくとも2モジュールで、既存monitorだけでは完結しないdeviationがある
- そのdeviationが、追加ログtrigger、診断読み順、品質feedback、顧客説明のどれかに転記できる
- E2E外乱推定ではなく、内部モジュール単位で説明できる

Hold条件:

- 既存diagnostic monitorで十分である
- baselineが安定しない
- 外部負荷を内部異常として誤読する
- 追加ログを残しても使う部署がない

Stop境界:

- 内部モジュール単位に限定しても、診断企画、品質改善、顧客技術説明のどれにも転記できない
- 価値説明に、故障時期、交換時期、安全保証、root cause断定が必要になる

## Required Conclusion Fields

| Field | Content |
|---|---|
| Market demand | DTC未満または原因未確定の段階で、追加ログ、診断読み順、品質feedback、顧客説明を決めたい |
| Unresolved pain | E2Eでは外乱が多く、既存monitorだけでは後から説明に使うsoft contextが残らない可能性がある |
| Hypothesis | 内部重要モジュール単位なら、規定範囲内deviationを追加ログや品質feedbackへ転記できる |
| Solution / artifact | internal module runtime deviation map |
| Buyer / user | 診断企画、製品企画、品質改善、顧客技術説明 |
| Why EPS supplier can play | 内部モジュール、信号整合、既存monitor、追加ログtriggerを定義できる |
| Proceed condition | 2モジュール以上で既存monitorとの差分があり、成果物へ転記できる |
| Hold condition | 既存monitorで十分、baseline不安定、外部負荷誤読 |
| Stop / Kill boundary | 部署成果物へ転記できない、または交換時期/安全保証/原因断定が必要になる |
| What not to claim | 故障時期、交換時期、外乱原因特定、安全保証、root cause |
| Next action | power monitorとcommunication input validityを先にsample化する |
| Confidence | Medium |

## Deepened Weak Points

### 既存monitorとの差分

SPD008の最大リスクは、既存monitorで十分であることだ。

差分が出る可能性があるのは、hard DTC thresholdではなく、DTC未満のsoft contextを後から説明や品質feedbackに使う場合である。
したがって、追加ログtriggerは「故障判定」ではなく「説明・診断・品質のための保存条件」として定義する。

### Baseline不安定

自己履歴や標準範囲は、温度、電源、走行条件、calibration、車両側入力で変わる。
そのため、最初から全条件を対象にしない。
power monitorとcommunication input validityのように、比較条件を比較的切りやすいモジュールから始める。

### 外部負荷誤読

motor / inverter responseは魅力があるが、外部操舵負荷を内部異常として誤読しやすい。
このため、最初のsampleでは本命扱いにせず、hardest candidateとして残す。

### 部署成果物への転記

転記先は次である。

- 診断企画: DTC未満のsoft contextを読む順番
- 品質改善: field patternとして残すログ条件
- 顧客技術説明: 故障断定ではなく、追加観察が必要な状態として説明する境界
- 製品企画: 次世代EPSで残すべきsoft context候補

## EPSサプライヤとしての言い方

言ってよいこと:

> EPS内部の重要モジュールについて、DTC未満だが通常と異なる信号関係を、追加ログ、診断読み順、品質feedback、顧客説明境界へ転記できるかを見る。

まだ言ってはいけないこと:

> runtime deviationから故障時期、交換時期、root cause、安全保証が分かる。
