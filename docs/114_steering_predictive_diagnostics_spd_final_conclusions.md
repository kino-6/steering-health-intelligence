# Steering Predictive Diagnostics SPD Final Conclusions

## 結論

今回のGoalでは、`SPD002`、`SPD003`、`SPD004`、`SPD001`、`SPD007`、`SPD008` について、一定の結論を出すところまで深掘りした。

結論は、全候補を同じProceed扱いにはしない。
次に進める中心は2本である。

1. 内部重要モジュールのruntime deviationを、追加ログ、診断読み順、品質feedbackへ転記できるかを見る
2. 低/高電圧または過温度によるreduced assistの1ケースで、既存DTC表やservice manualを超える診断読み順が作れるかを見る

つまり、伸びしろは `SPD008`、実証しやすさは `SPD002` にある。
`SPD003` は実務支援として残す。
`SPD004` はvehicle healthに近いが、一般電装診断に吸収されやすいため戦略オプションに下げる。
`SPD001` は低優先、`SPD007` はrepair feedback loopが見える場合だけ条件付きで再開する。

詳細表は [data/steering_predictive_diagnostics_spd_final_conclusions.tsv](../data/steering_predictive_diagnostics_spd_final_conclusions.tsv) に置く。

## 何を判断しているか

判断しているのは、操舵系predictive diagnosticsのSPD候補を、EPSサプライヤの次の作業へ進めるかどうかである。

ここでいう「進める」は、EPS交換時期やremaining lifetimeを予測するという意味ではない。
進める価値があるとは、次のどれかへ転記できるという意味である。

1. 診断企画の読み順
2. DTC未満の追加ログ保存trigger
3. 顧客技術説明の境界
4. service noteへ転記できる確認順
5. 品質改善のfeedback要求
6. 製品企画で確認すべき内部モジュール境界

## Rule Check

