# ドキュメント索引(旧READMEの「推奨読書順」を移設)

> **現在の結論: [224 現在の結論(2026-08-30)](224_current_conclusion.md)** ← 復帰時はまずここ

このファイルは、README.md にあった全ドキュメントの逐一リストを移設したものである。
README.md は結論とその根拠を読むための入口に整理し直したため、網羅的な索引はここに置く。

**現在の結論だけを知りたい場合は [README.md](../README.md)、セッション復帰は [Memory.md](../Memory.md) を読む。**

## 1. 現行の主線(実証フェーズ、docs/132〜151)

進行表と各フェーズの判定は [Plan.md](../Plan.md) が正。ここでは成果物だけを並べる。

| doc | 内容 | 主な出力 |
|---|---|---|
| [132](132_steering_predictive_diagnostics_payload_replay_demo.md) | 公開3ケースの最小payload再演と禁止主張の機械的ガード | `scripts/spd008_payload_replay.py` / `generated/spd008_payload_replay.html` |
| [133](133_failure_prediction_demand_map.md) | 故障予測を欲しがる主体別の需要マップ。空席は2つだけと特定 | `data/failure_prediction_demand_map.tsv` |
| [134](134_group_level_data_feasibility.md) | 群レベル曲線が公開データで誠実に引けるかの判定(=引ける) | `data/group_level_data_feasibility.tsv` |
| [135](135_steering_cohort_curve_demo_verdict.md) | 群レベル操舵系リスク曲線Demo。リコール対象cohortの答え合わせ成功 | `scripts/steering_cohort_curve.py` / `generated/steering_cohort_curve.html` |
| [136](136_steering_cohort_backtest_verdict.md) | 時点区切りバックテスト。リコール25ヶ月前に発火、偽陽性ゼロ | `scripts/steering_cohort_backtest.py` / `generated/steering_cohort_backtest.html` |
| [137](137_residual_candidates_sweep.md) | 横展開(負の結果)、故障モード分類、DVSA見極め、転記見本 | `scripts/steering_mode_split.py` / `data/steering_mode_split.tsv` |
| [138](138_business_model_definition.md) | ビジネスモデルの3層定義とKill条件(BM-KQ1〜4) | — |
| [139](139_log_sign_extraction_demo.md) | 公開走行logからの統計兆候の機械抽出(技術者向けDemo) | `scripts/steering_log_sign_extraction.py` / `generated/steering_log_sign_extraction.html` |
| [140](140_recall_detection_protocol.md) / [141](141_recall_detection_results.md) | 実証モデルA v1: 事前登録プロトコルと結果 | `scripts/recall_detection_model.py` |
| [142](142_recall_detection_protocol_v2.md) / [143](143_recall_detection_results_v2.md) | v2改訂と確定判定(基準に僅差未達=不成立を記録) | `data/recall_detection_results.tsv` / `generated/recall_detection_report.html` |
| [144](144_synthetic_sensitivity_results.md) | 実証モデルB: 合成劣化注入による検出限界の定量 | `scripts/steering_synthetic_sensitivity.py` / `generated/steering_synthetic_sensitivity*.html` |
| [145](145_final_conclusions_and_interpretations.md) | **技術・ビジネスの結論(確定版)と数字の読み方** | — |
| [146](146_business_framework_and_roadmap.md) | **ビジネスの枠組み・段取り・時限の窓・誤り条件** | — |
| [147](147_multiplatform_and_variant_verification.md) | 4車種再現と実在変種の分離可否(手法は移るが閾値は移らない) | `data/steering_fw_group_*.tsv` |
| [148](148_dvsa_mot_denominator_verification.md) | 英国車検2,800万件による分母つき群曲線 | `scripts/dvsa_mot_steering_rates.py` / `generated/dvsa_mot_steering_2025.html` |
| [149](149_concentration_ev_and_japan.md) | 車種偏在、EV/新興メーカー、日本データの可用性 | `scripts/dvsa_mot_concentration.py` / `data/dvsa_mot_concentration_2025.tsv` |
| [150](150_advisory_precedence_verification.md) | **兆候→翌年故障の先行性(約1,700万個体、最大24.1倍)** | `scripts/mot_advisory_longitudinal.py` / `data/mot_advisory_longitudinal.tsv` |
| [151](151_high_rate_model_crosscheck.md) | 高率モデルと公開不具合記録の突き合わせ + **観測台帳** | — |

## 2. SPD本線(第1ラウンド、docs/99〜131)より前の索引

以下は旧README掲載の逐一リストをそのまま保存したものである(記述は当時のまま。最新判断は上記および README.md が優先する)。
リンク先の相対パスはこのファイルの位置に合わせて修正した。実体が消えたHTML(旧デモの一部)は「削除済み」と付記してリンクを外してある。

まず読むなら、この順番が分かりやすい。

