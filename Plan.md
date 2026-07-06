# Plan: Steering Predictive Diagnostics 次アクション

作成日: 2026-07-06
前提ブランチ: `research/bosch-motion-domain-ai`
現在地: SPD008 power monitor は「判定保留付きの限定Proceed」([docs/122](docs/122_steering_predictive_diagnostics_power_monitor_payload_sample.md))。判定を閉じるための検証タスクを以下に固定する。

## 何を判断しようとしているか

自然言語で言うと、次の1点である。

> EPS内部重要モジュール(まず電源監視、次に通信入力妥当性)がruntimeで観測した「DTC未満の普段と違う状態」は、既存のDTC / reset log / freeze frame / extended data / 汎用テレマティクス / ADAS / IDSでは残らない差分を持ち、原因断定なしに部署成果物またはvehicle healthへの部品側状態説明に転記できるか。

Yesなら SPD008 は次の本線として続き、Noなら Hold / Stop に落とす。
この判断に必要な作業だけを、下のNextActionに置く。

## NextAction 一覧

| # | 作業 | 目的 | 出力 | 状態 |
|---|---|---|---|---|
| 1 | 電源監視の実残存フィールド照合質問シート作成 | [docs/122](docs/122_steering_predictive_diagnostics_power_monitor_payload_sample.md) の判定ゲート(5項目中2項目以上のsoft context差分 + 2部署以上の使い道)を解くための唯一のインプットを作る | [docs/123](docs/123_steering_predictive_diagnostics_power_monitor_program_question_sheet.md) + [data TSV](data/steering_predictive_diagnostics_power_monitor_program_question_sheet.tsv) | 完了 |
| 2 | 通信入力妥当性の独立ケース化 | 第二検証候補([docs/120](docs/120_steering_predictive_diagnostics_spd008_predictive_value_check.md))を、電源監視と同じ型(単一ターゲットケース → 最小payload → 判定ゲート)で独立に判定できる状態にする | [docs/124](docs/124_steering_predictive_diagnostics_comm_input_validity_case.md) + [data TSV](data/steering_predictive_diagnostics_comm_input_validity_case.tsv) | 完了 |
| 3 | 未検証デルタのファクトチェックと判定 | 「SPD008の既存monitor比優位性は未検証」([docs/117](docs/117_steering_predictive_diagnostics_spd008_vs_spd002_decision.md))と「汎用テレマティクス / 路面分類 / ADAS / IDSとのデルタは未検証」([docs/98](docs/98_business_model_mainline_after_correction.md) Kill条件)を、公開情報で検証し判定を書く | [docs/125](docs/125_steering_predictive_diagnostics_unverified_delta_check.md) + [data TSV](data/steering_predictive_diagnostics_unverified_delta_check.tsv) | 完了 |
| 4 | SPD002デモ枝の扱いを明文化 | [docs/114](docs/114_steering_predictive_diagnostics_spd_final_conclusions.md) でProceed指定のまま停滞しているSPD002 reference demoを、1〜3が決着するまで意図的に凍結と記録し、暗黙の放置にしない | docs/125 内の1節 | 完了 |
| 5 | ブランチのremote公開 | 23コミット未pushでlocalのみ。消失リスク回避 | `git push -u origin research/bosch-motion-domain-ai` | 未実施(ユーザ判断待ち) |
| 6 | SOTIFへの乗り方の判定 | 「SOTIFに乗っかれるプロダクト」の見込みを3分解(プロセス支援 / 論証証拠 / 運用フェーズ監視インプット)で判定し、入口条件KQ1を固定する | [docs/126](docs/126_steering_predictive_diagnostics_sotif_contribution_prospect.md) + [data TSV](data/steering_predictive_diagnostics_sotif_contribution_prospect.tsv) | 完了 |
| 7 | ターゲットケースの公開実在確認 | 「permanent DTCが残らない断続的なassist低下」が公開苦情 / TSB / リコール調査に実在するかを、既存pain family整理を「故障コードが残らない」条件で絞り直して確認する。実在しなければ市場需要側から弱まる | [docs/127](docs/127_steering_predictive_diagnostics_target_case_public_evidence.md) + [data TSV](data/steering_predictive_diagnostics_target_case_public_evidence.tsv) | 完了。実在Confirmed(Ford 15V-340の「DTCなし」是正経路、GM 17V-414の1秒喪失・復帰、GM TSB 17-NA-158の外部signal起因警告ほか)。以後のSPD本線は内部資料条件待ち |

