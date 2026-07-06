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