1. [docs/61_llm_kill_knowledge_base.md](61_llm_kill_knowledge_base.md): 次のLLMが最初に読む前提知識。Kill済み仮説、再提案禁止、再開条件、前提変更時にだけ復活する候補を整理。
1. [data/llm_kill_knowledge_base.tsv](../data/llm_kill_knowledge_base.tsv): Kill済み仮説ごとの現行判断、Kill理由、再主張禁止、再開条件、LLM向けルール。
1. [docs/97_trust_recovery_rule_check_audit.md](97_trust_recovery_rule_check_audit.md): 信用回復監査。過去のStop/Kill/Archive報告を上位ルールで再監査し、最新判断として使う文書、補正前として扱う文書、Rule Check付きで再引用する文書を分類。
1. [data/trust_recovery_rule_check_audit.tsv](../data/trust_recovery_rule_check_audit.tsv): 信用回復監査のTSV。各文書のcurrent use status、Rule Check status、main issue、corrected use、action takenを整理。
1. [docs/98_business_model_mainline_after_correction.md](98_business_model_mainline_after_correction.md): 補正後のビジネスモデル本線。故障予測ではなく、OEM用途想定をEPSサプライヤの製品企画・診断企画・品質改善・評価企画・顧客技術説明へ翻訳できるかを見る固定スコープassessmentとして整理。
1. [data/business_model_mainline_after_correction.tsv](../data/business_model_mainline_after_correction.tsv): 補正後ビジネスモデル本線の市場需要、痛み、仮説、解決策、買い手、初期offer、Proceed/Kill条件、禁止主張、次アクションを整理。
1. [docs/100_oem_usage_translation_minimum_pack.md](100_oem_usage_translation_minimum_pack.md): OEM用途想定をEPS側の確認観点、提案観点、説明境界へ翻訳する4枚の最小パック。製品企画、診断企画、品質改善/評価企画、診断企画/サイバー担当の順でサプライヤ内レビューする。
1. [data/oem_usage_translation_minimum_pack.tsv](../data/oem_usage_translation_minimum_pack.tsv): 4枚の最小パックのartifact別TSV。decision question、OEM入力、public proxy role、EPS supplier output、Proceed/Kill signal、禁止主張、最初のレビュー質問を整理。
1. [docs/101_oem_usage_translation_review_questions.md](101_oem_usage_translation_review_questions.md): 4枚の最小パックをサプライヤ内で確認する質問票。最初は製品企画と診断企画に絞り、既存RFQ回答、既存診断、既存評価との差分が出るかを見る。
1. [data/oem_usage_translation_review_questions.tsv](../data/oem_usage_translation_review_questions.tsv): 質問票のTSV。question、聞く理由、期待成果物、Proceed signal、Kill signal、禁止主張、Yes/No時の次アクションを整理。
1. [docs/102_bosch_motion_domain_ai_signal_review.md](102_bosch_motion_domain_ai_signal_review.md): Bosch公開情報を、EPS故障予測ではなく、by-wire / motion-domain時代の操舵側説明責任が増えるシグナルとして整理したレビュー。
1. [data/bosch_motion_domain_ai_signal_review.tsv](../data/bosch_motion_domain_ai_signal_review.tsv): Bosch公開情報のソース別TSV。public signal、公開されていること、EPSサプライヤへの含意、禁止主張、次の検証質問を整理。
1. [docs/103_bosch_predictive_diagnostics_meaning_review.md](103_bosch_predictive_diagnostics_meaning_review.md): Boschが言う予測を、fleet predictive maintenance、Predictive Diagnostics、Cloud and predictive diagnostics、AI cockpitに分解し、steering predictive diagnostics / predictive maintenance / vehicle healthとして扱う条件を整理したレビュー。
1. [data/bosch_predictive_diagnostics_meaning_review.tsv](../data/bosch_predictive_diagnostics_meaning_review.tsv): Bosch予測診断シグナルのソース別TSV。prediction type、予測対象、入力feature、出力action、EPSサプライヤ含意、禁止主張、次の質問を整理。
1. [docs/104_steering_predictive_state_candidate_scan.md](104_steering_predictive_state_candidate_scan.md): Boschの予測語をこのブランチでは正面から扱い、公開サービス情報やNHTSA資料から、steering predictive state候補を整理した調査。
1. [data/steering_predictive_state_candidates.tsv](../data/steering_predictive_state_candidates.tsv): steering predictive state候補のTSV。熱保護、低/高電圧、過温度、外部signal異常、複合電気症状、DTC coverage、DTC履歴について、材料、予測価値、用途、禁止主張、次checkを整理。
1. [docs/105_bosch_predictive_business_analysis.md](105_bosch_predictive_business_analysis.md): Boschの予測ビジネスを、接続、クラウド診断、predictive diagnostics、predictive maintenance、vehicle health、整備計画、保証・品質判断までの業務パッケージとして再整理した分析。
1. [data/bosch_predictive_business_analysis.tsv](../data/bosch_predictive_business_analysis.tsv): Bosch予測ビジネスの層別TSV。fleet maintenance、cloud diagnostics、predictive diagnostics、data-driven intelligence、Uptake、battery、brake、powertrain、connectivityをEPSサプライヤ含意へ変換。
1. [docs/106_steering_predictive_diagnostics_screening_plan.md](106_steering_predictive_diagnostics_screening_plan.md): 次アクション実施計画。Bosch公式ソースURLを固定し、操舵系predictive diagnostics候補をstate、必要データ、整備action、vehicle health output、禁止主張へ切る手順を整理。
1. [docs/107_steering_predictive_diagnostics_state_screening.md](107_steering_predictive_diagnostics_state_screening.md): Phase 1/2の実行結果。Bosch型予測ビジネス要求を操舵系screening要求へ変換し、SPS001-SPS007をmaintenance action、vehicle health output、diagnostic triage、quality/warranty investigationへ並べ替えた。
1. [data/steering_predictive_diagnostics_screening_requirements.tsv](../data/steering_predictive_diagnostics_screening_requirements.tsv): Bosch予測ビジネスのBBA001-BBA010を、操舵系screening requirementへ変換したTSV。
1. [data/steering_predictive_diagnostics_state_screening.tsv](../data/steering_predictive_diagnostics_state_screening.tsv): 操舵系predictive state候補のscreening TSV。Proceed / Hold / dependency、Bosch output fit、禁止主張、次checkを整理。
1. [docs/108_steering_predictive_diagnostics_proceed_deep_dive.md](108_steering_predictive_diagnostics_proceed_deep_dive.md): Proceed候補の深掘り。SPD002、SPD004、SPD003、SPD001、SPD007の順で、EPSサプライヤが定義できること、OEM/fleet/platform依存、vehicle health output、maintenance action、Hold/Kill riskを整理。
1. [data/steering_predictive_diagnostics_proceed_deep_dive.tsv](../data/steering_predictive_diagnostics_proceed_deep_dive.tsv): Proceed深掘りTSV。各stateのwhy proceed、必要依存、提案output、次artifactを整理。
1. [docs/109_steering_predictive_diagnostics_data_boundary.md](109_steering_predictive_diagnostics_data_boundary.md): Phase 3結果。Proceed候補5件について、必要DTC、freeze frame / extended data、limit state、温度・電源・通信context、repair feedback loop、EPSサプライヤが言えること/言えないことを整理。
1. [data/steering_predictive_diagnostics_data_boundary.tsv](../data/steering_predictive_diagnostics_data_boundary.tsv): Phase 3 data boundary TSV。各stateの必要データ、OEM/fleet/platform依存、RUL/交換時期を言わない境界、次checkを整理。
1. [docs/110_steering_predictive_diagnostics_supplier_workflow_fit.md](110_steering_predictive_diagnostics_supplier_workflow_fit.md): Phase 4結果。Phase 3のdata boundaryを、診断企画、品質改善、顧客技術説明、service / aftermarket連携、製品企画、評価企画の成果物へ転記できるかを確認。
1. [data/steering_predictive_diagnostics_supplier_workflow_fit.tsv](../data/steering_predictive_diagnostics_supplier_workflow_fit.tsv): Phase 4 supplier workflow fit TSV。部署別の成果物、価値、重複リスク、Proceed signal、Hold/Stop signal、禁止主張、次stepを整理。
1. [docs/111_steering_predictive_diagnostics_screening_decision.md](111_steering_predictive_diagnostics_screening_decision.md): Phase 5最終判断。操舵系predictive diagnosticsは、固定スコープの内部/顧客技術向けassessmentとしてProceed。EPS RUL/交換時期予測、Bosch型fleet platform、安全保証、root cause / warranty cost reductionはProceedしない。
1. [data/steering_predictive_diagnostics_screening_decision.tsv](../data/steering_predictive_diagnostics_screening_decision.tsv): Phase 5 decision TSV。Market demand、未解決の痛み、仮説、解決策、買い手、EPSサプライヤの手札、Demo、Kill criteriaを整理。
1. [docs/112_steering_predictive_diagnostics_parallel_continuation_deep_dive.md](112_steering_predictive_diagnostics_parallel_continuation_deep_dive.md): 継続候補の並列深掘り。SPD002/003/004/001/007に加え、内部重要モジュールruntime deviation案をSPD008として扱い、E2E製品全体ではなく内部モジュール単位に限定して検証する方針を整理。
1. [data/steering_predictive_diagnostics_parallel_continuation.tsv](../data/steering_predictive_diagnostics_parallel_continuation.tsv): 並列深掘りTSV。各候補の自然言語の問い、継続理由、module scope、E2Eにしない理由、成果物、Proceed signal、Hold/Stop signal、禁止主張を整理。
1. [docs/113_steering_predictive_diagnostics_promising_candidate_deep_dive.md](113_steering_predictive_diagnostics_promising_candidate_deep_dive.md): 見込み候補の深掘り。SPD008を伸びしろ、SPD002を実証しやすさ、SPD003を実務価値、SPD004をvehicle health接続として整理し、SPD001/007も状況と判断理由を明示。
1. [data/steering_predictive_diagnostics_promising_candidate_deep_dive.tsv](../data/steering_predictive_diagnostics_promising_candidate_deep_dive.tsv): 見込み候補深掘りTSV。各候補のstatus、判断、見込み理由、不足理由、成果物、初回テスト、Proceed/Hold/Stop境界、禁止主張を整理。
1. [docs/114_steering_predictive_diagnostics_spd_final_conclusions.md](114_steering_predictive_diagnostics_spd_final_conclusions.md): SPD別の一定結論。SPD008を本命候補、SPD002を実証demo、SPD003を近い実務支援、SPD004を戦略オプション、SPD001を低優先、SPD007を条件付き再開として整理。
1. [data/steering_predictive_diagnostics_spd_final_conclusions.tsv](../data/steering_predictive_diagnostics_spd_final_conclusions.tsv): SPD別最終結論TSV。final decision、market demand、unresolved pain、hypothesis、artifact、buyer/user、Proceed/Hold/Stop境界、禁止主張、次アクションを整理。
1. [docs/115_steering_predictive_diagnostics_spd008_runtime_deviation_map.md](115_steering_predictive_diagnostics_spd008_runtime_deviation_map.md): SPD008のinternal module runtime deviation map。5つの内部重要モジュールについて、既存monitorとの差分、deviation候補、追加ログtrigger、転記先を整理。
1. [data/steering_predictive_diagnostics_spd008_runtime_deviation_map.tsv](../data/steering_predictive_diagnostics_spd008_runtime_deviation_map.tsv): SPD008 map TSV。module別にinput/output、comparison basis、existing monitor、deviation candidate、diagnostic/quality/customer use、Proceed/Hold条件を整理。
1. [docs/116_steering_predictive_diagnostics_spd002_one_case_reading_order.md](116_steering_predictive_diagnostics_spd002_one_case_reading_order.md): SPD002のone-case diagnostic reading order。低/高電圧または過温度によるreduced assistを、DTC、電圧、温度、assist mode、key cycle、repair feedback requirementの順に読むsample。
1. [data/steering_predictive_diagnostics_spd002_one_case_reading_order.tsv](../data/steering_predictive_diagnostics_spd002_one_case_reading_order.tsv): SPD002 reading order TSV。step別のquestion、data to read、why this order、interpretation、service/customer output、feedback requirement、禁止主張を整理。
1. [docs/117_steering_predictive_diagnostics_spd008_vs_spd002_decision.md](117_steering_predictive_diagnostics_spd008_vs_spd002_decision.md): SPD008とSPD002の比較判断。SPD008を次の本線候補、SPD002をreference demoに置く判断を整理。SPD008は診断資料作成ではなく、内部重要モジュールのruntime状態説明がpredictive diagnostics / vehicle healthの部品側contributionになるかを見る。
1. [data/steering_predictive_diagnostics_spd008_vs_spd002_decision.tsv](../data/steering_predictive_diagnostics_spd008_vs_spd002_decision.tsv): SPD008 vs SPD002比較TSV。伸びしろ、実証しやすさ、既存業務との差分、依存、Proceed/Hold/Stop、禁止主張を整理。
1. [docs/118_steering_predictive_diagnostics_spd008_first_samples.md](118_steering_predictive_diagnostics_spd008_first_samples.md): SPD008 first samples。power monitorとcommunication input validityについて、DTC未満のsoft contextを内部重要モジュールのruntime状態説明として扱えるか、既存monitorとの差分やvehicle healthへの部品側contributionがあるかを整理。
1. [data/steering_predictive_diagnostics_spd008_first_samples.tsv](../data/steering_predictive_diagnostics_spd008_first_samples.tsv): SPD008 first samples TSV。sample別にevent pattern、soft deviation、existing monitor boundary、additional log trigger、runtime state explanation、vehicle health contribution、Proceed/Hold条件、禁止主張を整理。
1. [docs/119_steering_predictive_diagnostics_viewpoint_correction.md](119_steering_predictive_diagnostics_viewpoint_correction.md): SPD008観点補正。診断企画向け1枚schemaを目的にせず、runtime状態説明とpredictive diagnostics / vehicle healthへの部品側contributionを先に確認するルールとNext Actionを整理。
1. [docs/120_steering_predictive_diagnostics_spd008_predictive_value_check.md](120_steering_predictive_diagnostics_spd008_predictive_value_check.md): SPD008 predictive value check。power monitorを第一検証候補、communication input validityを第二検証候補に置き、既存monitorとの差分、runtime状態説明、vehicle healthへの部品側contribution、買い手業務、禁止主張を整理。
1. [data/steering_predictive_diagnostics_spd008_predictive_value_check.tsv](../data/steering_predictive_diagnostics_spd008_predictive_value_check.tsv): SPD008 predictive value check TSV。sample別にjudgment、runtime state、existing monitor difference、vehicle health contribution、business output、Proceed/Hold/Stop、禁止主張、次アクションを整理。
1. [docs/121_steering_predictive_diagnostics_power_monitor_case.md](121_steering_predictive_diagnostics_power_monitor_case.md): Power monitor 1ケース。短い電圧dip / near-reset contextとassist limitationの近接について、既存monitorで残る項目、残らない可能性、vehicle health向け状態説明、限定Proceed / Hold / Stop条件を整理。
1. [data/steering_predictive_diagnostics_power_monitor_case.tsv](../data/steering_predictive_diagnostics_power_monitor_case.tsv): Power monitor case TSV。under-voltage DTC、reset log、power supply fault、freeze frame / extended data、assist mode / limit state、key cycle recurrenceごとに、既存monitorとの差分と次確認項目を整理。
1. [docs/122_steering_predictive_diagnostics_power_monitor_payload_sample.md](122_steering_predictive_diagnostics_power_monitor_payload_sample.md): Power monitor payload sample。既存monitorで十分かを先に判定し、不足がある場合だけvehicle health向け最小payloadへ進むための確認項目、payload候補、Decision Gateを整理。
1. [data/steering_predictive_diagnostics_power_monitor_payload_sample.tsv](../data/steering_predictive_diagnostics_power_monitor_payload_sample.tsv): Power monitor payload sample TSV。check item、payload field、decision gateごとに、既存monitorで十分な条件、gap、payload use、Proceed/Hold/Stop、禁止主張を整理。
1. [docs/123_steering_predictive_diagnostics_power_monitor_program_question_sheet.md](123_steering_predictive_diagnostics_power_monitor_program_question_sheet.md): Power monitor program別照合質問シート。AUTOSAR標準で残せる設定余地を前提に、対象programが実際に残しているかを聞く形へ補正。判定ロジックと公開情報で埋められる一般論を整理。
1. [data/steering_predictive_diagnostics_power_monitor_program_question_sheet.tsv](../data/steering_predictive_diagnostics_power_monitor_program_question_sheet.tsv): 照合質問シートTSV。check item × 質問軸ごとに、質問、聞く理由、回答元、十分条件、差分条件、payload field、禁止主張を整理。program固有欄は空欄で渡す。
1. [docs/124_steering_predictive_diagnostics_comm_input_validity_case.md](124_steering_predictive_diagnostics_comm_input_validity_case.md): Communication input validityの独立ケース。hard communication DTC未満の揺らぎとfallback近接について、既存monitor(IdsM含む)との差分、最小payload、条件付きHold(Proceed寄り)の判定を整理。
1. [data/steering_predictive_diagnostics_comm_input_validity_case.tsv](../data/steering_predictive_diagnostics_comm_input_validity_case.tsv): Communication input validity case TSV。timeout DTC、bus-off、invalid value、E2E保護、fallback state、IdsM、recurrenceごとに差分条件と判定を整理。
1. [docs/125_steering_predictive_diagnostics_unverified_delta_check.md](125_steering_predictive_diagnostics_unverified_delta_check.md): 未検証デルタのファクトチェック。既存monitor比、汎用テレマティクス比、IDS比の差分主張を公開情報で検証し、価値主張の言い直しとSPD002の意図的凍結を記録。
1. [data/steering_predictive_diagnostics_unverified_delta_check.tsv](../data/steering_predictive_diagnostics_unverified_delta_check.tsv): デルタ検証TSV。delta claim、公開事実、検証結果、残る差分、言い直し後の表現、Kill条件への接続を整理。
1. [docs/126_steering_predictive_diagnostics_sotif_contribution_prospect.md](126_steering_predictive_diagnostics_sotif_contribution_prospect.md): SOTIFへの乗り方の判定。プロセス支援はNo-Go、論証証拠は既存業務、運用フェーズのフィールド監視への部品側インプットだけ条件付き検証候補。KQ1〜KQ5の入口条件と故障予測Kill維持を整理。
1. [data/steering_predictive_diagnostics_sotif_contribution_prospect.tsv](../data/steering_predictive_diagnostics_sotif_contribution_prospect.tsv): SOTIF prospect TSV。3つのoption判定、KQ1〜KQ5、EPS視点triggering condition候補、故障予測Kill維持を整理。
1. [docs/127_steering_predictive_diagnostics_target_case_public_evidence.md](127_steering_predictive_diagnostics_target_case_public_evidence.md): ターゲットケースの公開実在確認。Ford 15V-340のDTC有無2経路是正、GM 17V-414の一時喪失・突然復帰、GM TSB 17-NA-158の外部signal起因警告、Tesla過電圧調査などから「DTCが残らない断続的assist低下」の実在をConfirmed。痛みの実在確認であり商品価値の証明ではない、という限界も明記。
1. [data/steering_predictive_diagnostics_target_case_public_evidence.tsv](../data/steering_predictive_diagnostics_target_case_public_evidence.tsv): 公開証拠TSV。リコール是正・ODI調査・TSB・整備情報ごとに、公開事実、SPDとの関係、支持内容、限界、confidenceを整理。
1. [docs/128_steering_predictive_diagnostics_sotif_public_signal_watch.md](128_steering_predictive_diagnostics_sotif_public_signal_watch.md): SOTIF公開シグナル観測。ISO 21448のSOTIF-EooC(部品サプライヤの公式参加形式)、Bosch定量SOTIF特許、by-wire量産・L3展開を確認し、KQ1の公算を補強。SOTIF枝は実施条件待ちのまま、KQ1の質問形をEooC仮定ベースへ具体化。
1. [docs/129_steering_predictive_diagnostics_public_case_crosscheck.md](129_steering_predictive_diagnostics_public_case_crosscheck.md): 判定ゲートの公開ケース照合。Ford 15S18とGM 17276の一次文書精読により、是正実務の判断材料がDTC有無の1bitのみで、DTC未満event・snapshot・同時性・再発が存在しないことを確認。SPD008価値仮説を公開情報のみでConfirmedし、内部資料条件を実行のみに縮小。
1. [data/steering_predictive_diagnostics_public_case_crosscheck.tsv](../data/steering_predictive_diagnostics_public_case_crosscheck.tsv): 公開ケース照合TSV。5照合項目+誤診コスト実在+判定を、公開文書の記述、差分確認、SPDへの含意、限界とともに整理。
1. [docs/130_steering_predictive_diagnostics_comm_validity_public_crosscheck.md](130_steering_predictive_diagnostics_comm_validity_public_crosscheck.md): comm input validityの公開ケース照合。GM TSB 17-NA-158原文で依存signal起因の誤交換連鎖を確認し、Hold→公開レベルConfirmed付き限定Proceedへ。TSB=SPD008 payloadの人手版という言い直しと、Ford SSM 49530による2021年世代の誤帰属継続確認を含む。
1. [data/steering_predictive_diagnostics_comm_validity_public_crosscheck.tsv](../data/steering_predictive_diagnostics_comm_validity_public_crosscheck.tsv): comm validity公開照合TSV。保持・切り分け・説明・近接・再発・依存定義の主導権・現行世代誤帰属・判定を整理。
1. [docs/131_steering_predictive_diagnostics_checkpoint_summary.md](131_steering_predictive_diagnostics_checkpoint_summary.md): **区切りまとめ(まずこれを読む)**。IDを使わない自然言語での仮説と結論、ID対訳表、検証ストーリー、最終判定表、残る実行条件(すべて内部資料条件)を1本に集約。
1. [docs/132_steering_predictive_diagnostics_payload_replay_demo.md](132_steering_predictive_diagnostics_payload_replay_demo.md): 具体化デモ。公開3ケースを最小payloadで再演し、実務の判断材料(DTC 1bit / 誤帰属code)と「その場で出せた状態説明」を対比。禁止主張を機械的に拒否する境界ガードの動作確認込み。実行は `python3 scripts/spd008_payload_replay.py`、出力は [generated/spd008_payload_replay.html](../generated/spd008_payload_replay.html)。
1. [docs/133_failure_prediction_demand_map.md](133_failure_prediction_demand_map.md): 故障予測の需要マップ。買い手6セグメント別に、欲しい予測の形・粒度・必要データ・既存プレイヤー・EPSサプライヤの入り口を整理。個車レベルの席は埋まっており、空席は(1)部品内部のDTC未満信号(検証済み)と(2)群レベルの故障傾向(公開データで未検証、次フェーズの本命)の2つ。
1. [data/failure_prediction_demand_map.tsv](../data/failure_prediction_demand_map.tsv): 需要マップTSV。セグメント×(予測の形、粒度、データ所有、既存プレイヤー、入り口、公開Demo可否、判定)。
1. [docs/134_group_level_data_feasibility.md](134_group_level_data_feasibility.md): 群レベル曲線のデータ当たり付け。NHTSA苦情API(実働確認済み)を主データ、既知リコールを答え合わせ、DVSA MOT(分母付き)を拡張とし、フェーズC Goを判定。分母なし・報告バイアスの限界を明記。
1. [data/group_level_data_feasibility.tsv](../data/group_level_data_feasibility.tsv): データ当たり付けTSV。源別に実在確認、粒度、分母有無、曲線への使い方、限界、ライセンス、判定を整理。
1. [docs/135_steering_cohort_curve_demo_verdict.md](135_steering_cohort_curve_demo_verdict.md): **群レベルcohort曲線Demoの判定(答え合わせ成功)**。Ford Fusion 5年式・13,862件の公開苦情の盲検集計で、リコール対象cohort(MY2011-2012)の操舵系比率51.2%/57.7%が比較cohort(21.5%/24.2%)の2倍以上に浮き、公式リコール事実を再現。実行は `python3 scripts/steering_cohort_curve.py`、出力は [generated/steering_cohort_curve.html](../generated/steering_cohort_curve.html)。報告バイアスの可視化と限界(分母なし、事後検証である点)も明記。
1. [data/steering_cohort_curve_summary.tsv](../data/steering_cohort_curve_summary.tsv): cohort別サマリTSV。全苦情、操舵系件数、比率、車齢24/48/72/120ヶ月時点の累積。
1. [docs/136_steering_cohort_backtest_verdict.md](136_steering_cohort_backtest_verdict.md): **時点区切りバックテストの判定(事前検知成功)**。事前固定した検知ルールで、MY2012はリコール公表25ヶ月前(ODI調査開始より約1年前)、MY2011は7ヶ月前に発火。非リコールcohortは発火せず偽陽性ゼロ。MY2010は届出遅延で検知不能=苦情ベース検知の限界として記録し、部品内部観測(SPD008)との相補性を確定。実行は `python3 scripts/steering_cohort_backtest.py`。
1. [data/steering_cohort_backtest.tsv](../data/steering_cohort_backtest.tsv): バックテストTSV。cutoff別のcohort比率・発火判定と、初回発火時点・リード月数。
1. [docs/137_residual_candidates_sweep.md](137_residual_candidates_sweep.md): 残候補4件の一括消化。**①Silverado横展開は負の結果(事前固定ルールが両リコールcohortをMISS=絶対閾値は車種を跨いで汎化しない)** ②故障モード分類は成功(Fusionの浮きの60〜62%がアシスト喪失モード)、モードベース監視をルール改訂候補に ③DVSA MOTは年10GB級・EPS固有分類の存在確認・保留 ④品質改善向け月次監視レポートのモック。
1. [data/steering_cohort_backtest_silverado.tsv](../data/steering_cohort_backtest_silverado.tsv): Silverado横展開のバックテストTSV。
1. [data/steering_mode_split.tsv](../data/steering_mode_split.tsv): 故障モード分類TSV。車種×cohort別にアシスト喪失/騒音・振動/流れ・ふらつき/コラム・ロック/その他の件数とモード比率。
1. [docs/138_business_model_definition.md](138_business_model_definition.md): **ビジネスモデル定義**。3層構造(第1層=状態説明機能つきEPS製品仕様をOEMへRFQ差別化+診断コンテンツNREとして売る唯一の収益線、第2層=市場シグナル監視は内部投資、第3層=assessmentはprogram付帯NREのみ)。金の流れ、競争優位、既往Killとの整合、事業のKill条件(BM-KQ1〜4)を定義。技術検証が「問題への手当て」で終わらないための土台。
1. [docs/139_log_sign_extraction_demo.md](139_log_sign_extraction_demo.md): **技術者向けLog兆候抽出デモ**。公開走行log(commaSteeringControl、MIT)938セグメントから、操舵応答の残差6特徴をrobust z-scoreで機械抽出(学習モデルなし・決定的・再現可能)。raw波形の目視では分からない兆候を検出し、payload形式の状態説明とSOTIF語彙(triggering condition候補、EooC仮定検証)へ機械変換。故障検出ではない境界を明記。実行は `python3 scripts/steering_log_sign_extraction.py`、出力は [generated/steering_log_sign_extraction.html](../generated/steering_log_sign_extraction.html)。
1. [data/steering_log_sign_extraction.tsv](../data/steering_log_sign_extraction.tsv): セグメント別特徴量TSV。6特徴の実値とz-score、max_abs_z、主特徴、有効サンプル、平均車速。
1. [docs/140_recall_detection_protocol.md](140_recall_detection_protocol.md): **実証モデルAの事前登録プロトコル**(特徴量計算前にコミット)。cohort定義、ラベル(操舵系リコール537campaign)、時系列分割(2013-2018学習/2019-2024テスト)、特徴量6種、凍結操作点、成功/失敗の言い方まで事前固定。
1. [docs/141_recall_detection_results.md](141_recall_detection_results.md): **実証モデルA結果(v1)**。事前登録基準は未達(precision 0.39/recall 0.17)→不成立とそのまま報告。ただし信号は実在(テストPR-AUC 0.315=無情報2.9倍、ROC-AUC 0.783、手作りルール比大幅改善)。最大の課題はリコール台帳×苦情DBのモデル名マッチ率21%。
1. [docs/142_recall_detection_protocol_v2.md](142_recall_detection_protocol_v2.md): v2改訂の事前登録(実行前コミット)。マッチ率21%の正体=商用車・バス等が苦情DB圏外(乗用車系makeなら完全一致94%)→スコープをconsumer make 29社に是正、rel_makeを差に再設計、EPS系サブセット評価を追加。テストへの2回目アクセスであることを明示。
1. [docs/151_high_rate_model_crosscheck.md](151_high_rate_model_crosscheck.md): **高率モデルの突き合わせ(答え合わせ3例目・成立)**。Corsa=公知のEPSコラム故障+リコール複数(断続アシスト喪失が米2市場に続き3例目)、バン勢=用途起因の摩耗。能動的な公開検証はここで完了し、以後は観測台帳(競合・将来リコール・新興車齢・日本OBD DB・規制実装)のみ。
1. [docs/150_advisory_precedence_verification.md](150_advisory_precedence_verification.md): **兆候→翌年故障の先行性検証(成立・本研究最強の結果)**。英国車検2年分を個体連結(約1,700万台)し、不合格未満の記録だけが付いた個体は翌年の操舵系不合格率が最大24倍。若い車では不合格→修理群より高率=「不合格未満の層は最も予測力があり最も放置されている」。この研究の価値仮説の実証的言い換え。
1. [docs/149_concentration_ev_and_japan.md](149_concentration_ev_and_japan.md): **偏り・EV・日本データの検証**。英国2025年の操舵系不合格は10モデルで50%を占有(偏在は強烈=群監視の単位は車種×年式で正しい)。EV/新興メーカーは年齢補正後で中位、異常なし。日本は集計PDFのみ(かじ取り99件/年)で、苦情ベース群監視は日本では成立しにくいという地域差を記録。
1. [docs/148_dvsa_mot_denominator_verification.md](148_dvsa_mot_denominator_verification.md): **分母つき群曲線の再検証(成立)**。英国車検2025年・乗用車2,800万件の全数データで、操舵系不合格率は車齢とともに約40倍まで単調増加。米国苦情曲線の「形」を独立の制度・分母つきで再現。生存バイアス・コード化の癖・比較の限界を明記。
1. [docs/147_multiplatform_and_variant_verification.md](147_multiplatform_and_variant_verification.md): **多車種展開と実在変種比較**。波形感度は4車種で質的に再現(数値は車種固有、較正前提を仕様として明記)。実在の部品/ソフト版数グループの分離は使い方の交絡に埋もれ不成立と報告——「個体内の縦断監視が本命」に3つ目の独立経路で到達。
1. [docs/146_business_framework_and_roadmap.md](146_business_framework_and_roadmap.md): **ビジネスの枠組みと段取り(外部証拠だけで組み立てた版)**。判断1: 今は差別化として金になる時限の窓であり、いずれ当然要求に落ちる(根拠: Nexteer MotionIQ/Healthの商品化・量産開発=支払い意思の外部証拠、Bosch買収、規制の時間表、先例3類型)。判断2: 「空席」は部品ごとの席に修正。値付け3案の比較、判断の誤り条件まで明記。段取りは改訂済み: 公開・発信を伴う段(反応測定・業界発表)はユーザ判断で取り下げ、残るのは競合・規制の受動観測と将来リコールeraでの再検証のみ。
1. [docs/145_final_conclusions_and_interpretations.md](145_final_conclusions_and_interpretations.md): **最終結論と解釈集**。技術=成立(定量実証済み、実車実証のみ内部領域)/ビジネス=構造定義済み・最終判定はBM-KQ2に集約(内部領域)。数字の読み方(単窓感度は床、recallの構造的天井、3.2倍の使い方、A+Bの挟み撃ちと未架橋の中央、option価値、不成立判定の信頼性)を記録。
1. [docs/144_synthetic_sensitivity_results.md](144_synthetic_sensitivity_results.md): **実証モデルB結果**。合成劣化注入による波形パイプラインの検出限界: 誤検出6.7%の操作点で、応答遅れ0.4s/ゲイン変化15%/定常バイアス0.05m/s²を90%以上検出(合成条件下)。検出不能領域も対等に報告。HTMLレポートは [generated/steering_synthetic_sensitivity.html](../generated/steering_synthetic_sensitivity.html)。モデルAのHTMLレポートは [generated/recall_detection_report.html](../generated/recall_detection_report.html)。
1. [docs/143_recall_detection_results_v2.md](143_recall_detection_results_v2.md): **実証モデルA確定判定**。v2でも僅差未達(precision 0.48/recall 0.26)→「公開苦情のみでは実用シグナル不成立」で確定し、テスト3回目を封印(次の検証データは2025年以降の将来リコールera)。確定知見: 無情報の3.2倍の並べ替え効率、リード×精度トレードオフ、適用範囲=乗用車系のみ、EPS系予兆は苦情から最も見えにくい。第2層は「注意配分の道具」と位置づけ確定。
1. [docs/68_repo_closure_inventory.md](68_repo_closure_inventory.md): Repoを閉じるかどうかの人間向け棚卸し。探索枝ごとの現行判断、残す価値、再開条件、Close推奨を整理。
1. [data/repo_closure_inventory.tsv](../data/repo_closure_inventory.tsv): 探索枝ごとのmarket signal、tested artifact、latest decision、why not proceed、residual value、reopen condition、source docsを整理したTSV。
1. [docs/archive/oem_remote_diagnostics/78_oem_remote_diagnostics_eps_explanation_layer_hypothesis.md](archive/oem_remote_diagnostics/78_oem_remote_diagnostics_eps_explanation_layer_hypothesis.md): 新しい作業仮説。OEM remote diagnostics networkに組み込むEPS/SbW内部データ由来の操舵系状態説明レイヤー。
1. [data/archive/oem_remote_diagnostics/oem_remote_diagnostics_eps_explanation_layer_questions.tsv](../data/archive/oem_remote_diagnostics/oem_remote_diagnostics_eps_explanation_layer_questions.tsv): 新仮説の検証質問。data field、既存remote diagnosticsとの差分、service outcome、責任境界、成果物転記を確認する。
1. [docs/archive/oem_remote_diagnostics/80_oem_remote_diagnostics_validation_plan.md](archive/oem_remote_diagnostics/80_oem_remote_diagnostics_validation_plan.md): 新仮説の検証計画。Network参加可能性、必要data field、既存remote diagnosticsとの差分、service outcome、責任境界、1ケースsampleへ分解。
1. [data/archive/oem_remote_diagnostics/oem_remote_diagnostics_validation_items.tsv](../data/archive/oem_remote_diagnostics/oem_remote_diagnostics_validation_items.tsv): RDI001〜RDI006の調査item。Network参加経路を最初のKill gateとして整理。
1. [docs/archive/oem_remote_diagnostics/81_rdi001_006_research_report.md](archive/oem_remote_diagnostics/81_rdi001_006_research_report.md): RDI001〜RDI006を公開情報で調査した結果。Network参加経路はあるがopenではなく、公開APIだけではEPS/SbW固有data fieldとservice outcome feedbackが弱い。
1. [data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi_research_findings.tsv](../data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi_research_findings.tsv): RDI001〜RDI006のitem別結論、根拠、反証、Proceed条件、Kill条件を整理したTSV。
1. [docs/archive/oem_remote_diagnostics/82_rdi006_thermal_limit_4_column_sample.md](archive/oem_remote_diagnostics/82_rdi006_thermal_limit_4_column_sample.md): thermal limit / assist limitationの1ケースsample。DTCだけ、既存remote diagnostics、EPS/SbW内部説明、OEM service noteを比較し、差分が出る条件を整理。
1. [data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_thermal_limit_sample.tsv](../data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_thermal_limit_sample.tsv): RDI006 sampleのstep別4列比較。event snapshot、cool-down、repeated event、software/calibration、service outcome feedbackを整理。
1. [data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_program_gap_template.tsv](../data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_program_gap_template.tsv): 実programまたは想定programで穴埋めする確認表。読めるdata field、既存action plan、追加説明、service note転記先、outcome feedback、責任境界を確認する。
1. [docs/archive/oem_remote_diagnostics/83_rdi006_program_gap_pdca.md](archive/oem_remote_diagnostics/83_rdi006_program_gap_pdca.md): RDI006 program gapをPDCAで穴埋めしたレポート。当時はConditional Continue / not offerに縮小したが、内部資料なしルールではArchive判断の根拠として扱う。
1. [data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_program_gap_filled.tsv](../data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_program_gap_filled.tsv): 穴埋め完了版。10項目ごとにfilled status、必要artifact、owner、Proceed/Kill signal、EPS supplier decisionを整理。
1. [data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_pdca_log.tsv](../data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_pdca_log.tsv): PDCA 4周分のPlan / Do / Check / Actと判断変化。
1. [docs/archive/motion_health/79_motion_health_archive_index.md](archive/motion_health/79_motion_health_archive_index.md): motion health / fleet運行可否調査をArchive化した索引。新仮説で使える知見と使ってはいけない主張を整理。
1. [data/archive/motion_health/motion_health_archive_links.tsv](../data/archive/motion_health/motion_health_archive_links.tsv): Archive化したsource link、使い方、限界を整理したTSV。
1. [docs/archive/motion_health/69_old_theme_archive_and_new_focus.md](archive/motion_health/69_old_theme_archive_and_new_focus.md): 旧テーマをArchiveし、新テーマを「自動運転・商用車両群向けの操舵系運行可否/点検優先度判断」に絞るための入口。
1. [data/archive/motion_health/motion_health_new_focus_questions.tsv](../data/archive/motion_health/motion_health_new_focus_questions.tsv): 新テーマで最初に確認する10個の検証質問。買い手、痛み、データアクセス、判断出力、Kill条件を整理。
1. [docs/archive/motion_health/70_motion_health_mhq001_005_research_report.md](archive/motion_health/70_motion_health_mhq001_005_research_report.md): 新テーマの検証質問1〜5を公開情報で確認したレポート。fleet一般の需要は強いが、操舵系固有の痛みとサプライヤのデータアクセスは追加検証が必要。
1. [data/archive/motion_health/motion_health_mhq001_005_evidence.tsv](../data/archive/motion_health/motion_health_mhq001_005_evidence.tsv): MHQ001〜005向けのsource、evidence signal、support、limit、confidence、URLを整理したTSV。
1. [docs/archive/motion_health/72_mhq001_20min_deep_dive.md](archive/motion_health/72_mhq001_20min_deep_dive.md): MHQ001を20分枠で深掘りしたメモ。fleet downtimeとAV maintenanceは強いが、steering単独では弱く、chassis / motion healthとしても `Hold / Continue Investigation` に留める判断。
1. [docs/archive/motion_health/73_mhq001_second_20min_deep_dive.md](archive/motion_health/73_mhq001_second_20min_deep_dive.md): MHQ001を再深掘りし、`Proceed` を `Hold / Continue Investigation` に下げた修正版。steering-onlyの購買painは未確認で、chassis / motion healthとしてのみ継続。
1. [docs/archive/motion_health/74_mhq003_005_deep_dive_for_mhq001.md](archive/motion_health/74_mhq003_005_deep_dive_for_mhq001.md): MHQ003のdata accessとMHQ005の既存remote diagnostics差分を深掘りし、MHQ001を `Hold / Stop-leaning` に下げた判断。次の1ケースsampleで差分が出なければStop。
1. [docs/archive/motion_health/75_motion_health_mhq001_final_decision.md](archive/motion_health/75_motion_health_mhq001_final_decision.md): MHQ001の最終判断。fleet downtime需要はあるが、data accessと既存remote diagnosticsとの差分が公開情報だけでは証明できないため、外販テーマとしてはStop / Archive。
1. [docs/archive/motion_health/76_other_mhq_20min_deep_dive.md](archive/motion_health/76_other_mhq_20min_deep_dive.md): MHQ001以外のMHQ002/004/006/007/008/009/010を20分枠で深掘りした最終補強メモ。市場側のYesはあるが、外販Stop判断は変わらない。
1. [docs/archive/motion_health/77_mhq004_007_008_deeper_review.md](archive/motion_health/77_mhq004_007_008_deeper_review.md): MHQ004/007/008を追加深掘りし、外販ではなく再開条件として残す判断を整理。MHQ004はoutput rubric、MHQ007はbundle boundary、MHQ008はfield-to-engineering feedbackとして保存。
1. [data/archive/motion_health/motion_health_mhq_work_surface.tsv](../data/archive/motion_health/motion_health_mhq_work_surface.tsv): MHQ001〜010の作業面。各questionの現在結論、confidence、弱点、次アクション、priorityを整理。
1. [data/archive/motion_health/motion_health_mhq001_deep_dive_evidence.tsv](../data/archive/motion_health/motion_health_mhq001_deep_dive_evidence.tsv): MHQ001向けにfleet downtime general、AV maintenance、chassis/motion specific、steering specificのevidenceを分類したTSV。
1. [data/archive/motion_health/motion_health_mhq003_005_evidence.tsv](../data/archive/motion_health/motion_health_mhq003_005_evidence.tsv): MHQ003/MHQ005向けに、vehicle data access、OEM/API、supplier cloud連携、既存remote diagnostics、SOVDの反証材料を整理したTSV。
1. [data/archive/motion_health/motion_health_mhq001_final_kill_check_sample.tsv](../data/archive/motion_health/motion_health_mhq001_final_kill_check_sample.tsv): 高負荷操舵でEPS thermal limit / assist limitationに入った仮想ケースを、DTCだけ、既存remote diagnostics、supplier domain triageの3列で比較したKill確認sample。
1. [data/archive/motion_health/motion_health_other_mhq_deep_dive.tsv](../data/archive/motion_health/motion_health_other_mhq_deep_dive.tsv): MHQ002/004/006/007/008/009/010のitem別結論、support/counter-signal、EPS supplier decisionを整理したTSV。
1. [data/archive/motion_health/motion_health_mhq004_007_008_deeper.tsv](../data/archive/motion_health/motion_health_mhq004_007_008_deeper.tsv): MHQ004/007/008について、深掘り結論、support/counter-signal、再開条件、EPS supplier boundaryを整理したTSV。
1. [docs/66_return_to_eps_product_value_after_kaggle_branch.md](66_return_to_eps_product_value_after_kaggle_branch.md): Kaggle/Bosch線を需要調査の枝に下げ、本題をEPS製品価値へ戻すための判断。次候補はEPS診断コンテンツの次世代化。
1. [docs/67_next_generation_diagnostic_content_value_check.md](67_next_generation_diagnostic_content_value_check.md): EPS診断コンテンツの次世代化が製品仕様・診断仕様・RFQ回答に残るかをKill-firstで確認した最新メモ。SOVD基盤ではなく、公開範囲、権限、禁止主張、software/calibration接続だけを見る。
1. [data/next_generation_diagnostic_content_value_check.tsv](../data/next_generation_diagnostic_content_value_check.tsv): 25件の仮診断コンテンツを、次世代診断での見せ方、EPSサプライヤ境界、RFQ/仕様文言、禁止主張、Kill signalへ整理したproxy demo。
1. [docs/62_kaggle_competition_hidden_demand_review.md](62_kaggle_competition_hidden_demand_review.md): Kaggleコンペを、公開代替データではなく「企業が外に出した隠れた需要」として読み直した最新メモ。最有力はEPS市場故障ではなく、製造品質と評価時間短縮。
1. [data/kaggle_hidden_demand_candidates.tsv](../data/kaggle_hidden_demand_candidates.tsv): Bosch、Mercedes-Benz、OBD-II/CAN、Car-Hacking等を、隠れた需要、EPSサプライヤ適合、使ってはいけない主張、Kill条件で整理。
1. [docs/84_kaggle_problem_setting_lens.md](84_kaggle_problem_setting_lens.md): Kaggleを「データセット」ではなく、企業が外に出した問題設定として読む観点。目的変数、入力データ、評価指標から隠れた業務意図を読む。
1. [data/kaggle_problem_setting_lens.tsv](../data/kaggle_problem_setting_lens.tsv): Kaggle課題ごとに、何を読むか、隠れた意図、EPSサプライヤでの読み替え、使ってよい用途、使ってはいけない用途を整理。
1. [docs/85_kaggle_problem_setting_id_deep_dive.md](85_kaggle_problem_setting_id_deep_dive.md): Kaggle問題設定をKGL001〜KGL006に分け、各IDの結論、EPSサプライヤへの読み替え、Proceed/Kill条件、次アクションを整理。工程検査を目的にしない前提では、KGL003/005/006を実使用条件proxyとして残し、KGL004を通信異常・禁止主張の境界確認として残す。KGL001/002は製造・評価効率の別枝として保存。
1. [data/kaggle_problem_setting_id_deep_dive.tsv](../data/kaggle_problem_setting_id_deep_dive.tsv): KGL001〜KGL006のID別作業面。problem setting signal、hidden intent、buyer/user、evidence、decision、kill condition、source URLを整理。
1. [docs/86_kaggle_usage_proxy_refresh.md](86_kaggle_usage_proxy_refresh.md): 工程検査ではなく実使用条件proxyとしてKaggleを再調査し、KGL007〜KGL012を追加。KGL003/005/006/007/008を実使用条件family、KGL011/KGL004を通信異常と禁止主張の境界確認に置く。
1. [data/kaggle_usage_proxy_refresh.tsv](../data/kaggle_usage_proxy_refresh.tsv): KGL003/005/006/007/008/009/010/011/012のproxy type、EPSサプライヤ用途、優先度、limit、next action、kill condition、source URLを整理。
1. [docs/87_kaggle_each_id_deep_dive.md](87_kaggle_each_id_deep_dive.md): KGL001〜KGL012を同じ判定軸で深掘り。KGL003/005/006/007/008を使用条件familyの主材料、KGL004/011を通信異常境界、KGL001/002/009/010/012を別枝または補助に整理。
1. [data/kaggle_each_id_deep_dive.tsv](../data/kaggle_each_id_deep_dive.tsv): 各IDのdeep_dive_decision、何を示すか、EPSサプライヤでの読み替え、次artifact、禁止主張、次checkを整理。
1. [docs/88_kaggle_usage_condition_family_table.md](88_kaggle_usage_condition_family_table.md): KGL003/005/006/007/008を中心に、KGL004/011通信異常境界も含めた30件の使用条件familyを人間向けに説明。最新ルールでは主成果物ではなく、予測的な付加価値候補を検証するための中間成果物として扱う。
1. [data/kaggle_usage_condition_families.tsv](../data/kaggle_usage_condition_families.tsv): 30件のusage family作業表。source ID、proxy signal、EPS評価質問、診断質問、顧客説明質問、禁止主張、priority、next checkを整理。次に「何を先読みできる可能性があるか」へ変換する土台として使う。
1. [docs/89_kaggle_predictive_value_plan.md](89_kaggle_predictive_value_plan.md): Kaggle / 公開proxyを、予測的付加価値候補として順次検証する計画。PVC001〜PVC007の優先順位、実施順、Kill条件を整理。
1. [data/kaggle_predictive_value_candidates.tsv](../data/kaggle_predictive_value_candidates.tsv): KGL/UFをPVC001〜PVC007へ変換した候補表。何を先読みするか、買い手/利用者、EPSサプライヤが関与できる理由、禁止主張、Kill条件を整理。
1. [docs/90_pvc001_usage_load_class_deep_dive.md](90_pvc001_usage_load_class_deep_dive.md): 最有望候補PVC001「使用負荷classの先読み」の初回深掘り。外販商品ではなく、EPSサプライヤ内の製品企画、診断企画、品質改善、評価企画へ転記できるかを見る。
1. [data/pvc001_usage_load_class_sample.tsv](../data/pvc001_usage_load_class_sample.tsv): PVC001の9件の使用負荷class sample。ULC001〜ULC009ごとに公開proxy、先読み対象、部署、価値、禁止主張、Kill条件、次checkを整理。
1. [docs/91_pvc001_1h_goal_deep_dive.md](91_pvc001_1h_goal_deep_dive.md): PVC001を1時間Goalで深掘りした結果。ULC001/003/004/008のitem別結論、ULC008中心の1枚sample、部署別価値、弱点、Continue/Kill条件を整理。
1. [data/pvc001_four_class_deep_dive.tsv](../data/pvc001_four_class_deep_dive.tsv): ULC001/003/004/008の4件について、結論、confidence、部署適合、価値、弱点、Proceed/Kill impact、next actionを整理。
1. [data/pvc001_ulc008_one_page_sample.tsv](../data/pvc001_ulc008_one_page_sample.tsv): ULC008「駐車場走行で低速・大舵角・凹凸が重なる使われ方」の1枚sample。市場需要、未解決pain、仮説、部署別用途、禁止主張、Kill条件を整理。
1. [docs/92_pvc001_ulc008_department_review_deep_dive.md](92_pvc001_ulc008_department_review_deep_dive.md): ULC008を、製品企画・診断企画に見せるサプライヤ内レビューsampleとして深掘り。出力形式、evidence boundary、最小信号契約、部署別判断、Kill gateを整理。
1. [data/pvc001_ulc008_department_review_questions.tsv](../data/pvc001_ulc008_department_review_questions.tsv): ULC008の部署別レビュー質問。製品企画、診断企画、品質改善、評価企画、全体Kill gateごとに、Proceed signal、Kill signal、次アクションを整理。
1. [data/pvc001_ulc008_kill_gate.tsv](../data/pvc001_ulc008_kill_gate.tsv): ULC008の最小Kill gate。2部署以上に具体的な使い道があるか、原因断定に見えないか、既存評価・診断の言い換えで終わらないかを判定する表。
1. [docs/93_predictive_value_id_status_inventory.md](93_predictive_value_id_status_inventory.md): 手持ちのPVC/ULC/KGL IDを棚卸しした補正前レポート。EPS内部事実不足を主Kill理由にしすぎたため、最新判断はdocs/96を見る。
1. [data/predictive_value_id_status_inventory.tsv](../data/predictive_value_id_status_inventory.tsv): PVC001〜007、ULC001〜009、KGL001〜012の補正前ステータス表。最新ステータスはdata/predictive_value_corrected_status.tsvを見る。
1. [docs/94_predictive_value_next_items_deep_dive.md](94_predictive_value_next_items_deep_dive.md): 次アイテムとして挙げたULC008、ULC004、PVC004を深掘り。ULC008は製品企画向け/診断企画向けに分割し、ULC004は品質改善・顧客説明向け、PVC004は診断信頼性境界として整理。
1. [data/pvc001_ulc008_two_department_sheets.tsv](../data/pvc001_ulc008_two_department_sheets.tsv): ULC008を製品企画向けと診断企画向けに分けたサプライヤ内レビュー用作業表。各sheetの判断、需要、evidence boundary、初期artifact、禁止主張、Proceed/Kill signalを整理。
1. [data/ulc004_rough_road_steering_deep_dive.tsv](../data/ulc004_rough_road_steering_deep_dive.tsv): ULC004「荒れた路面 + 操舵」の深掘り表。品質改善、評価企画、顧客技術説明で使えるか、路面分類productや原因断定へ流れないかを整理。
1. [data/pvc004_communication_boundary_deep_dive.tsv](../data/pvc004_communication_boundary_deep_dive.tsv): PVC004「通信異常context」の境界表。診断企画、サイバー担当、顧客技術説明での使い道、汎用IDS/CSMS/TARAへの逸脱、禁止主張を整理。
1. [docs/95_predictive_value_continue_final_decision.md](95_predictive_value_continue_final_decision.md): 残っていたContinue項目の最終判断。公開情報とKaggle proxyだけで継続深掘りする項目は残さず、ULC008/ULC004/PVC004をサプライヤ内レビュー材料に限定。
1. [data/predictive_value_continue_final_decisions.tsv](../data/predictive_value_continue_final_decisions.tsv): PVC/ULC/KGL各IDのprevious status、final status、最終結論、停止理由、再開条件、次owner、禁止主張を整理。
1. [docs/96_predictive_value_internal_fact_correction.md](96_predictive_value_internal_fact_correction.md): 前回の全滅判断を補正した最新判断。EPS内部事実が見えないことを主Kill理由にせず、PVC001/ULC008/ULC004/PVC004を公開proxy価値の検証候補として戻す。
1. [data/predictive_value_corrected_status.tsv](../data/predictive_value_corrected_status.tsv): 補正後のID別ステータス。使用条件class、路面・操舵context、通信異常contextを、故障予測ではなくEPSサプライヤの業務価値候補として整理。
1. [docs/63_kaggle_supplier_owned_data_pdca.md](63_kaggle_supplier_owned_data_pdca.md): Kaggle方向を1時間Goalで深掘りし、データ収集、仮説、検証PDCAを回した結果。Bosch型の製造・EOL検査の早期不良候補抽出を最優先、Mercedes型の評価時間見積もりを2番手に置く。
1. [data/kaggle_supplier_owned_source_collection.tsv](../data/kaggle_supplier_owned_source_collection.tsv): Bosch、Mercedes-Benz、EPS/EPAS EOL、EOL品質データ、OBD/CAN、Car-Hackingのソース収集表。
1. [data/kaggle_supplier_owned_hypotheses.tsv](../data/kaggle_supplier_owned_hypotheses.tsv): 製造・EOL検査、bench/HILS評価時間、説明1枚、停止候補を、市場需要、未解決pain、解決策、買い手、Kill条件で整理。
1. [data/kaggle_supplier_owned_pdca.tsv](../data/kaggle_supplier_owned_pdca.tsv): 4周分のPlan / Do / Check / Actと判断。
1. [docs/64_kaggle_pre_shipment_predictive_quality_deep_dive.md](64_kaggle_pre_shipment_predictive_quality_deep_dive.md): Kaggleから「出荷前の予知保全」を掘り直した最新メモ。Bosch型を、出荷前品質スクリーニングとして読み替える。
1. [data/kaggle_pre_shipment_quality_findings.tsv](../data/kaggle_pre_shipment_quality_findings.tsv): Bosch/Mercedesから得られた具体情報、EPSサプライヤへの読み替え、使えること/使えないこと。
1. [data/pre_shipment_quality_offer_candidate.tsv](../data/pre_shipment_quality_offer_candidate.tsv): 出荷前品質スクリーニング候補を、市場需要、痛み、仮説、解決、買い手、初期artifact、検証、Kill条件で1行ずつ整理。
1. [docs/65_pre_shipment_quality_screening_proxy_demo.md](65_pre_shipment_quality_screening_proxy_demo.md): Bosch型の構造を再現した出荷前品質スクリーニングproxy demo。上位5%個体でfail/retest候補17.5%を捕捉し、再検査・保留・工程確認への転記可否を確認。
1. [generated/pre_shipment_quality_screening_proxy.html](../generated/pre_shipment_quality_screening_proxy.html): ブラウザで見られるproxy demo。Kaggle実データではなくsynthetic proxyであることを明記。
1. [docs/60_sbw_explanation_support_no_go_reasoning.md](60_sbw_explanation_support_no_go_reasoning.md): Steer-by-wire向けの説明資料整理支援が、なぜ有償サービスとしてNo-Goなのかを、市場需要からKill条件まで一本の論理で整理した最新判断。
1. [data/sbw_explanation_support_no_go_reasoning.tsv](../data/sbw_explanation_support_no_go_reasoning.tsv): 市場需要、未解決pain、仮説縮小、既存業務重複、EPSサプライヤ境界、Kill条件を対応づけたTSV。
1. [docs/59_wheel_side_steering_unit_plain_deep_dive.md](59_wheel_side_steering_unit_plain_deep_dive.md): `road wheel actuator` を「車輪側操舵ユニット」と言い直し、何が市場変化で、何が既存安全・認証・診断業務の範囲かを平易に整理した判断。
1. [data/wheel_side_steering_unit_plain_deep_dive.tsv](../data/wheel_side_steering_unit_plain_deep_dive.tsv): 車輪側操舵ユニットについて、市場需要、未解決の痛み、仮説、解決策、利用者、初期提供物、検証方法、Kill条件を平易な言葉で整理したTSV。
1. [docs/58_sbw_public_only_info_collection.md](58_sbw_public_only_info_collection.md): 内部資料を使わず、公開情報だけでSbW方向を追加収集した判断。市場変化はあるが、汎用安全・認証・診断支援は既存論点と重なり、外販Proceedには進めない。
1. [data/sbw_public_only_source_inventory.tsv](../data/sbw_public_only_source_inventory.tsv): Bosch、ZF、Nexteer、Schaeffler、HELLA、JTEKT、Tesla、NHTSA、VCA、R79、ASAM SOVDの公開情報を、何を支持し、何を支持しないかで整理したTSV。
1. [data/sbw_public_only_value_check.tsv](../data/sbw_public_only_value_check.tsv): 公開情報だけで市場変化、未解決pain、既存業務との差分、診断コンテンツ余地、初期提供物をどこまで言えるかの判定表。
1. [docs/54_steer_by_wire_business_deep_dive.md](54_steer_by_wire_business_deep_dive.md): Steer-by-wire方向を事業成立性まで深掘りした判断。汎用安全支援ではなく、OEM説明・診断設計へ転記するcomponent-boundary整理だけを狭く残す。
1. [data/steer_by_wire_business_deep_dive.tsv](../data/steer_by_wire_business_deep_dive.tsv): SbW方向の市場需要、未解決の痛み、仮説、初期提供物、Kill条件を整理したTSV。
1. [docs/57_sbw_8_material_verification.md](57_sbw_8_material_verification.md): SbW 8項目を公開情報で検証した結果。1-4はPartial、5-8はUnknown。現行方針では内部資料を要求しないため、外販Proceedには進めない。
1. [data/sbw_8_material_verification.tsv](../data/sbw_8_material_verification.tsv): 8項目ごとのpublic verification result、公開情報で分からないこと、decision impact、公開情報だけでの限界。
1. [docs/56_sbw_decision_materials.md](56_sbw_decision_materials.md): SbW方向をProceed / Killするために集めた判断材料。公開ソースから見えることと、公開情報だけでは埋まらない8項目を分ける。
1. [data/sbw_decision_materials.tsv](../data/sbw_decision_materials.tsv): ZF、Mercedes-Benz、Tesla、Lexus、HELLA、NHTSA、VCAの公開情報を、判断への使い方、強める点、弱める点へ対応づけたTSV。
1. [docs/55_sbw_redundancy_degraded_one_page_sample.md](55_sbw_redundancy_degraded_one_page_sample.md): 車輪を動かす側の冗長系が一部落ちた場合を題材にした公開情報ベースの1ケースsample。これ単体で独自価値が出るかを見る。
1. [data/steer_by_wire_redundancy_degraded_sample.tsv](../data/steer_by_wire_redundancy_degraded_sample.tsv): 1ケースsampleのfield、supplier-owned source、OEM回答価値、Kill条件。
1. [docs/51_steer_by_wire_kill_first_review.md](51_steer_by_wire_kill_first_review.md): Steer-by-wire安全・冗長・cyber方向の一次レビュー。市場変化はあるが、既存安全業務と被るためHold / explore next。
1. [data/steer_by_wire_kill_first_review.tsv](../data/steer_by_wire_kill_first_review.tsv): Steer-by-wireの市場シグナル、EPSサプライヤが持てる手札、Kill条件を整理したTSV。
1. [docs/52_sovd_kill_first_review.md](52_sovd_kill_first_review.md): SOVD / next-generation diagnostics方向の一次レビュー。主商品ではなく、EPS診断コンテンツ設計のextensionとしてのみ残す。
1. [data/sovd_kill_first_review.tsv](../data/sovd_kill_first_review.tsv): SOVD標準・既存ツール・EPSサプライヤ残余価値・Kill条件を整理したTSV。
1. [docs/42_coverage_benchmark_artifact_intake_result.md](42_coverage_benchmark_artifact_intake_result.md): Coverage BenchmarkのArtifact Intake実行結果。
1. [data/coverage_benchmark_artifact_intake_result.tsv](../data/coverage_benchmark_artifact_intake_result.tsv): 10 artifactごとのplaceholder、実資料有無、今判定できること、できないこと、status。
1. [data/coverage_benchmark_artifact_intake_decision.tsv](../data/coverage_benchmark_artifact_intake_decision.tsv): Artifact intake後のProceed/Hold/Kill判断表。
1. [data/coverage_benchmark_internal_placeholder_screening_sheet.tsv](../data/coverage_benchmark_internal_placeholder_screening_sheet.tsv): 内部資料を使える場合だけ参照する4項目screening sheet。
1. [generated/coverage_benchmark_p1_assessment.html](../generated/coverage_benchmark_p1_assessment.html): FAM08/FAM02/FAM11を使ったP1 assessment packageのクイックHTML。
1. [docs/40_coverage_benchmark_p1_assessment_package.md](40_coverage_benchmark_p1_assessment_package.md): Coverage BenchmarkのP1 assessment最小構成。
1. [data/coverage_benchmark_p1_assessment_plan.tsv](../data/coverage_benchmark_p1_assessment_plan.tsv): P1 workstream、入力、出力、owner、timebox、Proceed/Kill条件。
1. [data/coverage_benchmark_family_reuse_matrix.tsv](../data/coverage_benchmark_family_reuse_matrix.tsv): FAM08/FAM02/FAM11で同じrow構造を再利用できるかのmatrix。
1. [data/coverage_benchmark_p1_decision_rubric.tsv](../data/coverage_benchmark_p1_decision_rubric.tsv): P1のProceed / Hold / Kill判定ルーブリック。
1. [generated/fam08_immediate_visibility_review.html](../generated/fam08_immediate_visibility_review.html): FAM08が今日すぐProceed / Hold / Kill判定できるかを見るクイックHTML。
1. [docs/39_fam08_immediate_visibility_review.md](39_fam08_immediate_visibility_review.md): `FAM08 stop-start low-speed` の即時可視性レビュー。
1. [data/fam08_immediate_visibility_triage.tsv](../data/fam08_immediate_visibility_triage.tsv): FAM08のmarket fit、HILS重複、DTC snapshot、workflow fitを即時triageするTSV。
1. [docs/38_fam08_stop_start_low_speed_coverage_benchmark_sample.md](38_fam08_stop_start_low_speed_coverage_benchmark_sample.md): `FAM08 stop-start low-speed` の1ページcoverage benchmark sample。
1. [data/fam08_stop_start_low_speed_coverage_benchmark_sample.tsv](../data/fam08_stop_start_low_speed_coverage_benchmark_sample.tsv): FAM08 sampleのreview item、expected EPS facts、coverage question、HILS/bench scenario、Kill条件。
1. [docs/37_eps_coverage_benchmark_business_value.md](37_eps_coverage_benchmark_business_value.md): Coverage Benchmark線でビジネス価値が出るかを、買い手・予算・代替・Kill条件まで深掘りしたレポート。
1. [data/eps_coverage_benchmark_business_value.tsv](../data/eps_coverage_benchmark_business_value.tsv): business model別に市場需要、未解決痛み、買い手、予算経路、proof demo、Kill条件を整理したTSV。
1. [docs/36_eps_common_pain_productization_scan.md](36_eps_common_pain_productization_scan.md): EPS共通pain familyから、スケール可能な事業候補を再抽出したレポート。
1. [data/eps_common_pain_business_scores.tsv](../data/eps_common_pain_business_scores.tsv): 13 familyの共通性、サプライヤ制御性、差別化、スケール性のスコア表。
1. [data/eps_common_market_pain_reclassification.tsv](../data/eps_common_market_pain_reclassification.tsv): 公開EPS case 30件の共通pain family再分類。
1. [docs/35_rca_8d_case_pack_viability_report.md](35_rca_8d_case_pack_viability_report.md): `RCA / 8D Evidence Case Pack` が単独主商品として弱いことを検証したレポート。
1. [data/rca_8d_case_pack_viability_assessment.tsv](../data/rca_8d_case_pack_viability_assessment.tsv): 成立条件、代替品、EPSサプライヤ適合、収益モデル、Kill条件の評価表。
1. [docs/34_eps_supplier_business_model_reassessment.md](34_eps_supplier_business_model_reassessment.md): 上位ルール後に既存データを再評価し、主商品をcase packへ寄せた判断。現在はhistorical寄り。
1. [data/eps_supplier_business_model_reassessment.tsv](../data/eps_supplier_business_model_reassessment.tsv): EPSサプライヤ視点の再評価表。現在はhistorical寄り。
1. [docs/20_existing_diagnostics_oem_boundary.md](20_existing_diagnostics_oem_boundary.md): 既存DEM/UDS診断との差分、OEM領分、サプライヤ側の現実的な手札。
1. [docs/22_public_proxy_data_reset.md](22_public_proxy_data_reset.md): 内部ケースにアクセスできない前提で、公開市場情報/Kaggle/公開CANデータで補える範囲を再定義。
1. [docs/27_s2e001_diagnostic_evidence_gap_check.md](27_s2e001_diagnostic_evidence_gap_check.md): S2E001を既存DTC/freeze frameで説明できるか見るgap check。
1. [docs/28_s2e001_diagnostic_evidence_review_template.md](28_s2e001_diagnostic_evidence_review_template.md): 内部DTC仕様を入れてProceed/Kill/Holdを判定するレビュー手順。
1. [docs/29_business_model_rebranch_after_s2e001_hold.md](29_business_model_rebranch_after_s2e001_hold.md): S2E001 Hold後のビジネスモデル再分岐。
1. [docs/30_bmr001_market_pain_scenario_cards.md](30_bmr001_market_pain_scenario_cards.md): BMR001の初期3枚scenario cardと商品化境界。最新では主商品ではなく前段材料。
1. [docs/31_bmr002_rfq_design_review_pack.md](31_bmr002_rfq_design_review_pack.md): BMR001をRFQ/設計レビュー1ページへ変換したBMR002 sample。最新では主商品ではなく副産物。
1. [docs/23_public_proxy_demo_plan.md](23_public_proxy_demo_plan.md): `Steering Context Risk Explorer` の代理デモ計画。
1. `generated/bmr002_rfq_design_review_pack.html`(削除済み): BMR002 Scenario Readiness Pageのブラウザ表示。
1. `generated/bmr001_market_pain_scenario_cards.html`(削除済み): BMR001 scenario cardのブラウザ表示。
1. [generated/business_model_rebranch_after_s2e001_hold.html](../generated/business_model_rebranch_after_s2e001_hold.html): 再分岐の意思決定ビュー。
1. `generated/s2e001_diagnostic_evidence_review_template.html`(削除済み): S2E001 review templateの意思決定ビュー。
1. [generated/s2e001_diagnostic_evidence_gap_check.html](../generated/s2e001_diagnostic_evidence_gap_check.html): S2E001 gap checkの意思決定ビュー。
1. `generated/eps_scenario_to_evidence_pack.html`(削除済み): Scenario-to-Evidence Packの意思決定ビュー。
1. `generated/low_speed_high_steering_proxy.html`(削除済み): Phase 2の代表window可視化。
1. `generated/steering_context_risk_explorer_phase1_ja.html`(削除済み): ブラウザで見られるPhase 1静的デモ日本語版。
1. `generated/steering_context_risk_explorer_phase1.html`(削除済み): Phase 1静的デモ英語版。
1. [data/eps_public_market_pain_cases.tsv](../data/eps_public_market_pain_cases.tsv): NHTSA/recall/investigationから抽出したdriver-visible EPS painケース。
1. [data/public_steering_dataset_inventory.tsv](../data/public_steering_dataset_inventory.tsv): 公開steering / CAN / Kaggle dataset棚卸し。