## 内部資料の扱い(2026-07-06追記)

現行方針は「公開情報は使う、内部資料は使わない」である。
これに伴い、次の2つは次アクションから外し、**内部資料を使える条件になった場合だけの実施条件**として保存する(Coverage Benchmark / SbWと同じ扱い)。

- #1 質問シートのprogram固有欄の回答取得(docs/123に実施条件として明記)
- docs/126のKQ1(RFQ / 安全要件の中身確認)とKQ2

現行方針で進められる次アクションは #7 である。

| # | 作業 | 目的 | 出力 | 状態 |
|---|---|---|---|---|
| 8 | SOTIF公開シグナル観測 | KQ1(SOTIF要求の部品側展開)の公算を公開情報で観測する | [docs/128](docs/128_steering_predictive_diagnostics_sotif_public_signal_watch.md) + TSV追記(SOTIF013〜016) | 完了。SOTIF-EooC(規格上の部品参加形式)とBosch定量SOTIF特許・by-wire量産を確認。KQ1公算は補強、最終確認は内部資料条件のまま |
| 9 | 判定ゲートの公開ケース照合 | 質問シートの照合対象を「自社program」から「公開リコール是正実務」へ組み替え、内部資料なしで判定ゲートを閉じられるか試す | [docs/129](docs/129_steering_predictive_diagnostics_public_case_crosscheck.md) + [data TSV](data/steering_predictive_diagnostics_public_case_crosscheck.tsv) | 完了。Ford 15S18・GM 17276の一次文書精読により5項目中4項目の差分を公開レベルでConfirmed。SPD008は「公開レベルConfirmed付き限定Proceed」へ。内部資料条件は検証ではなく実行のみに縮小 |
| 10 | comm input validityの公開ケース照合 | #9と同じ手法を第二候補に適用する | [docs/130](docs/130_steering_predictive_diagnostics_comm_validity_public_crosscheck.md) + [data TSV](data/steering_predictive_diagnostics_comm_validity_public_crosscheck.tsv) | 完了。GM TSB 17-NA-158原文で「無効な依存signal→操舵警告→直らないgear交換の連鎖」をOEM公式記録として確認し、Hold→公開レベルConfirmed付き限定Proceedへ。副産物としてFord SSM 49530(2021年)で現行世代のpower context誤帰属も確認 |

## 実行順と依存関係

1. #1 質問シート(電源監視) — docs/122の明示的な次タスク。最優先
2. #2 通信入力妥当性ケース — #1と独立。同じ型を再利用
3. #3 デルタ検証 — #1/#2の照合観点を既存技術事実(UDS / AUTOSAR DEM / テレマティクス電圧監視 / IdsM)と突き合わせる。ネットワークでのファクトチェックを含む
4. #4 は#3のドキュメント内で処理
5. #5 は任意タイミング

## 判定の出口

- 質問シート(#1)が対象programで回答され、判定ゲートの条件を満たす → 電源監視はProceed(固定スコープassessmentとして)
- 既存monitor / 既存mechanismで5項目が十分に残ると分かる → Hold / Stop に落とす(Rule Check必須)
- #3で汎用テレマティクス / IDSとの差分が説明できない → docs/98のKill条件に接続する

## 禁止主張(全作業共通)

EPS RUL、交換時期、故障発生時期、安全保証、root cause断定、保証費削減、EPS無罪、電源原因断定、外部ECU原因断定。
