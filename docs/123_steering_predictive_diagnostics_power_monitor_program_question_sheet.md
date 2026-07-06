# Power Monitor Program Question Sheet

## 結論

power monitorの判定を閉じるための、対象program別の実残存フィールド照合質問シートを作成した。

このシートは、[docs/122](122_steering_predictive_diagnostics_power_monitor_payload_sample.md) のDecision Gate(5項目のうち2項目以上で既存monitorに残らないsoft contextがあり、2部署以上で使い道がある場合だけProceed)を解くための唯一のインプットである。

現時点の判断は変えない。**判定保留付きの限定Proceed** のままである。
このシートが対象programの診断仕様で回答された時点で、Proceed / Hold / Stopのどれかに落とす。

重要な補正が1つある。
公開されているAUTOSAR診断標準を確認した結果、「DTC未満のcontextは既存の仕組みでは残せない」という前提は正確ではない。
AUTOSARのDiagnostic Event Manager(Dem)は、snapshot / extended dataの格納トリガをconfirmed(DTC確定)だけでなくpending、testFailed(検出成立)の段階でも設定でき、デバウンスカウンタの不揮発保存も標準機能として持つ。
したがって本シートの質問は、「残せるか」ではなく「**対象programの設定で実際に残しているか**」を聞く形にした。
差分があるとすれば、それは新しい検知能力ではなく、EPSサプライヤ側の設計・設定選択で埋められる状態説明の穴である。

詳細表は [data/steering_predictive_diagnostics_power_monitor_program_question_sheet.tsv](../data/steering_predictive_diagnostics_power_monitor_program_question_sheet.tsv) に置く。

## 何を判断しているか

判断しているのは、次の1点である。

> 対象programの既存診断設定(DTC、reset log、freeze frame / extended data、event memory)で、「短い電圧dip / near-reset contextとassist limitationの近接がDTC未満で繰り返す」ケースを後から状態説明できるか。できないなら、その穴はEPSサプライヤの設計選択で埋められるか。

質問の宛先は、対象programの診断設計担当(EPSサプライヤ内の診断企画 / ソフト設計)である。
OEM側の資料を要求する質問は含めない。EPSサプライヤが自分の製品仕様として答えられる範囲に限定した。

## Rule Check

