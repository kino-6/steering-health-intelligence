# SPD008 vs SPD002 Decision

## 結論

SPD008とSPD002を比較すると、次の本線候補として強いのはSPD008である。

理由は、SPD008が既存DTC表やservice manualの整理を超えて、EPS製品側の機能価値に近づく可能性を持つためである。
内部重要モジュール単位で、規定範囲内だが通常と違う状態をruntimeで検知、分類、説明できれば、predictive diagnostics / vehicle healthらしい付加価値になる。
追加ログ、診断読み順、品質feedback、顧客説明境界は、その価値を検証するための副次artifactであり、最終目的ではない。

一方で、SPD002は最初の実証demoとして強い。
低/高電圧または過温度によるreduced assistの1ケースを使えば、固定スコープassessmentが既存service manualやDTC表の要約を超えるかを早く確認できる。

したがって、次の扱いはこうする。

- `SPD008`: 次の本線候補として、sample化する
- `SPD002`: 比較用のreference demoとして使う

比較表は [data/steering_predictive_diagnostics_spd008_vs_spd002_decision.tsv](../data/steering_predictive_diagnostics_spd008_vs_spd002_decision.tsv) に置く。

## 何を判断しているか

判断しているのは、次の作業をどちらに寄せるべきかである。

ここでいう本線候補は、EPS交換時期予測ではない。
EPSサプライヤが、診断、品質、製品企画、顧客技術説明へ転記できる予測的付加価値を作れるか、という意味である。

## Rule Check

