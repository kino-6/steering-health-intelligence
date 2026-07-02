# Steering Predictive Diagnostics Parallel Continuation Deep Dive

## 結論

今回の追加検討では、ユーザー提案の「runtimeで普段と違う状態を見る」案を、既存の継続候補と横並びで扱う。

結論は、継続候補は1本に絞らず、次の6本を並列に深掘りするのがよい。

1. 低/高電圧または過温度によるreduced assist
2. 電気接続 / harness / network由来の複合症状
3. 外部signalまたは通信validity異常
4. 熱保護に近い状態
5. DTC履歴とreduced assistの再発監視
6. 内部重要モジュールのruntime deviation

ただし、6番目はまだ案である。
EPS製品全体をE2Eで見て「普段と違う」と言うと、路面、タイヤ、運転者、アライメント、積載、温度、電源、外部ECU signalが混ざりすぎる。
そのため、追加候補として扱う場合は、EPS内部の重要モジュール単位に限定する。

並列深掘り表は [data/steering_predictive_diagnostics_parallel_continuation.tsv](../data/steering_predictive_diagnostics_parallel_continuation.tsv) に置く。

## 何を判断しているか

判断しているのは、最終判断でProceedにした固定スコープassessmentの次に、どの具体テーマを同時に掘るべきかである。

ここでは、最初から商品名を決めない。
見るのは、各候補がEPSサプライヤ内のどの成果物へ転記できるかである。

成果物の候補は次である。

1. 診断読み順
2. fault grouping map
3. signal dependency table
4. thermal state explanation template
5. recurrence feedback loop requirement
6. internal module runtime deviation map

## Rule Check