今回の作業では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Kaggle / Public Proxy Predictive Value Rule`
5. `Steering Predictive Diagnostics Value Rule`
6. `Mandatory Rule Check Before Stop / Kill / Archive`

確認結果:

- 市場需要は、故障確定前または原因未確定の段階で、EPSが観測したpower contextを後から読めるかである
- EPS製品全体E2Eではなく、power monitorという内部重要モジュール単位に限定している
- 質問シートは判定ゲートを解くための副次artifactであり、それ自体を最終成果物にしない
- EPS交換時期、RUL、安全保証、root cause、保証費削減を主張していない
- 既存設定で十分に残るならHoldまたはStopにする
- 「AUTOSARの標準機能で残せる」という事実は、SPD008を殺す理由ではなく、価値主張を「検知能力」から「component boundaryでの状態説明設計」へ言い直す理由として扱う

## Market Demand

繰り返しになるが、市場需要はEPS交換時期を当てることではない。

実務でこのシートの回答が要るのは、次の場面である。

1. reduced assist / assist limitationの市場クレームが来たが、permanent under-voltage DTCが残っておらず、EPS内部故障か電源系かの切り分けに時間がかかる
2. 品質改善が、DTC未満のnear-threshold power contextの再発傾向をfieldで追いたいが、何が残っているか分からない
3. 顧客技術説明で、原因断定なしに「EPSが観測した事実」を出したいが、出せる事実の在庫が不明
4. vehicle health基盤側から部品側contributionを求められたとき、既存設定のままで渡せるものと、設計変更が要るものの区別がない

## 質問シートの構成

質問は、[docs/122](122_steering_predictive_diagnostics_power_monitor_payload_sample.md) の5 check item × 6質問軸のマトリクスである。

質問軸:

| Axis | 質問 | 判定への使い方 |
|---|---|---|
| Q1 | 既存DTC / reset log / freeze frame / extended dataに、その項目は残るか | Yesが多いほどHold寄り |
| Q2 | DTC未満(pending / testFailed / デバウンス未成立)の段階でも残るか | Noなら差分候補 |
| Q3 | assist mode / limit stateと同一event recordで紐づくか | Noなら同時性の差分候補 |
| Q4 | key cycleをまたぐ再発回数が残るか | Noならrecurrenceの差分候補 |
| Q5 | 既存資料だけで docs/122 の状態説明文を書けるか | YesならHold / Stop |
| Q6 | 不足がある場合、Dem設定変更または追加trigger設計で埋められるか | Yesならminimum payloadをsupporting artifactとして残す |

check item(docs/122のRetained Field Checklistと同一):

1. under-voltage DTC
2. reset log
3. freeze frame / extended data
4. assist mode / limit stateと電圧contextの同時性
5. DTC未満eventのkey cycle recurrence

## 公開情報で先に埋められる一般論

対象program固有の回答は空欄で渡すが、AUTOSAR標準の一般論として次は既知である。
回答者はこれを前提に、自programの設定がどれに該当するかだけを答えればよい。

| 項目 | 公開標準での事実 | programに聞くこと |
|---|---|---|
| snapshot格納トリガ | Demはsnapshot record番号ごとに、testFailed / pending / confirmedのどのstatus遷移で格納するかを設定できる | 自programのsnapshotトリガはどれか。confirmed限定なら、DTC未満eventのsnapshotは残らない |
| extended data格納トリガ | 同様にrecord番号ごとに設定できる。occurrence counter、aging counter、最終発生時刻などを含められる | occurrence counterはDTC未満eventも数えるか、confirmed後だけか |
| デバウンスカウンタ保存 | デバウンスカウンタの不揮発保存(シャットダウン時保存を含む)は標準機能として存在する | 自programはデバウンスカウンタをNV保存しているか。していれば「DTCに至らなかった接近度」が読める |
| event memory entry | event memoryへの登録条件はpending / confirmedなどで設定できる | DTC未満のeventはevent memoryに入るか |
| 閾値未満のdip | デバウンス閾値に達しない(testFailedにならない)短いdipは、Demの枠組みでは原理的にどこにも残らない | dip検出のデバウンス設定(閾値、継続時間)はいくつか。assist limitationを起こし得るdipがtestFailed未満に収まる設計か |

この表の最後の行が、SPD008 power monitorの差分が残る可能性の中心である。
「testFailedに至らないが機能影響(assist limitation)はあった」領域は、標準の仕組みの外にあり、残すなら追加のtrigger設計(=minimum payload)が要る。

## 判定ロジック

回答が揃ったら、次で機械的に判定する。

1. 5 check itemごとに、Q1〜Q4の回答から「既存設定で十分 / 差分あり」を決める
2. 差分ありが2項目未満 → **Hold / Stop**(docs/122のStop条件「既存monitorで5項目が十分に残る」に該当するか確認し、Rule Checkを書いた上で落とす)
3. 差分ありが2項目以上 → Q6で埋められるかを確認し、埋められるなら診断企画、品質改善、顧客技術説明のうち2部署以上の使い道を確認して **Proceed**(固定スコープassessmentとして)
4. 差分はあるがQ6で埋められない(設計変更不能、コスト過大) → **Hold**

## EPSサプライヤとしての言い方

言ってよいこと:

> 対象programの診断設定で、assist制限近傍の短い電源不安定がDTC未満でどこまで残るかを照合する。残らない領域があり、それがEPS側の設計選択で埋められるなら、原因断定なしの状態説明として価値候補になる。

まだ言ってはいけないこと:

> 既存診断では残らないことが分かっている。

(→ 対象programの設定次第であり、照合前に断定しない)

> 電源原因が分かるようになる。

> EPS交換時期が分かる。

## 次の作業

1. 本シート(TSV)を対象programの診断設計担当に渡し、program固有欄を回答してもらう
2. 回答を判定ロジックに通し、Proceed / Hold / Stopを docs/122 のDecision Gateで閉じる
3. Proceedの場合だけ、minimum payloadをsupporting artifactとして確定する
4. 並行して、第二候補のcommunication input validityは [docs/124](124_steering_predictive_diagnostics_comm_input_validity_case.md) で独立に判定する

## Sources

AUTOSAR標準の一般論は次の公開情報による。

- [AUTOSAR SWS Diagnostic Event Manager (R20-11)](https://www.autosar.org/fileadmin/standards/R20-11/CP/AUTOSAR_SWS_DiagnosticEventManager.pdf): snapshot / extended dataの格納トリガ設定(testFailed / pending / confirmed)、デバウンスカウンタ、event memory
- [AUTOSAR SRS Diagnostic (FO R1.1.0)](https://www.autosar.org/fileadmin/standards/R17-03_R1.1.0/FO/AUTOSAR_SRS_Diagnostic.pdf): 診断要求仕様