今回の判断では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Kaggle / Public Proxy Predictive Value Rule`
5. `Steering Predictive Diagnostics Value Rule`
6. `Mandatory Rule Check Before Stop / Kill / Archive`

この文書では、Hold / Stop / Kill境界を比較するため、次を確認する。

- 市場需要から始めている
- 自然言語で、誰のどの業務の話かを説明している
- EPSサプライヤとして売る / 実施する / 言ってはいけないことに戻している
- EPS交換時期、RUL、安全保証、root cause、保証費削減へ戻していない
- 診断読み順、追加ログ、品質feedback、顧客説明を最終目的にしていない
- 不足データは、言ってはいけないことを切る境界として扱っている
- 具体的な次アクションとStop境界を残している

## Market Demand

市場側の需要は、故障が確定してからDTCを読むことだけではない。

実務では、DTC未満または原因未確定の段階で、次を決めたい。

1. EPSが通常と違う状態に入りつつあるかを、内部重要モジュール単位で早く見分けたい
2. その違いが、既存DTCやservice manualだけでは残らない情報かを判断したい
3. vehicle healthやpredictive diagnosticsに渡せる部品側の状態説明へ変換したい
4. 必要に応じて、追加ログ、診断読み順、品質feedback、顧客説明境界へ転記したい

SPD008は、この需要に対してruntime状態検知と部品側の状態説明に寄る。
SPD002は、既に起きたreduced assist eventの診断読み順に寄る。

## Comparison

| Field | SPD008 | SPD002 | Decision |
|---|---|---|---|
| 伸びしろ | 高い。内部重要モジュールのruntime状態検知を、predictive diagnostics / vehicle healthの部品側contributionへ展開できる可能性がある | 中程度。診断読み順assessmentとして有効 | SPD008 |
| 実証しやすさ | 中から低。既存monitorとの差分確認が必要 | 高い。1ケースで読み順を作れる | SPD002 |
| 既存業務との差分 | 既存monitorとの差分が出れば大きい | service manualの要約になるリスクあり | SPD008優位だが未検証 |
| EPSサプライヤの手札 | 内部モジュール、信号整合、monitor、追加ログtrigger | assist limit、DTC、freeze frame、電圧/温度context | 両方あり |
| OEM/fleet/platform依存 | field outcomeには依存するが内部mapはsupplier側で作れる | repair feedbackや電源系修理結果は依存 | 同程度 |
| 初期利用部署 | 診断企画、製品企画、品質改善、顧客技術説明 | 診断企画、service、顧客技術説明 | SPD008の方が広い |
| 禁止主張 | 故障時期、交換時期、外乱原因特定、安全保証、root cause | RUL、交換日、安全保証、root cause、保証費削減 | 共通 |

## Deepened Weak Points

### SPD008: 既存monitorとの差分

SPD008の最大リスクは、既存diagnostic monitorで十分だと分かることである。

その場合、runtime deviation mapは新規価値ではなく、既存monitor一覧の整形になる。
このリスクを避けるため、次作業では「既存monitorでは故障判定しないが、runtimeで普段と違う状態として検知、分類、説明する価値があるsoft context」があるかを見る。

最初に見るべきmoduleは、power monitorとcommunication input validityである。
理由は、比較条件が比較的切りやすく、既存monitorとの差分、状態説明、vehicle healthへの部品側contributionを検証しやすいためである。

### SPD008: Baseline不安定

runtime deviationはbaselineが不安定だと成立しない。
温度、電源、車両側入力、calibration、使用条件で通常範囲が変わるためである。

したがって、最初から全条件を対象にしない。
同じvoltage band、temperature band、signal source、fallback stateのように、比較条件を限定してsample化する。

### SPD008: 外部負荷誤読

motor / inverter responseは魅力があるが、外部操舵負荷を内部異常として誤読しやすい。
このため、最初のsampleでは本線の中心に置かず、hardest moduleとして残す。

### SPD002: 既存service manualとの差分

SPD002の最大リスクは、「電源と温度を確認」の言い換えで終わることである。

差分は、event summary、DTC status、voltage、temperature、assist mode、key cycle、repair feedback requirementを読む順番としてつなげることにある。
この順番が作れないなら、SPD002はreference demoとしても弱い。

### SPD002: 診断情報に残る項目

SPD002は、電圧、温度、assist modeが残らない場合に弱い。
この場合、service noteや顧客説明に転記できる情報が薄くなる。

## Required Conclusion Fields

| Field | SPD008 | SPD002 |
|---|---|---|
| Market demand | 故障確定前または原因未確定の段階で、EPS内部重要モジュールが普段と違う状態に入りつつあるかを見たい | reduced assist eventをDTCだけで判断せず、電源・温度・assist stateと合わせて読みたい |
| Unresolved pain | 既存monitorだけでは説明用contextが残らない可能性がある | 読む順番が弱いと既存資料の断片になる |
| Hypothesis | 内部重要モジュール単位なら、規定範囲内deviationを価値へ転記できる | 1ケース読み順なら、既存DTC表を超える説明境界が作れる |
| Solution / artifact | internal module runtime deviation value map | one-case diagnostic reading order |
| Buyer / user | 診断企画、製品企画、品質改善、顧客技術説明 | 診断企画、service / aftermarket、顧客技術説明 |
| Why EPS supplier can play | 内部モジュールと既存monitorを定義できる | assist limitとDTC/freeze frame/extended dataを説明できる |
| Proceed condition | 2モジュール以上で既存monitorとの差分があり、成果物へ転記できる | 読む順番が具体化し、2部署以上に転記できる |
| Hold condition | 既存monitorで十分、baseline不安定、外部負荷誤読 | service manualの言い換え、診断情報不足 |
| Stop / Kill boundary | 部署成果物へ転記できない、または交換時期/安全保証/原因断定が必要になる | 電圧、温度、assist modeが残らず説明境界も作れない |
| What not to claim | 故障時期、交換時期、外乱原因特定、安全保証、root cause | RUL、交換日、安全保証、root cause、保証費削減 |
| Next action | power monitorとcommunication input validityで、runtime状態検知、既存monitorとの差分、vehicle healthへの部品側contributionを検証する | reference demoとして使う |
| Confidence | Medium | Medium-High |

## Final Decision

最終判断:

> SPD008を次の本線候補に置き、SPD002をreference demoに置く。

理由:

- SPD008は伸びしろが大きく、製品企画・品質改善にも広がる
- SPD002は実証しやすく、診断企画・serviceに説明しやすい
- ただし、SPD002だけでは既存service manual要約に近づきやすい
- SPD008は未検証なので、最初にpower monitorとcommunication input validityのsampleから始める

## Stop / Continue Judgment

Continueする。

ただし、次にやることは無制限な追加調査ではない。
次の最小作業は、SPD008のsampleを「診断資料」ではなく、predictive diagnostics / vehicle healthの価値仮説として洗い直すことである。

1. power monitor runtime deviation sample
2. communication input validity runtime deviation sample

見る項目は、runtimeで普段と違う状態を検知・分類できるか、既存monitorとの差分があるか、EPSサプライヤの製品価値・診断価値・品質改善価値・顧客技術説明価値・vehicle healthへの部品側contributionのどれに転記できるかである。
診断読み順や追加ログschemaは、この検証に必要な場合だけ副次artifactとして作る。

SPD002は、比較用のreference demoとして残す。
SPD008でpredictive diagnostics / vehicle healthとしての差分が出なければ、SPD002型のdiagnostic reading order assessmentへ戻す。

## EPSサプライヤとしての言い方

言ってよいこと:

> 次の本線候補は、内部重要モジュールのruntime deviationである。DTC未満のsoft contextを、まずpredictive diagnostics / vehicle healthの部品側状態説明として価値があるかを見る。追加ログ、診断読み順、品質feedback、顧客説明境界は、その検証に必要な副次artifactとして扱う。低/高電圧または過温度によるreduced assistの1ケースは、比較用の診断読み順demoとして使う。

まだ言ってはいけないこと:

> SPD008で故障時期や交換時期が分かる。

> SPD002でreduced assist履歴からEPS寿命が分かる。

> どちらかで安全保証、root cause、保証費削減を主張できる。

この次の作業として、SPD008のfirst samplesを [docs/118_steering_predictive_diagnostics_spd008_first_samples.md](118_steering_predictive_diagnostics_spd008_first_samples.md) と [data/steering_predictive_diagnostics_spd008_first_samples.tsv](../data/steering_predictive_diagnostics_spd008_first_samples.tsv) に整理した。