今回の判断では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Kaggle / Public Proxy Predictive Value Rule`
5. `Mandatory Rule Check Before Stop / Kill / Archive`

この文書では、Stop / Kill / Archiveを主結論にしていない。
ただし、各候補のHold / Stop条件を明示するため、次を確認する。

- 市場需要は、故障後ではなく、問題拡大前に診断、整備、品質、顧客説明の行動を決めたいことである
- Boschの `predictive diagnostics / predictive maintenance / vehicle health` は正面から扱う
- EPS交換時期、RUL、安全保証、root cause、保証費削減へ戻さない
- EPS内部状態やrepair feedbackがないことだけを主Kill理由にしない
- 不足データは、言ってはいけないことを切る境界として扱う
- EPSサプライヤとして持てる手札を、state定義、内部モジュール境界、診断意味、説明境界、追加ログtrigger、feedback要求へ限定する

## 市場需要

市場側の需要は、EPSが壊れる日を当てることだけではない。

実務上ほしいのは、DTCや警告が出たとき、またはDTC未満の違和感があるときに、次を早く決めることである。

1. 何を先に読むか
2. EPS内部故障と外部contextをどう分けるか
3. 交換前に何を確認するか
4. 顧客に何を説明してよいか
5. 品質側にどのfeedbackを戻すべきか
6. 追加ログを残すべき状態はどれか

この需要に対して、EPSサプライヤが最初に狙えるのは、fleet platformやRUL予測ではない。
操舵系の状態を、診断、説明、品質、評価へ転記できる形へ整理することである。

## 並列で深掘りする候補

### 1. 低/高電圧または過温度によるreduced assist

これは最初にdemo化する候補として残す。

理由は、電源、温度、assist limit、reduced assist、DTC / freeze frame / extended dataが、診断読み順へ落ちやすいためである。
E2Eで路面や運転者を推定しなくても、電源・温度・assist制限の内部/周辺contextを読む価値がある。

作るもの:

- one-case diagnostic reading order

Proceed signal:

- DTC単体ではなく、電圧、温度、assist mode、key cycle、repair feedback requirementを読む順番が出る

Hold / Stop signal:

- 既存service manualの「電源と温度を確認」以上にならない

### 2. 電気接続 / harness / network由来の複合症状

これはvehicle healthに近い候補として残す。

ただし、車両全体の故障診断をEPSサプライヤが代替する話ではない。
EPSが影響を受ける可能性がある電源、ground、connector、harness、network interfaceの境界を整理する。

作るもの:

- fault grouping map
- supplier boundary statement

Proceed signal:

- EPS交換前に読むべき複合症状、複数DTC、電源/通信/接続確認の順番が出る

Hold / Stop signal:

- 汎用電装診断に吸収され、EPSサプライヤ固有の説明が残らない

### 3. 外部signalまたは通信validity異常

これは誤交換回避と顧客技術説明に強い。

EPSが外部signalに依存している場合、そのsignalがinvalidになったときに、操舵表示やassist説明へどう影響するかを切る。
ここでも、外部ECUのroot causeを断定しない。

作るもの:

- signal dependency table
- diagnostic triage example

Proceed signal:

- 依存signal、invalid時の動作、先に読むDTC、言ってはいけないことを表にできる

Hold / Stop signal:

- 自社EPSが依存signalとfallbackを定義できない

### 4. 熱保護に近い状態

これは操舵系固有性がある。

ただし、整備actionは軽く、主価値は説明境界、不要交換回避、評価確認条件になりやすい。
路面や運転者負荷を直接特定するのではなく、motor / inverter温度、motor current、assist limit、thermal derating、復帰条件を見る。

作るもの:

- thermal state explanation template
- diagnostic validation seed

Proceed signal:

- 温度、assist limit、復帰、再発条件を自然言語で切れる

Hold / Stop signal:

- 単なる「熱くなると保護する」という既存説明の焼き直しで終わる

### 5. DTC履歴とreduced assistの再発監視

これは予測らしさが最も強いが、最も危ない。

DTC履歴、発生頻度、再発間隔、status agingは、repair feedbackとつながればmaintenance forecast候補になる。
しかし、DTC履歴だけで交換時期や故障発生時期を言ってはいけない。

作るもの:

- recurrence feedback loop requirement

Proceed signal:

- 修理結果なしで言えることと、修理結果があって初めて言えることを分けられる

Hold / Stop signal:

- repair feedbackが取れず、DTC履歴の読み方が既存診断と同じになる

### 6. 内部重要モジュールのruntime deviation

これは今回追加する案である。

EPS製品全体をE2Eで見て「普段と違う」と言う方向には寄せない。
外乱が多すぎるためである。

狙うなら、内部の重要モジュール単位で見る。

候補は次である。

1. torque / angle sensor plausibility
2. motor / inverter response
3. power monitor
4. thermal derating
5. communication input validity

ここで見るのは、規定範囲内だが、自己履歴、標準範囲、信号間整合からズレる状態である。
ただし、これを故障予測とは言わない。
最初の価値は、DTC未満の追加ログtrigger、診断読み順、品質feedback、顧客説明境界である。

作るもの:

- internal module runtime deviation map

Proceed signal:

- 規定範囲内のdeviationが、追加ログ保存や診断読み順へ転記できる

Hold / Stop signal:

- 安定したbaselineが作れない
- 既存diagnostic monitorで十分である
- 外部負荷を内部異常に誤読する
- 部署別成果物へ転記できない

## 並列優先順位

同時に見るが、初期demoの順番は分ける。

| Priority | Candidate | Reason |
|---:|---|---|
| 1 | SPD002 | 最も1ケースdemoにしやすい。診断読み順、service note、顧客説明へ落ちる |
| 2 | SPD003 | signal dependency tableとして切りやすく、誤交換回避に強い |
| 3 | SPD004 | vehicle healthに近いが、汎用電装診断に吸収されない境界が必要 |
| 4 | SPD008 | 新案として有望。ただしE2Eではなく内部モジュール単位に限定する必要がある |
| 5 | SPD001 | 操舵系固有だが、既存熱保護説明を超える必要がある |
| 6 | SPD007 | maintenance forecastに近いが、repair feedback依存が大きい |

## CoVe

| 検証質問 | 回答 | Confidence | 反映 |
|---|---|---:|---|
| SPD008を主テーマにしてよいか | No。まだ案であり、既存5候補と並列に置く。 | High | 結論で明記 |
| EPS製品全体E2Eのdeviation detectionは妥当か | Weak。外乱が多すぎて、EPS内部由来か外部条件由来か切りにくい。 | Medium-High | SPD008を内部モジュール単位に限定 |
| 既存候補はまだ継続価値があるか | Yes。SPD002/003/004/001/007は、それぞれ別の成果物へ転記できる。 | Medium | 並列深掘りに反映 |
| どれを最初にdemo化するべきか | SPD002。必要データ、診断読み順、言ってはいけないことが最も具体的である。 | Medium-High | 優先順位1位 |
| 予測語を使ってよいか | Yes。ただしRULや交換時期ではなく、predictive diagnostics / vehicle healthの診断・説明・ログ・feedback文脈に限定する。 | High | What not to claimに反映 |

## EPSサプライヤとしての言い方

言ってよいこと:

> 操舵系predictive diagnosticsの継続候補は、1本に絞らず、電源/温度、外部signal、複合電気症状、熱保護、再発履歴、内部重要モジュールのruntime deviationを並列に見る。目的はEPS交換時期を当てることではなく、診断読み順、説明境界、追加ログtrigger、品質feedback、service noteへ転記できるかを見ることである。

まだ言ってはいけないこと:

> EPS製品全体のE2E挙動から外乱原因を特定できる。

> 内部モジュールのdeviationから故障時期や交換時期が分かる。

> DTC未満の違和感を検知できれば安全保証やroot cause断定ができる。

## 次のTask

次は2本立てがよい。

1. SPD002の1ケースdiagnostic reading orderを作る
2. SPD008のinternal module runtime deviation mapを作る

SPD002は既存Proceed判断の検証である。
SPD008は追加案の成立性確認である。
この2本を比べると、既存診断読み順型と、新しいruntime deviation型のどちらにビジネスの芯があるかを見やすい。
