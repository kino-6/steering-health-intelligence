# Steering Predictive Diagnostics Promising Candidate Deep Dive

## 結論

見込みがある候補は、同じ「Proceed」でも性格が違う。

最も伸びしろがあるのは、内部重要モジュールのruntime deviationである。
これは、EPS製品全体をE2Eで見て外乱込みの違和感を当てる話ではない。
torque / angle sensor、motor / inverter、power monitor、thermal derating、communication input validityのような内部重要モジュールについて、規定範囲内だが自己履歴、標準範囲、信号間整合からズレる状態を、追加ログ、診断読み順、品質feedbackへ転記できるかを見る。

一方で、最初に実証すべきなのは、低/高電圧または過温度によるreduced assistである。
理由は、診断読み順、service note、顧客説明へ最も早く落とせるためである。

したがって、次は2本立てで進めるのがよい。

1. `SPD008`: 内部重要モジュールのruntime deviation mapを作る
2. `SPD002`: 低/高電圧または過温度によるreduced assistの1ケースdiagnostic reading orderを作る

他の候補も落とさない。
`SPD003` は実務価値が出やすく、`SPD004` はvehicle health文脈に近い。
`SPD001` は二番手以下、`SPD007` はrepair feedback loopが見える場合だけ条件付きで扱う。

詳細表は [data/steering_predictive_diagnostics_promising_candidate_deep_dive.tsv](../data/steering_predictive_diagnostics_promising_candidate_deep_dive.tsv) に置く。

## 何を判断しているか

判断しているのは、操舵系predictive diagnosticsの継続候補のうち、どれが次の作業に値するかである。

ここでいう「見込み」は、EPS交換時期を当てられるという意味ではない。
次のどれかへ転記できるという意味である。

1. 診断企画の読み順
2. 追加ログ保存trigger
3. 顧客技術説明の境界
4. service noteへ転記できる確認順
5. 品質改善のfeedback要求
6. 製品企画や診断企画で確認すべき内部モジュール境界

## Rule Check