## SOTIF / 棚卸し(docs/153〜154)

- [153 SOTIF-EooC 仮定シート](153_sotif_eooc_assumption_sheet.md): 部品側が差し出す仮定を本研究の実データで埋めた。埋まる欄・埋まらない欄・OEMが埋める欄の区別
- [154 「すべて消化した」の棚卸し](154_open_items_after_exhaustion_claim.md): docs/151の完了宣言は誤り。未消化3件を確定し、全て消化
- [155 窓長と再発判定の検証](155_window_recurrence_verification.md): 「再発を数えれば感度が上がる」は一律には成立しない。特徴量ごとに最適設計が逆を向き、その順序は4車種で一致
- [156 学習era内の見逃し構造分析](156_train_era_miss_structure.md): 見逃しは調整不足ではなく情報の不在。見逃しcohortの操舵系苦情は中央値1件
- [192 STR capability 決定則 — 事前登録](192_str_capability_rule_protocol.md): 結果を見る前に固定。`C = sqrt(R_on_base/R_on(t))`。**比を取るとRthが消える**ので docs/189② の測定失敗を迂回できる
- [193 STR capability 決定則 — 実行結果](193_str_capability_rule_results.md): **P1(早く鳴る)は3/6で不成立。**P2は6/6成立、**宣言粒度 0.081〜0.641%**。個体基準が買うのは警報の早さではなく**値の解像度**。終端で能力7〜17%喪失
- [194 capability決定則 — 第2機構の事前登録](194_capability_rule_second_mechanism_protocol.md): 1機構では規則ではなく計器。層間短絡へ同じ形を当てる
- [195 capability決定則 — 第2機構で転移](195_capability_rule_second_mechanism_results.md): **R1/R2成立(ρ=−1.000)。**2機構をまたいだ**宣言粒度 0.08〜1.0%**。副産物: 個体基準が docs/162 の不成立(ρ=0.381)を ρ=−1.000 に解消。**発症は容易、進行は難しい**
- [196 SOTIFに部品側として参加する要素](196_eps_health_element.md): **決定則を要素として組んで動かした。**組んで初めて出た要求——**出荷時指紋は運用動作点範囲を掃引して採ること**(スパン10°Cに対し運用は20〜31°C動き、6個体中1個体が終端で宣言を失った)。個体基準のコストは**36バイト**
- [197 宣言を縛るのは測定ではなく仮定だった](197_what_limits_the_declaration.md): **自己訂正——0.08〜1.0%は分解能であって確度ではない。**Rthが0.16〜2.0%増えるだけで誤差が並ぶ。指紋の要求を数値化(動作点は指紋幅の1.7〜3.0倍を動く)
- [198 パルス自己発熱で熱経路を測る 事前登録](198_pulse_thermal_protocol.md): docs/189②は`steadyState`しか見ていなかった。`transient`にパルス発熱の曲線がある
- [199 熱経路は劣化していなかった／観測量の取り違え](199_pulse_thermal_results.md): **T1/T2とも0/6で不成立=熱経路は平坦。**そして探索で判明——**`Vds/Id`はオン抵抗ではなく能動領域の動作点抵抗。試験機の温度低下は実験計画。**パワー段側のCは指標であって能力比ではない
- [200 モータ側 第2の故障種と振動 事前登録](200_motor_second_fault_and_vibration_protocol.md): KAIST 32ファイル中24が未使用。振動が要るかはセンサ追加の要否を決める
- [201 巻線の故障は2種類あり電流は片方しか見ない](201_motor_second_fault_and_vibration_results.md): **W1不成立。**層間短絡は電流(ρ=−1.000)、**コイル間短絡は電流が効かず振動(ρ=+1.000)**。**ECUの既存センサは巻線故障の片方しか覆わない**
- [202 別機体2台での再現 事前登録](202_cross_machine_replication_protocol.md): 同一データセットに3機体あった。**ダウンロード前に事前登録をコミット**。探索(1.0 kW)と確認(1.5/3.0 kW)が別データに分かれた初めての例
- [203 別機体では再現しなかった](203_cross_machine_replication_results.md): **1.0 kWの巻線側の結論はほぼ全部非再現。**層間短絡の電流指標は ρ = −1.000 / **+1.000** / +0.400 と機体で向きが逆。docs/201は取り下げ。**測定キャンペーンの段差だけが3機体6セル全部で再現し、日付メタデータから復元できる**
- [204 符号を捨てた逸脱指標 事前登録](204_sign_free_deviation_protocol.md): capability値を降ろし、逸脱検知が機体をまたぐかを問う。既に見た特徴量と盲検の特徴量を先に区別
- [205 機体をまたぐ逸脱指標は1つだけあった](205_sign_free_deviation_results.md): **振動2f0が3機体5セルで成立(5/5)。相電流ベースは2つとも不成立。**→ **センサ追加ゼロでは成立しない。**「検出できる」はまたぐが「どこから」はまたがない(3.35〜17.86%)
- [206 車検データの原因別分解 事前登録](206_mot_cause_breakdown_protocol.md): docs/150は操舵系を一括、docs/189①はEPS固有9項目。**その中間の一般PS 59項目が未使用**
- [207 PS兆候は33.9倍／機能不全には兆候の階層が無い](207_mot_cause_breakdown_results.md): 兆候のみ54,431台で**33.9倍**(docs/189①の範囲を訂正)。**ただし74.2%は油圧の漏れ。**そして**機能系項目にadvisoryの区分が制度上存在しない**——少ないのではなく無い
- [208 油圧を除いた先行性 事前登録](208_mot_nonhydraulic_protocol.md): 33.9倍の74.2%が油圧の漏れだった。作動油系を兆候からも不合格からも外す
- [209 油圧を除いても22.0倍が残る](209_mot_nonhydraulic_results.md): **N1成立(22.0倍、n=14,029)。33.9倍は油圧の性質ではなかった。**ただし残った中身は実質的に**腐食1族**。腐食→機能不全の6.9倍は観察として記録し検定せず
- [210 不安定さは水準に先行するか 事前登録](210_instability_precursor_protocol.md): docs/165以降ずっと中央値しか見ていなかった。**断続＝不安定**なので記録ごとのばらつきを見る
- [211 不安定さは先行しなかった](211_instability_precursor_results.md): **3基準とも不成立(先行0/6)。**水準は基準の35倍まで離れるのにばらつきは1.0〜2.0倍。**この試験の劣化は乱れずにずれる**——断続機構がデータに入っていない。主張から「不安定さを見る」を外した
- [212 断続故障の発生条件 事前登録](212_trigger_conditions_protocol.md): 売り物は「その瞬間を捕まえる」なのに、**いつ記録を始めるかの答えが無い**。苦情本文の発生条件を読む
- [213 トリガ条件 — 登録は満たしたが分母が不適切だった](213_trigger_conditions_results.md): **`while_turning` 5.61倍を自分で取り下げ**(操舵系分母では1.59倍)。公正な分母では2.0倍超が1件も無い。**言えるのは「キーサイクルまで保持される形が瞬間的な形より4倍以上多く書かれる」——記録の窓は広く取れる**
- [214 公開データ棚卸し 2026-08-30](214_dataset_reinventory_2026_08.md): 軸を断続故障に変えて再探索。**接点系は依然として無い**が、**インバータ駆動PMSMの故障データ(実機・CC BY 4.0・開放/短絡/過熱)**と**OpenLKA(実車62車種・操舵トルク100Hz・事象ラベル付き)**を新規発見。docs/211の「使い切った」を取り下げ
- [215 インバータ故障データを取得](215_inverter_dataset_acquisition.md): **故障は恒久で断続は入っていない。**ただし**正常クラスだけが非定常**(Ib が118カウント漂動)で、故障クラスは定常——**分類器が「漂動しているか」を分けている危険**。本Repo初のインバータ側データ
- [216 開放故障は相電流だけで切り分けられるか 事前登録](216_inverter_signal_requirement_protocol.md): 分類器を使わず**物理から向きを予測**。1条件1記録・正常だけ非定常なので分類器は記録を当ててしまう
- [217 向きは出たが場所は特定できなかった](217_inverter_signal_requirement_results.md): **P1成立(2/2)・P2不成立(1/2)。**HB2上側開放は明瞭(R_B 3.017→0.205)だがHB3下側は特定を外す。**温度を足しても救われない**(開放2件ともT1が最大)。原因は**基準にした正常データが不平衡**(R_B=3.017) — 基準は取り替えず別登録へ
- [218 整定後を基準に取り直す 事前登録](218_inverter_settled_baseline_protocol.md): 落ちた後の基準選び直しなので、区間規則を結果と無関係に固定(全ファイル末尾60%、他の割合は試さない)
- [219 基準は直った。判定は落ちた](219_inverter_settled_baseline_results.md): 基準は平衡化(R_B 3.017→0.975)したが**Q1/Q2とも1/2で不成立。**そして**故障がどこにあってもB相が最大(5/8)**——**この指標は場所ではなく最も動くチャネルを選んでいる。**成功に見えた1件も証拠にならない。**この線を閉じる**
- [220 実車ログで個体基準法の粒度を測る 事前登録](220_real_vehicle_granularity_protocol.md): 中心的な方法を**実車で試したことが一度も無かった**。残差がEPSの測定量でないことを先に宣言
- [221 動作点正規化は実車では効かなかった](221_real_vehicle_granularity_results.md): **R2は0/4で不成立**(2車種は悪化)。試験装置では6.8〜14.3%→0.09〜0.75%だったものが実車では効かない。**ただし実車の宣言粒度が初めて出た: 0.19〜0.24 m/s²。**逸脱の裾は最大1.2〜2.3倍で重い裾は無い
- [222 窓平均とfirmware 事前登録](222_window_and_firmware_protocol.md): 実車の床は測ったが**窓でどれだけ下がるかを測っていなかった**。docs/144の粒度主張に直結する
- [223 平均は予想の半分しか効かないが2〜5秒で届く](223_window_and_firmware_results.md): **W1成立(r=1.63〜2.31、1/√Nは実車に当てはまらない)。**しかし**0.10 m/s²には2.0〜5.0秒で到達**——**docs/144の主張が実車の雑音構造でも支持された。**W3: 同一車種内でも群により床が1.2倍違う(交絡あり)
- [228 仕様を実車ログの上で動かす 事前登録](228_recorder_simulation_protocol.md): 「記録器がどれだけ黙るか」を測る。指紋の代用が既知の欠陥を持つことを手順に明記
- [229 1回の走行で採った指紋では3〜4分の時間を黙る](229_recorder_simulation_results.md): **沈黙 65.6〜80.7%。配備できない。**×5で1%未満に落ちる崖(×2では24〜42%残る)。**ただし×5は同一走行内の話で、走行をまたぐ要求はdocs/227の7〜35倍。**出力は1件24バイトで容量は問題にならない
- [226 仕様の空欄を2つ埋める 事前登録](226_filling_spec_blanks_protocol.md): 6欄中2欄は手元のデータで埋まる。分位点を結果を見る前に固定
- [227 空欄2つが埋まった](227_filling_spec_blanks_results.md): **指紋は1走行では速度軸で7〜35倍足りない**(実車2,495ログ)。**記録は397日(13か月)生きる必要がある**(車検2,234万台のp90)。事前バッファは設計で消えた。**残る空欄は4件**
- [225 記録器の仕様](225_recorder_specification.md): **docs/188の一文を実装可能な仕様にした。**新データ無し、全項目に根拠付き。**トリガは条件で絞らない**(公正な分母では2.0倍超が1件も無い)、窓5秒以上、不揮発必須、指紋36バイト。**主張してはならない7件**と**空欄6件**を仕様の一部として明記
- [230 棚卸しの失敗とIGBTデータ](230_inventory_failure_and_igbt.md): **総覧を起点にしていなかった。**既に使っていたNASAリポジトリに未取得の電子部品run-to-failureが**3件**。**IGBTは矩形波ゲート＝スイッチ動作**で、docs/199の欠陥が当てはまらない。docs/192〜199をやり直せる
- [231 配布論文とReadmeを読んで設計を変えた 事前登録](231_igbt_reading_and_protocol.md): 論文が前駆をV_gthと名指し。**良質なスイッチ動作データは1個体だけ**と判明し、docs/192〜199のやり直しは不成立と判断。代わりに**新品40個体**でCapacitorは取得せず
- [232 新品40個体で測った](232_pristine_unit_spread_results.md): **しきい値電圧の個体差が測定ノイズの159〜530倍**(IGBT漏れ電流は727倍)。**「個体基準は必須」を実部品で直接測れた初めての結果。**ただし6つ中3つは測定が荒く個体を区別できない
- [233 除外の判断を取り下げる 事前登録](233_igbt_exclusion_retracted_protocol.md): **docs/231の除外は誤り。**Readmeの警告は過渡波形に向いていなかった。**約690回の波形が全部埋まっていた**
- [234 スイッチ動作でも動かなかった／三度目の「試験機が動作点を変えていた」](234_igbt_switching_results.md): **H1不成立(最大2/4)。**そして**供給2.5→6.0V・温度設定100→280°Cのストレスランプ**が観測量の変動を説明する。**3件連続で同じ失敗。**AGENTS.mdに作法を追加
- [235 取得せずに候補を評価した](235_pre_acquisition_survey.md): **8件を配布ページだけで判定、取得ゼロ。合計526 GB超を落とした。**最有望だったボールねじは**Simulinkのシミュレーション**、NASA Capacitorは**動作点は良質だが問いに答えない**。断続故障は三度目の探索でも無し。**総覧論文の付録表は3通り試して読めず**
- [236 ストレスランプを除いて測る 事前登録](236_within_condition_protocol.md): 落ちた後の切り直しなので、条件群の選び方を最多件数で固定。落ちた場合の結論も先に決めた
- [237 ランプを除いても動かない](237_within_condition_results.md): **J1は1/4で不成立。理由は条件の保持時間が9〜44分しかないこと。**加速試験は**「保持」と「劣化する」が両立しない。**測定は量子化限界(基準の散らばりが厳密に0)。**S11の線を閉じる。**取得前評価に項目を1つ追加
- [238 何のデータが要るのか](238_data_requirement.md): **落ちた検証から逆算したデータの仕様。**13要件、各行にそれを決めた失敗を付す。**効くのは2件だけ——断続故障そのものと、事象時刻の正解。**他11件は既存データで近似できている。最小構成はEPSでなくてよい
- [239 断続故障を正面から探した](239_arc_fault_search.md): **アーク故障データ4件を評価、取得ゼロ。**接点開放方式でR12には合致するが、**全部がアーク開始でトリガされ事象前のデータが無い。**→ **「断続のデータが無い」は訂正。無いのは「断続が起きる前」である**
- [224 現在の結論(2026-08-30)](224_current_conclusion.md): **この2週間の12件を1本に集約。**外部観測は6系統盲目/個体基準は必須/実車の観測床0.19〜0.25 m/s²・必要窓2〜5秒/落ちた7件の一覧/**断続故障の公開データは存在しない**
- [191 劣化を知る需要とSOTIFの境界](191_degradation_demand_and_sotif.md): 需要は実在し既に134万台で稼働中。**DTC未到達は2つに割れ、「故障が無いまま性能包絡が縮んだ」側はSOTIFである**(初版の否定を訂正)。宛先は `STR capability`、空欄はその値の決め方。操舵系715件中EPS×運転支援依存は0件
- [190 「Assyごと交換」は何を意味するか](190_assembly_replacement_meaning.md): docs/189の140万台を223,159台に訂正。**EPS交換の選別根拠は「動作履歴」か「製造ロット」の2種類しかなく、ECU内部の記録で134万台の交換可否が決まっていた**
- [189 「まだ言えないこと」5件をデータ検証](189_five_limits_tested.md): ①は**検証不能を確定**(EPS兆候が2,177万台中64台)。②は直接測定を**試みて失敗**。⑤の台数は[190](190_assembly_replacement_meaning.md)で訂正。副産物: EPS不合格の再発が**121〜417倍**
- [188 筋道 — 何が言えて何を売るのか](188_the_line.md): **7段すべてに検証参照を付けた本線**。売るものを1文に、言えないことを5件に確定
- [187 交換しても直らないはEPS固有でない](187_replacement_no_fix_result.md): EPS 0.92倍で**基準以下**。**EPS固有の痛みは「再現しないこと」1つだけ**と確定
- [186 どう金になり、SOTIFとどう繋がるか](186_how_it_becomes_money.md): **金の筋とSOTIFの筋は別**。金は保証の空振り修理とNTF返却(全車両・今日)。SOTIFは同じ記録の第2用途(ADS車のみ)。**SOTIFは需要の柱にしない**
- [185 誤診の痛みを定量](185_misdiagnosis_quantified.md): 苦情160万件。**EPS全体では差なし(1.01倍)**だが、**断続的な故障に絞ると原因不明率が5.0倍**。標的の族が痛みの族だった
- [184 誤り条件4の点検](184_ads_deployment_reality.md): **ADSは西側で後退**。Mercedes/BMW/HondaがL3を停止・終了。中国のみ指定区間・低速で商用展開。**規制の存在と需要の量は別**——需要の根拠をSOTIFから品質・保証の経済性へ戻す
- [183 誤り条件1の点検](183_autosar_capability_channel.md): AUTOSAR VMCは**宛先(STR capability報告)を標準化済み、中身(劣化からの導出)は未規定**(degradation/wear/thermalの語が0件)。副産物として**出力の宛先が標準に既にあった**
- [182 事業判断の更新](182_business_judgment_update.md): 「タダ化するか」に公開証拠で答えた。**規制が結果だけを義務化し方法を開けている**ため有償側の類型。誤り条件4つを明示
- [181 監視義務の範囲を精密化](181_monitoring_scope_refinement.md): SOTIF内容はADS限定だが、**フィールド監視の組織的義務は R155/R156 で2024-07から全車両**。導入障壁は「組織の新設」でなく「内容の追加」
- [180 EooCシート 26/26 充填](180_eooc_sheet_all_filled.md): **空欄ゼロ**。許容発生率はGAMAB+人間ドライバー基準(10⁻⁸オーダー)で導出方法まで公開情報で埋まった。**3つは調査不足の言い換えだった**
- [179 EooCシートの欠落](179_eooc_sheet_completion.md): **SOTIFの中核 triggering conditions が丸ごと無かった**。規格Clause 4.4.3と照合してE節(発現条件5)・F節(統合要求2)を追加、26項目に
- [178 SOTIFへの直答](178_sotif_straight_answer.md): **乗る。出せるのはEooC仮定シート1つだけ**。シートの埋まり具合を全欄提示。**Nexteerが取ったのは予知保全の席でSOTIFではない**(公式仕様に21448の言及なし)
- [177 SOTIF方向の判定更新](177_sotif_direction_update.md): **需要は規制の義務へ格上げ**(UN ADS GTR 2026-06採択)。**同時に競合Nexteerが量産投入**。観測台帳の2項目が両方発火。窓は開いたと同時に最初の席が埋まった
- [176 訂正: 接点系にも劣化の窓は存在する](176_correction_degradation_window.md): 「測れない」を「無い」と書いた飛躍を、公開リコール文書(断続・回復・再発)で訂正。**SOTIF方向は弱まっていない**
- [175 A''を閉じる](175_close_contact_question.md): 公開劣化データ**110件の総覧に接点は0件**。問いを閉じたうえで、文献の3段階カーブから「**fretting系に先行時間はない**」を構成。故障族ごとに主張を分ける
- [174 変動は水準に先行するか(結果)](174_contact_variance_results.md): **実質不成立**。SOReDDは固着故障が支配的で、狙う機構(漸進的な抵抗劣化)を動かしていなかった。**A''は未解決のまま**
- [173 変動先行の検証プロトコル](173_contact_variance_protocol.md): 値を見る前に固定した基準
- [172 接点劣化(A'')の検証経路](172_contact_degradation_route.md): リコールの進行性語は**定型句**だった。文献は膝型軌跡を示唆。**SOReDDで検証可能**。棚卸しに第3軸「接点」を追加
- [171 EPSに接合部の摩耗故障は現れるか](171_eps_wearout_mechanism_scan.md): **熱経路は公開記録に支持されない**(熱語は平均の0.54倍)。一方**断続的電気症状は2.81倍**。リコールは摩耗故障を見られない=**4つ目の構造的盲点**
- [170 パラメータのずれを機能不足へ翻訳](170_thermal_headroom_translation.md): **ギャップSを熱経路で埋めた**。最初の兆候時点で持続アシスト熱余裕を13〜50%喪失。faultは立たない=SOTIF。顕在化条件は低速大舵角で、公開市場ペインと一致
- [169 SOTIFとの絡みの再点検](169_sotif_link_check.md): **docs/167が実証したのは26262側のfault前駆であってSOTIFではない**。接点は「兆候〜故障確定の窓」。用語を3層に分離
- [168 転移はほぼ製品規格に還元される](168_transfer_reduces_to_spec.md): gain/offsetは手法が個体ごとに同定するので新しい問題ではない。**残るのは「frettingが単調な発生率を生むか」1点**
- [167 前駆指標の検証結果v2](167_precursor_results_v2.md): **成立(6/6)**。故障の1〜2段階前に兆候。温度を個体ごとに除けば個体基準は**0.09〜0.75%**で安定し、兆候はその**20〜300倍**
- [166 前駆指標の検証結果v1と v2の事前登録](166_precursor_results_v1.md): v1は不成立。プロトコル欠陥2件を記録
- [165 前駆指標の検証プロトコル](165_precursor_protocol.md): 値を見る前に固定した基準
- [164 現在地の1枚まとめ](164_position_summary.md): 証明できたこと6件・できていないこと2件・Kill済み・訂正5件を1枚に。**この研究が嘘をつけない構造**も明記
- [163 個体ばらつきへの標準対策と供給境界](163_per_unit_baselining.md): 基準は母集団ではなく**個体ごと**。docs/155/158の較正設計を訂正。**個体基準を書けるのはEOL検査を持つ者だけ**
- [162 PMSMモデル検証の結果](162_pmsm_model_validation_results.md): **不成立**。事前登録基準に対しモデルは整合せず、モデルは調整しなかった。ただし実測から EooC シート初の実測ベース行が1つ得られた
- [161 PMSMモデル検証プロトコル](161_pmsm_model_validation_protocol.md): 実測を見る前に固定した基準
- [160 資産範囲の拡張判定](160_asset_scope_expansion.md): SbW/ギアAssyへの拡張はKill再提案に当たらない。ただし車検データは資産を広げても本命にならない
- [159 公開データセット棚卸しの更新](159_public_dataset_reinventory.md): **前回は部品レベルを見ていなかった**。実故障ラベル付きPMSMデータを2件発見(DS011はCC BY 4.0・severity 8段階・EPS同出力帯)
- [158 SOTIF-EooC 運用フェーズ監視デモ](158_sotif_eooc_monitor_demo.md): 宣言→較正→観測→報告を1本で動かす。**核心は「OEMが埋める空欄」を同じ画面に並べたこと**
- [157 モードによる照合とCorsa訂正](157_mode_split_and_corsa_correction.md): 500X/Renegadeはカバー型。**Corsaの答え合わせはモード水準で誤帰属**——車検の群シグナルはEPSの代理指標ではない

## 公開準備

- [152 公開準備 再監査](152_publication_readiness_reaudit.md): 2026-08-21実施。他者データ非再配布の確認、Git履歴の個人メール除去、一人称wordingの是正。前回監査は [99](99_publication_readiness_audit.md)
- [SOURCES.md](../SOURCES.md): 出典・ライセンス・出典表示・取得日・派生ファイルの対応表