今回の判断では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Kaggle / Public Proxy Predictive Value Rule`
5. `Mandatory Rule Check Before Stop / Kill / Archive`

この文書では、`Hold`、`Stop boundary`、`低優先`、`条件付き` を明示する。
そのため、次を確認する。

- 市場需要から始めている
- 自然言語で、誰のどの業務の話かを説明している
- EPSサプライヤとして売る / 実施する / 言ってはいけないことに戻している
- EPS内部状態やrepair feedbackがないことだけを主Kill理由にしていない
- 不足データは、RUL、交換時期、安全保証、root cause、保証費削減を言わないための境界として扱っている
- 具体的な再開条件または次の検証質問を残している

## Market Demand

市場側の需要は、故障が確定してからDTCを読むことだけではない。

実務では、DTCが出る前、またはDTCが出ても原因を断定できない段階で、次を決めたい。

1. 何を追加で読むべきか
2. EPS内部故障と外部contextをどう分けるか
3. 交換前に何を確認するか
4. 顧客へ何を説明してよいか
5. 品質側へ何をfeedbackすべきか
6. DTC未満の違和感をログとして残すべきか

Boschの `predictive diagnostics / predictive maintenance / vehicle health` という言葉を、このブランチでは正面から扱う。
ただし、操舵系で最初に狙うのは、EPSのRULや交換時期ではない。
診断、説明、品質、追加ログ設計へ転記できる予測的付加価値である。

## Item Conclusions

| SPD | Conclusion | Confidence | Why | Next action |
|---|---|---:|---|---|
| SPD008 | Proceed to concept artifact | Medium | 伸びしろが最も大きい。内部重要モジュール単位ならEPSサプライヤの主語が残る。 | internal module runtime deviation map |
| SPD002 | Proceed to demo | Medium-High | 実証しやすい。診断読み順、service note、顧客説明へ落としやすい。 | one-case diagnostic reading order |
| SPD003 | Proceed as practical support | Medium-High | 誤交換回避、責任境界、顧客技術説明に強い。 | signal dependency table |
| SPD004 | Hold as strategic option | Medium | vehicle healthに近いが、一般電装診断に吸収されやすい。 | SPD003後に必要ならfault grouping map |
| SPD001 | Defer | Medium | 操舵系固有だが、既存熱保護説明を超えにくい。 | SPD008/002後に必要なら説明template |
| SPD007 | Conditional only | Medium-Low | repair feedback loopがある場合だけmaintenance forecastに近づく。 | 特定programでfeedback loopが見えるまで新規artifactなし |

## SPD008: 内部重要モジュールのruntime deviation

これは、最も本命に近い。

理由は、DTC表やservice manualの整理だけでなく、EPS製品側の機能価値に近づく可能性があるためである。
規定範囲内だが普段と違う状態を、DTC未満の追加ログtrigger、診断読み順、品質feedback、顧客説明境界へつなげられれば、予測的付加価値に近い。

ただし、EPS製品全体をE2Eで見てはいけない。
路面、タイヤ、運転者、アライメント、積載、温度、電源、外部ECU signalが混ざりすぎる。
そのため、見る単位は内部重要モジュールに限定する。

最初に見るモジュール:

1. torque / angle sensor plausibility
2. motor / inverter response
3. power monitor
4. thermal derating
5. communication input validity

Proceed条件:

- 少なくとも2モジュールで、既存monitorでは完結しないが、追加ログまたは品質feedbackに残したいdeviationが定義できる

Hold条件:

- 既存diagnostic monitorで同じ判定が完結する
- baselineが安定しない
- 外部負荷を内部異常として誤読する

Stop境界:

- 内部モジュール単位に限定しても、診断企画、品質改善、顧客技術説明のどれにも転記できない

次アクション:

- `internal module runtime deviation map` を作る

## SPD002: 低/高電圧または過温度によるreduced assist

これは、最初に実証する候補である。

理由は、電源、温度、assist limit、reduced assist、DTC / freeze frame / extended dataが、診断読み順とservice noteへ落ちやすいからである。
新規性はSPD008ほど強くない。
しかし、固定スコープassessmentが既存資料の要約を超えるかを試すには一番よい。

Proceed条件:

- DTC単体よりも、電圧、温度、assist mode、key cycle、repair feedback requirementを読む順番が具体化する

Hold条件:

- 既存service manualの「電源と温度を確認」を言い換えるだけになる

Stop境界:

- 電圧、温度、assist modeが残らず、説明境界も作れない

次アクション:

- `one-case diagnostic reading order` を作る

## SPD003: 外部signalまたは通信validity異常

これは、実務支援として残す。

理由は、誤交換回避、責任境界、顧客技術説明に強いためである。
EPSが外部signalに依存している場合、そのsignalがinvalidになったときに、操舵表示やassist説明へどう影響するかを切れる。

Proceed条件:

- 依存signal、invalid時の動作、先に読むDTC、言ってよいこと/いけないことを示せる

Hold条件:

- 通信診断や外部ECU診断の一般論に埋もれる

Stop境界:

- 自社EPSの依存signal、fallback、表示影響を定義できない

次アクション:

- `signal dependency table` を作る

## SPD004: 電気接続 / harness / network由来の複合症状

これは、戦略オプションとしてHoldにする。

vehicle health文脈には最も近い。
しかし、車両全体ログ、複数ECU DTC、service workflowがOEM/fleet/platform依存であり、EPSサプライヤ固有の価値が薄くなりやすい。

Proceed条件:

- EPS単体故障、電源/harness/network、外部ECU影響を混同しない分類が作れる

Hold条件:

- 複数ECU情報が取れず、EPS側の説明境界だけになる

Stop境界:

- EPSサプライヤ固有のstateや説明境界が残らず、一般電装診断だけになる

次アクション:

- SPD003後に、必要なら `fault grouping map` を作る

## SPD001: 熱保護に近い状態

これは、低優先にする。

操舵系固有性はある。
motor / inverter温度、motor current、assist limit、thermal derating、復帰条件はEPSサプライヤが語りやすい。

ただし、既存の熱保護説明と重複しやすい。
整備actionも、冷却、復帰、再発確認に留まりやすい。

残す理由:

- 顧客説明、評価確認条件、不要交換回避には使える

低優先の理由:

- 追加ログtriggerや診断読み順へ転記できなければ、既存説明の焼き直しになる

次アクション:

- SPD008/002後に必要なら `thermal state explanation template` を作る

## SPD007: DTC履歴とreduced assistの再発監視

これは、条件付きにする。

DTC履歴、発生頻度、再発間隔、status agingをservice outcomeと結べれば、maintenance forecastに近づく。
しかし、repair feedbackなしでは、DTC履歴だけで交換時期予測に戻りやすい。

再開条件:

- repair feedback
- 再発有無
- 作業結果
- 部品交換有無
- 修理後の同一/類似DTC再発

Stop境界:

- DTC履歴だけでRULや交換日を推定する方向へ戻る

次アクション:

- 特定programでfeedback loopが見えるまで、新規artifactは作らない

## Deepened Points

今回、弱点として重点的に見たのは次である。

1. SPD008が既存diagnostic monitorと重複しないか
2. SPD004が一般電装診断に吸収されないか
3. SPD007がDTC履歴だけの交換時期予測に戻らないか
4. SPD002が既存service manualの要約で終わらないか

その結果、SPD008は最も伸びしろがあるが、まずconcept artifactで既存monitorとの差分を見る段階に置く。
SPD002は事業の本命ではなく、固定スコープassessmentの実証用demoに置く。
SPD004は戦略オプション、SPD007は条件付きに下げる。

## What Not To Claim

次は言ってはいけない。

1. 内部モジュールのdeviationから故障時期や交換時期が分かる
2. reduced assistの履歴からEPS寿命が分かる
3. 外部signalや複合電気症状からroot causeや保証責任を断定できる
4. 熱保護近傍の状態から安全保証や交換必要性を言える
5. DTC履歴だけでRULや交換日を推定できる
6. EPS製品全体のE2E挙動から外乱原因を特定できる

## CoVe

| 検証質問 | 回答 | Confidence | 反映 |
|---|---|---:|---|
| SPD008を本命候補にしてよいか | Yes。ただし本命確定ではなく、concept artifactで成立性を見る段階である。 | Medium | Rank 1 |
| SPD002を本命にすべきか | No。最も実証しやすいが、伸びしろはSPD008より小さい。 | Medium-High | Rank 2 |
| SPD003は続けるべきか | Yes。signal dependency tableとして実務価値がある。 | Medium-High | Rank 3 |
| SPD004は続けるべきか | 条件付き。vehicle healthには近いが、一般電装診断化リスクがある。 | Medium | Hold |
| SPD001は続けるべきか | 低優先。説明templateにはなるが、差分が薄い。 | Medium | Defer |
| SPD007は続けるべきか | repair feedback loopが見える場合だけ。 | Medium-Low | Conditional |
| EPS交換時期予測へ戻っていないか | 戻っていない。禁止主張とStop境界を明記した。 | High | What not to claim |

## EPS Supplier Conclusion

EPSサプライヤとして実施すること:

- SPD008の `internal module runtime deviation map` を作る
- SPD002の `one-case diagnostic reading order` を作る
- SPD003の `signal dependency table` を次点で用意する

EPSサプライヤとしてまだ売らないこと:

- EPS RUL予測
- EPS交換時期予測
- Bosch型fleet predictive maintenance platform
- 安全保証
- root cause / warranty cost reduction

OEM / fleet / service platform領域として初期対象外に置くもの:

- fleet dispatch
- workshop appointment decision
- OEM保証DB連携前提のmaintenance forecast
- 車両全体ログによるcomponent localization

次に見せる部署:

1. 診断企画
2. 製品企画
3. 品質改善
4. 顧客技術説明

## Stop / Continue Judgment

このGoalの結論は、Continueである。

ただし、Continue対象は全SPDではない。
次に作るべきものは、`SPD008` と `SPD002` の2つである。

`SPD003` は近い実務支援として残す。
`SPD004` は戦略オプションとしてHold。
`SPD001` は低優先。
`SPD007` はrepair feedback loopが見える場合だけ再開する。