今回の判断では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Kaggle / Public Proxy Predictive Value Rule`
5. `Mandatory Rule Check Before Stop / Kill / Archive`

この文書では、各候補のHold / Stop境界を明示する。
そのため、次を確認する。

- 市場需要は、故障後ではなく、問題拡大前に診断、整備、品質、顧客説明の行動を決めたいことである
- Boschの `predictive diagnostics / predictive maintenance / vehicle health` は正面から扱う
- EPS交換時期、RUL、安全保証、root cause、保証費削減へ戻さない
- EPS内部状態やrepair feedbackがないことだけを主Kill理由にしない
- 不足データは、言ってはいけないことを切る境界として扱う
- EPSサプライヤとして持てる手札を、内部モジュール境界、診断意味、説明境界、追加ログtrigger、feedback要求へ限定する

## 市場需要

市場側の需要は、故障が確定してからDTCを読むことだけではない。

実務では、次が問題になる。

1. まだ故障と断定できない状態で、何を追加で読むべきか
2. DTCが出たとき、EPS内部故障と外部contextをどう分けるか
3. 交換前に、電源、温度、通信、外部signal、harnessをどこまで確認すべきか
4. DTC未満の違和感を、追加ログや品質feedbackへどう残すか
5. 顧客へ、何を説明してよく、何を言ってはいけないか

この需要に対して、EPSサプライヤが最初に売る、または社内で使うべきものは、RUL予測ではない。
操舵系の状態を、診断、説明、品質、評価、追加ログ設計へ転記できる形にすることである。

## 見込みがある候補

### 1. SPD008: 内部重要モジュールのruntime deviation

これは最も伸びしろがある。

理由は、既存のDTC表やservice manualの整理を超えて、EPS製品側の機能価値に近づく可能性があるためである。
規定範囲内だが普段と違う、という状態を、DTC未満の追加ログtrigger、診断読み順、品質feedback、顧客説明境界へつなげられれば、単なる事後診断ではなく、predictive diagnosticsらしい付加価値になる。

ただし、E2E製品全体で見てはいけない。
路面、タイヤ、運転者、アライメント、積載、温度、電源、外部ECU signalが混ざりすぎるためである。

見るべき単位は、内部重要モジュールである。

候補:

1. torque / angle sensor plausibility
2. motor / inverter response
3. power monitor
4. thermal derating
5. communication input validity

作るべき成果物:

- internal module runtime deviation map

最初の確認:

- 各モジュールで、入力、出力、比較対象、通常範囲、自己履歴、標準範囲、既存monitor、追加ログtriggerを並べる

Proceed signal:

- 規定範囲内のdeviationが、追加ログ保存や診断読み順へ転記できる
- 既存monitorでは拾わないが、品質feedbackや顧客説明に残したい状態がある

Hold / Stop境界:

- 既存diagnostic monitorで十分である
- baselineが安定しない
- 外部負荷を内部異常として誤読する
- 診断企画または品質改善の成果物へ転記できない

### 2. SPD002: 低/高電圧または過温度によるreduced assist

これは最もdemo-readyである。

理由は、電源、温度、assist limit、reduced assist、DTC / freeze frame / extended dataが、診断読み順とservice noteへ落ちやすいためである。
新規性はSPD008より弱い。
しかし、固定スコープassessmentが本当に既存資料の要約を超えるかを確認するには、一番良い。

作るべき成果物:

- one-case diagnostic reading order

最初の確認:

- 低/高電圧または過温度によるreduced assistの1ケースについて、読む順番、必要データ、言ってよいこと、言ってはいけないことを1枚化する

Proceed signal:

- DTC単体よりも、電圧、温度、assist mode、key cycle、repair feedback requirementを読む順番が具体化する

Hold / Stop境界:

- 既存service manualの「電源と温度を確認」以上にならない
- 電圧、温度、assist modeが診断情報に残らず、説明境界も作れない

### 3. SPD003: 外部signalまたは通信validity異常

これは実務価値が出やすい。

理由は、誤交換回避、責任境界、顧客技術説明に強いためである。
EPSが外部signalに依存している場合、そのsignalがinvalidになったとき、操舵表示やassist説明へどう影響するかを切れる。

作るべき成果物:

- signal dependency table

最初の確認:

- 外部signal invalid時に、操舵DTC、外部ECU DTC、CAN validity、fallbackをどう読むかを表にする

Proceed signal:

- 依存signal、invalid時の動作、先に読むDTC、言ってよいこと/いけないことを示せる

Hold / Stop境界:

- 自社EPSの依存signal、fallback、表示影響を定義できない
- 通信診断や外部ECU診断の一般論に埋もれる

### 4. SPD004: 電気接続 / harness / network由来の複合症状

これは戦略的には魅力がある。

理由は、vehicle health文脈に最も近いためである。
複数ECU症状、電源、harness、networkを束ねることで、EPS交換前の確認順やfault groupingに使える。

一方で、リスクも大きい。
車両全体ログ、複数ECU DTC、service workflowがOEM/fleet/platform依存であり、EPSサプライヤ固有の価値が薄くなりやすい。

作るべき成果物:

- fault grouping map
- supplier boundary statement

Proceed signal:

- EPS単体故障、電源/harness/network、外部ECU影響を混同しない分類が作れる

Hold / Stop境界:

- EPSサプライヤ固有のstateや説明境界が残らず、一般電装診断だけになる

## その他候補の状況

### SPD001: 熱保護に近い状態

これは二番手以下でよい。

操舵系固有性はある。
motor / inverter温度、motor current、assist limit、thermal derating、復帰条件はEPSサプライヤが語りやすい。

ただし、既存の熱保護説明と重複しやすい。
整備actionも、冷却、復帰、再発確認に留まりやすい。

残す理由:

- 顧客説明、評価確認条件、不要交換回避には使える

低優先の理由:

- 追加ログtriggerや診断読み順へ転記できなければ、既存説明の焼き直しになる

### SPD007: DTC履歴とreduced assistの再発監視

これは条件付きである。

DTC履歴、発生頻度、再発間隔、status agingをservice outcomeと結べれば、maintenance forecastに近づく。
しかし、repair feedbackなしでは、DTC履歴だけで交換時期予測に戻りやすい。

残す理由:

- repair feedback loopが見える特定programでは、品質改善や再発監視に使える

低優先の理由:

- repair feedbackがないと、既存DTC履歴の読み方とほぼ同じになる
- DTC履歴だけでRULや交換日を推定する方向へ戻る危険がある

## CoVe

| 検証質問 | 回答 | Confidence | 反映 |
|---|---|---:|---|
| 見込みがある候補は1本に絞れるか | No。伸びしろ、実証しやすさ、実務転記先が違うため、SPD008とSPD002を2本立てにするのがよい。 | Medium-High | 結論 |
| SPD008は最有力と言ってよいか | 伸びしろは最も大きい。ただし未検証であり、主テーマ確定ではない。 | Medium | Promising but unproven |
| SPD002は最有力か | ビジネスの伸びしろより、demo-readyとして最有力である。 | Medium-High | Most demo-ready |
| SPD003/004は残すべきか | Yes。SPD003は実務価値、SPD004はvehicle health接続がある。ただし一般論化リスクを明示する。 | Medium | Practical / Strategic |
| SPD001/007は落とすべきか | No。ただし低優先または条件付きに置く。 | Medium | その他候補の状況 |
| EPS交換時期予測へ戻っていないか | 戻っていない。各候補で禁止主張を明示した。 | High | What not to claim |

## EPSサプライヤとしての言い方

言ってよいこと:

> 見込みがあるのは、内部重要モジュールのruntime deviationと、低/高電圧または過温度によるreduced assistの2本である。前者は伸びしろ、後者は実証しやすさがある。どちらもEPS交換時期を当てる話ではなく、追加ログ、診断読み順、説明境界、品質feedbackへ転記できるかを見る。

まだ言ってはいけないこと:

> 内部モジュールのdeviationから故障時期や交換時期が分かる。

> reduced assistの履歴からEPS寿命が分かる。

> 外部signalや複合電気症状からroot causeや保証責任を断定できる。

> 熱保護近傍の状態から安全保証や交換必要性を言える。

## 次のTask

次は、2つのartifactを作る。

1. `SPD008`: internal module runtime deviation map
2. `SPD002`: one-case diagnostic reading order

この2つを比較すると、新しい機能価値に寄せるべきか、まず診断読み順assessmentとして成立性を固めるべきかを判断しやすい。
