# 旧READMEの記述(そのまま保存)

README.md を「結論とその根拠を読むための入口」に整理し直した際に、README から外した記述をそのまま保存したもの。
**内容は当時のままで、最新判断ではない。** 最新は [README.md](../../README.md)、[Memory.md](../../Memory.md)、docs/145・146・150・151 が正。

保存した理由は、判断の履歴(何をどの順で捨てたか)自体がこのRepoの資産だからである。
Kill済み仮説の一覧としては [docs/61_llm_kill_knowledge_base.md](../61_llm_kill_knowledge_base.md) の方が整理されている。

---

## 現在の状態

旧テーマはArchive扱いにする。

ここでいう旧テーマは、乗用車向けEPS単体について、公開情報だけを使い、故障予測、劣化兆候通知、追加ログ、公開市場pain分類、Coverage Benchmark、汎用SbW説明支援、SOVD基盤支援を外販商材にできるかを探した一連の探索である。
現行条件では、この方向は閉じる。

追加で見た自動運転・商用車両群向けの操舵系運行可否 / 点検優先度判断も、EPS/SbWサプライヤ単独の外販テーマとしてはArchiveする。
最終判断は [docs/archive/motion_health/75_motion_health_mhq001_final_decision.md](motion_health/75_motion_health_mhq001_final_decision.md) に置く。

結論は、市場需要はあるが、EPS/SbWサプライヤが公開情報だけで外販商品にできる差分は確認できない、である。
必要データはOEM/fleet/platform契約に依存し、既存remote diagnosticsもDTC severity、action plan、API連携、診断時間短縮をすでに扱っている。

ただし、新しい作業仮説として、OEM remote diagnostics networkに組み込む操舵系状態説明レイヤーは切り出す。
これはfleet監視サービスではなく、EPS/SbW内部データからDTCだけでは分からない状態説明、追加DID読み順、禁止主張、field-to-engineering feedbackを作る部品側コンテンツである。
入口は [docs/archive/oem_remote_diagnostics/78_oem_remote_diagnostics_eps_explanation_layer_hypothesis.md](oem_remote_diagnostics/78_oem_remote_diagnostics_eps_explanation_layer_hypothesis.md) に置く。
過去のmotion health調査は [docs/archive/motion_health/79_motion_health_archive_index.md](motion_health/79_motion_health_archive_index.md) へArchiveする。

Kaggle / 公開proxyによる予測的付加価値探索については、後続レビューで補正済みである。
「EPS内部状態、DTC、freeze frame、交換結果が見えないから全滅」という判断は撤回する。
最新判断は [docs/96_predictive_value_internal_fact_correction.md](../96_predictive_value_internal_fact_correction.md)、信用回復監査は [docs/97_trust_recovery_rule_check_audit.md](../97_trust_recovery_rule_check_audit.md) に置く。
修正後は、`PVC001`、`ULC008`、`ULC004`、`PVC004` を公開proxy価値の検証候補として残す。
補正後のビジネスモデル本線は [docs/98_business_model_mainline_after_correction.md](../98_business_model_mainline_after_correction.md) に置く。


## EPSサプライヤ視点

このRepoの結論は、必ずEPSサプライヤの立場に帰着させる。

市場、OEM、エンドユーザ、サービス、connected platform、規制、公開データをメタ視点で見るのはよい。
ただし、最終判断は以下で締める。

- EPSサプライヤとして何を売るか
- EPSサプライヤとして何を実施できるか
- EPSサプライヤとして何を言ってはいけないか
- OEM領域、サービス領域、fleet platform領域として初期対象外に置くものは何か
- 次にEPSサプライヤ内のどの部署に見せるか

当初はEPS故障予測やVehicle Health Managementを検討していたが、現在は以下の順で仮説が進化している。

```text
EPS故障予測
  -> EPS単体の個車RULは頻度・責任・データ面で弱い

EPS Health Intelligence Package
  -> EPSをhealth-aware subsystemとして差別化する

Development Evaluation First
  -> まず開発・耐久評価でECU信号ベースの指標価値を検証する

Common ECU Hardware Health Layer
  -> EPS固有メカ指標から、より横展開しやすいECU共通hardware healthへ広げる

Existing Diagnostics / OEM Boundary Check
  -> DTC、freeze frame、extended data、DEM/UDSは既存。価値があるなら、サプライヤ内部のNTF/返却品ケース棚卸しから不足証跡を特定する方向へ修正する

Public Proxy Data Reset
  -> 内部NTF/返却品ケースにアクセスできない前提に修正。公開市場情報、NHTSA、Kaggle、公開CAN datasetで補える範囲に限定する

Market Demand To Warranty / RCA Evidence
  -> 公開事例やscenario card単体ではなく、NTF、返却品解析、保証claim、SCAR/8D、顧客品質説明で使えるproduct-side evidence readinessへ軸を修正する

EPS Common Pain Productization
  -> RCA/8D単体はドメイン固有でスケールしにくい。公開市場で繰り返すEPS共通pain familyを、既存診断・reader・HILS/bench評価のcoverage benchmarkへ変換する
```

## 旧テーマの最終判断

旧テーマについては、以下を最終判断として扱う。

> Coverage Benchmarkは、内部資料なしでは止める。広いcyber/SBOM商品も既存業務・既存ツールと被るためKill寄りに下げる。Steer-by-wireの汎用説明支援も有償サービスとしてはNo-Go。SOVD / 次世代診断は基盤ではなく、EPS診断コンテンツの公開範囲・権限・禁止主張が製品仕様やRFQ回答に残るかだけをKill-firstで見る。

さらに旧テーマのメタ結論として、現行条件では外販ビジネスとしてProceedできる強い手札はほぼ残っていない。
次にこのRepoを読むLLMは、まずKill知識ベースを前提にすること。
過去にKillした仮説を、名前だけ変えて再提案しない。

Kaggle/Bosch線は、需要調査の枝としては有用だった。
ただし、これは製造品質、EOL検査、工程改善の話であり、EPS製品そのものの付加価値ではない。
したがって、Repoの主仮説にはしない。
本題に戻る場合は、EPS製品仕様、診断仕様、制御仕様、評価仕様、OEM説明に残る価値だけを主探索にする。

`ECU内に証跡を残す` こと自体は既存診断の範囲にあるため、新規性として扱わない。
`TARA/SBOM/CVE管理をやる` ことも既存CSMS/ISO21434/R155/R156対応と被るため、新規性として扱わない。
価値が残るとすれば、EPSサプライヤがcomponent boundaryで説明責任を持てる範囲を、OEM説明、設計レビュー、RFQ回答、診断コンテンツ設計に転記できる形にすることである。
Steer-by-wireでは、この範囲が従来EPSより広がる可能性がある。
ただし、公開情報を追加収集した結果、SbWの安全・認証・診断論点はNHTSA、VCA、R79、ASAM SOVDで既にかなり扱われている。
したがって、公開情報だけで有償offerへ進める判断はしない。
深掘り後の結論は、Steer-by-wire向けの汎用説明資料整理支援も有償サービスとしてはNo-Goである。
市場変化はあるが、異常時説明、安全設計、認証、診断、ソフト更新、顧客説明は既存業務の中に既に持ち主がいるためである。
次に見るなら、EPSサプライヤが持つDTC、DID、freeze frame、extended data、software/calibration ID、routine、security accessを、近接整備、リモート診断、車内診断、製造、開発の利用場面ごとに、公開/制限/禁止へ整理できるかを見る。
それが既存診断仕様やODX authoringの言い換えで終わるなら、SOVD / 次世代診断方向もStopする。

重要な境界:

- OEMの市場fleetデータ、保証DB、苦情DB、車両クラウドを初期前提にしない
- OTAやremote diagnosticsは主商品ではなく、読み出しチャネルの一つ
- 個車RULやエンドユーザ故障通知は初期主張にしない
- まずはEPSサプライヤが責任を持てるcomponent-levelの説明範囲に収める
- OEMデータ接続やfleet analyticsはOptional extensionに置く
- OEMに無手で聞きに行くのではなく、EPSサプライヤ側で持てる診断仕様、software/calibration ID、security access、fail-safe / degraded state、HILS/bench評価、公開市場scenarioから仮説を作ってから検証する
- `8D回答` という曖昧な言い方は避け、RCA/8Dや顧客品質報告は副次artifactとして扱う

## 現在の焦点

| 観点 | 現在の見立て |
|---|---|
| 最新判断 | 旧テーマ、単独fleet監視型motion health、RDI / OEM remote diagnostics説明レイヤーは外販商品としてArchive。Kaggle / 公開proxyによる予測的付加価値探索は、前回の全滅判断を補正し、PVC001 / ULC008 / ULC004 / PVC004を検証候補として残す |
| EPS向け軸 | 個車のEPS残寿命や交換時期を当てるとは言わない。OEMが想定する車両用途や使われ方を、操舵要求、路面・振動exposure、使用負荷class、通信異常contextなどのEPS側確認観点へ翻訳できるかを見る |
| 最終検証軸 | EPS内部状態、DTC、freeze frame、交換結果が見えないことを主Kill理由にしない。評価するのは、OEM用途想定をEPSサプライヤの製品企画、診断企画、品質改善、評価企画、顧客技術説明へ翻訳できるか |
| 近い商品名 | まだ作らない。自然言語では「OEM用途想定をEPS側の確認観点へ翻訳する検証候補」。外販商品ではなく検証候補である |
| RCA/8Dの扱い | 主商品ではない。特定programの短期支援で、確認済み事実の転記先になる場合だけ |
| Primary target | EPSサプライヤの商品企画、製品企画、診断企画、品質改善、評価企画。製造品質、EOL検査、評価時間短縮は別枝または補助材料として扱う |
| 初期データ前提 | 内部資料は使わない。Kaggleの公開課題を、データセットそのものではなく、外に出された問題設定と公開proxyとして読む |
| OEM / fleetデータ | 使わない。OEM保証DB、fleet data、service outcomeを必要とする方向へ戻さない |
| AI / 予測 | 予測のような付加価値を探索する。ただし個車RUL、交換時期、安全保証、保証費削減、root cause断定は主張しない。Kaggle精度競争ではなく、予測対象がEPSサプライヤの価値へ転記できるかを見る |
| 避ける主張 | EPS交換時期の正確予測、安全機能の代替、保証費削減断定、root cause断定、サプライヤ単独fleet監視 |
| Kaggle/Bosch線 | 公開データそのものではなく、外に出された問題設定から隠れた需要を読む観点として使う。Bosch型の製造品質 / EOL検査、Mercedes型の評価時間短縮は現テーマ外。KGL003/005/006/007/008は、OEM用途想定をEPS側確認観点へ翻訳するための公開proxy入力として残す |
| Bosch公開シグナル | BoschのAct-by-Wire、Vehicle Motion Management、Motion integration platform、AI/SDV公開情報は、EPS故障予測の根拠ではない。ただし、by-wire / motion-domain時代に、上位制御から操舵側へ来る要求を、EPSサプライヤの受け入れ境界、制限境界、診断境界、禁止主張へ翻訳する必要が増える可能性を示す |
| Bosch予測診断シグナル | 2026年のBosch / Uptake発表とBosch Predictive Diagnosticsでは、fleet / connected vehicle / cloud diagnostics文脈でAI-driven predictive maintenance、vehicle health、component-specific load and diagnostic featuresが明確に出ている。このブランチでは、steering predictive diagnostics / predictive maintenance / vehicle healthを正面から扱う |
| 次アクション | `ULC008` を最有力、`ULC004` を二番手、`PVC004` を境界候補として、OEM用途想定をどの業務成果物へ翻訳できるかを確認する。加えて、Bosch公開シグナルを受けて、上位motion controllerから来る操舵要求の受け入れ境界と、steering predictive diagnostics / predictive maintenance / vehicle healthの対象を確認する。4枚の最小パックは `docs/100`、質問票は `docs/101`、Bosch motion枝は `docs/102`、Bosch予測診断枝は `docs/103`、操舵系predictive state候補は `docs/104`、Bosch予測ビジネス分析は `docs/105`、screening計画は `docs/106`、Phase 1/2結果は `docs/107`、Proceed深掘りは `docs/108`、Phase 3 data boundaryは `docs/109`、Phase 4 supplier workflow fitは `docs/110`、Phase 5 screening decisionは `docs/111`、継続候補の並列深掘りは `docs/112`、見込み候補の深掘りは `docs/113`、SPD別の一定結論は `docs/114`、SPD008/SPD002のartifactと比較判断は `docs/115`〜`docs/117`、SPD008 first samplesは `docs/118`、観点補正は `docs/119`、predictive value checkは `docs/120`、power monitor 1ケースは `docs/121`、payload sampleは `docs/122`、program別照合質問シートは `docs/123`、communication input validityの独立ケースは `docs/124`、未検証デルタのファクトチェックは `docs/125`、SOTIFへの乗り方の判定は `docs/126` に切り出した。SOTIFはプロセス支援商品としてはNo-Go、SOTIF運用フェーズのフィールド監視への部品側インプット(SPD008 payloadの宛先追加)としてだけ条件付き検証候補に残す。入口条件はKQ1(SOTIF由来のfault未満監視要求が部品側RFQへ実際に降りてきているか)であり、確認できるまで工数を割かない。故障予測はKill維持。最終判断は、SPD008を次の本線候補、SPD002をreference demoに置く(SPD002は `docs/125` で意図的凍結を明文化)。デルタ検証の結果、価値主張は「既存monitorでは残らない」ではなく「既存標準(AUTOSAR Dem)は残す設定余地を持つが、機能影響との同時性や閾値未満eventの再発は残らない設計が多く、EPSサプライヤがcomponent boundaryで設計できる」に言い直した。`docs/123` の質問シートのprogram固有欄の回答取得は、内部資料(対象programの診断仕様)への接触が必要なため、次アクションに置かず、内部資料を使える条件になった場合だけの実施条件として保存する(Coverage Benchmark / SbWと同じ扱い)。ターゲットケース(permanent DTCが残らない断続的なassist低下)の公開実在確認は `docs/127` で完了し、Confirmedとした(Ford 15V-340是正手順の「DTCなし」経路、GM 17V-414の約1秒の一時喪失・突然復帰、GM TSB 17-NA-158の外部signal起因操舵警告、Tesla EA24001の過電圧起因ほか)。さらに `docs/129` で、判定ゲートの照合対象を「サプライヤprogram」から「公開リコール是正実務」へ組み替え、Ford 15S18とGM 17276のディーラー向け一次文書を精読した結果、5項目中4項目の差分(DTC未満event、snapshot利用、同時性、再発がいずれも是正実務に存在せず、判断はDTC有無の1bitのみ)を公開レベルでConfirmedした。これによりSPD008 power monitorは「公開レベルConfirmed付き限定Proceed」となり、内部資料条件は仮説検証ではなく実行のみ(現行世代のサプライヤ設定確認=`docs/123` 質問シート、2部署以上の使い道確認、SOTIF KQ1)に縮小した。`docs/130` では同じ手法を第二候補のcommunication input validityに適用し、GM TSB 17-NA-158の原文(無効な冷却水温signal→操舵警告→「U0401:71でgearを交換するな」という公式警告と誤交換の記録)により、Hold→「公開レベルConfirmed付き限定Proceed(第二候補)」へ引き上げた。このTSBの内容はSPD008 payloadと同一のfield構成であり、SPD008は「OEMが誤交換の後に人手で書くservice文書を、部品側がruntimeで機械的に出せるようにする」提案だと言い直せる。副産物として、Ford SSM 49530(2021年F-150、始動時電圧8V未満→内部故障系code U3000:96保存→PSCM交換不要とOEMが説明)により、現行世代でもpower contextの誤帰属が続いていることを確認した。EPS RUL/交換時期予測やBosch型fleet platformとしてはProceedしない。内部事実の不足だけでKillしない |


## プロジェクトSkill

このRepoでは、事業仮説の探索と検証をCodex側に寄せるため、プロジェクトSkillを追加している。

- `future-need-interviewing`: 顧客の最初のニーズ、最悪の未来、最高の未来、欲しい感情から本当のニーズを掘る。
- `chain-of-verification`: 叩き台の結論を検証質問に分解し、エビデンスで潰してから修正版を出す。
- `human-readable-reporting`: 人間向けレポートで、造語・商品名・phase名より先に自然言語で結論、業務文脈、判定条件を説明する。

## ビジネスモデル成立性の整理

今回追加した100案の整理では、以下を重視した。

- ECUメーカー起点で始められる
- OEMデータを初期前提にしない
- EPS / ECUの付加価値として説明できる
- HILS / bench / durability logでデモしやすい
- 将来OEM VHM / connected diagnosticsへ拡張できる

Best5:

| Rank | ID | Candidate |
|---:|---|---|
| 1 | BMFE020 | Health-ready EPS Feature Bundle |
| 2 | BMFE001 | EPS Health Indicator Set Licensing |
| 3 | BMFE031 | Offline Health Indicator Analyzer |
| 4 | BMFE041 | Return-part Health Summary Reader |
| 5 | BMFE096 | Co-development with Gear Maker |

推奨初手:

> Health Indicator Starter Kitを入口にして、Offline Health Indicator Analyzerでデモし、成功した指標をHealth-ready EPS Feature Bundleへ拡張する。

## 主要プロダクト仮説

### EPS Health Intelligence Package

過去の仮説。
EPSを、故障してからDTCを出す部品ではなく、劣化兆候と予測材料を持つhealth-aware subsystemにする方向を検討した。

現在は、`劣化兆候` や `内蔵証跡` を新規価値として主張するのは弱いと判断している。
以下の候補指標は、内部案件レビューで `実際に解析を進める証跡か` を確認するまでは仮説扱いにする。

候補指標:

- assist current / load proxy
- steering torque to motor current ratio
- current tracking warning count
- torque sensor redundancy / drift
- steering angle sensor redundancy / drift
- thermal derating accumulation
- low voltage stress history
- assist limitation recurrence
- high-load / low-speed event count
- end-stop / curb-hit-like event count
- transient abnormal recovery count

### Development Evaluation Indicator

ギア / ラック / 機械負荷を、ECU信号ベースのcontrol effort / stress / margin indicatorで比較する。
ただし、開発時の外付けモニタとの差分が弱いため、現在は主軸から下げている。

### Common ECU Hardware Health Layer

EPS固有メカ指標に閉じず、電源、温度、リップル、brownout、reset、capacitor stressなど、ECU横断で使えるhardware health evidenceへ広げる。
これは将来ピボットとして残すが、現在のEPSサプライヤ視点では、先に返却品・NTFケースの不足証跡分類を行う。

## リポジトリ構成

```text
AGENTS.md
  Repo-wide operating rule: market demand -> hypothesis -> solution.

docs/
  00_context.md
  01_business_model_options.md
  02_option_comparison.md
  03_supplier_scope.md
  04_project_charter_diagnostic_evidence.md
  05_risks_and_open_questions.md
  06_next_actions.md
  07_market_needs_and_positioning.md
  08_ota_connected_health_market.md
  09_feasibility_and_targeting.md
  10_project_charter_eps_health_intelligence.md
  11_virtual_health_sensor_market.md
  12_reset_hypothesis_development_evaluation.md
  13_business_scheme_reset.md
  15_public_driving_data_proxy_simulation.md
  16_common_ecu_hardware_health_pivot.md
  17_customer_value_reality_check.md
  18_market_research_customer_pain.md
  19_market_research_eps_event_context.md
  20_existing_diagnostics_oem_boundary.md
  21_value_of_ntf_case_classification.md
  22_public_proxy_data_reset.md
  23_public_proxy_demo_plan.md
  24_steering_context_risk_phase1.md
  25_low_speed_high_steering_proxy_phase2.md
  26_scenario_to_evidence_pack_direction.md
  27_s2e001_diagnostic_evidence_gap_check.md
  28_s2e001_diagnostic_evidence_review_template.md
  29_business_model_rebranch_after_s2e001_hold.md
  30_bmr001_market_pain_scenario_cards.md
  31_bmr002_rfq_design_review_pack.md
  32_market_demand_solution_framing.md
  33_public_data_validation_scn001.md
  34_eps_supplier_business_model_reassessment.md
  35_rca_8d_case_pack_viability_report.md
  36_eps_common_pain_productization_scan.md
  37_eps_coverage_benchmark_business_value.md
  38_fam08_stop_start_low_speed_coverage_benchmark_sample.md
  39_fam08_immediate_visibility_review.md
  40_coverage_benchmark_p1_assessment_package.md
  41_coverage_benchmark_artifact_request_pack.md
  42_coverage_benchmark_artifact_intake_result.md
  43_coverage_benchmark_forced_conclusion.md
  48_steering_ecu_cyber_value_check.md
  49_steering_ecu_cyber_kill_evidence_dossier.md
  50_next_exploration_plan_after_cyber_kill.md
  51_steer_by_wire_kill_first_review.md
  52_sovd_kill_first_review.md
  53_public_market_monitor_input_only.md
  54_steer_by_wire_business_deep_dive.md
  55_sbw_redundancy_degraded_one_page_sample.md
  56_sbw_decision_materials.md
  57_sbw_8_material_verification.md

data/
  business_model_research.tsv
  business_model_feasibility_100.tsv
  business_model_feasibility_sources.md
  best5_business_model_candidates.md
  demo_eps_health_summary_examples.tsv
  customer_pain_market_signals.tsv
  eps_public_market_pain_cases.tsv
  eps_event_context_market_research.tsv
  eps_ntf_case_classification_value_map.tsv
  eps_ntf_case_review_template.tsv
  public_steering_dataset_inventory.tsv
  steering_context_risk_phase1_summary.tsv
  low_speed_high_steering_proxy_summary.tsv
  low_speed_high_steering_proxy_windows.tsv
  low_speed_high_steering_proxy_timeseries.tsv
  eps_scenario_to_evidence_pack.tsv
  s2e001_diagnostic_evidence_gap_check.tsv
  s2e001_diagnostic_evidence_review_template.tsv
  business_model_rebranch_after_s2e001_hold.tsv
  bmr001_market_pain_scenario_cards.tsv
  bmr002_rfq_design_review_pack.tsv
  market_demand_solution_map.tsv
  public_data_validation_sources.tsv
  scn001_public_data_evidence_readiness.tsv
  eps_supplier_business_model_reassessment.tsv
  rca_8d_case_pack_viability_assessment.tsv
  eps_common_market_pain_reclassification.tsv
  eps_common_pain_business_scores.tsv
  eps_coverage_benchmark_business_value.tsv
  fam08_stop_start_low_speed_coverage_benchmark_sample.tsv
  fam08_immediate_visibility_triage.tsv
  coverage_benchmark_p1_assessment_plan.tsv
  coverage_benchmark_family_reuse_matrix.tsv
  coverage_benchmark_p1_decision_rubric.tsv
  coverage_benchmark_artifact_request_pack.tsv
  coverage_benchmark_artifact_intake_result.tsv
  coverage_benchmark_artifact_intake_decision.tsv
  coverage_benchmark_internal_placeholder_screening_sheet.tsv
  coverage_benchmark_forced_conclusion.tsv
  steering_ecu_cyber_value_check.tsv
  steering_ecu_cyber_kill_evidence_dossier.tsv
  steering_ecu_cyber_kill_questions.tsv
  next_exploration_candidates_after_cyber_kill.tsv
  steer_by_wire_kill_first_review.tsv
  sovd_kill_first_review.tsv
  public_market_monitor_input_plan.tsv
  steer_by_wire_business_deep_dive.tsv
  steer_by_wire_redundancy_degraded_sample.tsv
  sbw_decision_materials.tsv
  sbw_8_material_verification.tsv
  public_proxy_data_sources.tsv
  useful_items_for_steering_diagnostic_evidence.md
  ota_connected_health_market_signals.tsv
  target_feasibility_matrix.tsv
  eps_health_indicator_candidates.tsv

generated/
  coverage_benchmark_forced_conclusion.html
  coverage_benchmark_artifact_intake_result.html
  coverage_benchmark_artifact_request.html
  coverage_benchmark_p1_assessment.html
  fam08_immediate_visibility_review.html
  public_data_validation_scn001.html
  market_demand_solution_framing.html
  bmr002_rfq_design_review_pack.html
  bmr001_market_pain_scenario_cards.html
  business_model_rebranch_after_s2e001_hold.html
  s2e001_diagnostic_evidence_review_template.html
  s2e001_diagnostic_evidence_gap_check.html
  eps_scenario_to_evidence_pack.html
  low_speed_high_steering_proxy.html
  steering_context_risk_explorer_phase1_ja.html
  steering_context_risk_explorer_phase1.html

scripts/
  extract_low_speed_high_steering_proxy.py
```

## 現在の次アクション

- 以後の提案は `AGENTS.md` の上位ルールに従い、市場需要 -> 未解決の痛み -> 仮説 -> 解決策 -> 買い手 -> 初期提供物 -> 検証方法 -> Kill条件で書く
- 旧テーマはArchiveとして閉じる。詳細は [docs/68_repo_closure_inventory.md](../68_repo_closure_inventory.md) と [data/repo_closure_inventory.tsv](../../data/repo_closure_inventory.tsv) を参照する
- motion health新テーマも外販テーマとしてはArchive。最終判断は [docs/archive/motion_health/75_motion_health_mhq001_final_decision.md](motion_health/75_motion_health_mhq001_final_decision.md) を参照する
- RDI / OEM remote diagnostics系は [docs/archive/oem_remote_diagnostics/README.md](oem_remote_diagnostics/README.md) を入口にArchive参照する
- RDI001〜RDI006の公開情報調査は [docs/archive/oem_remote_diagnostics/81_rdi001_006_research_report.md](oem_remote_diagnostics/81_rdi001_006_research_report.md) と [data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi_research_findings.tsv](../../data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi_research_findings.tsv) を参照する
- RDI006の4列sampleは [docs/archive/oem_remote_diagnostics/82_rdi006_thermal_limit_4_column_sample.md](oem_remote_diagnostics/82_rdi006_thermal_limit_4_column_sample.md) と [data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_thermal_limit_sample.tsv](../../data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_thermal_limit_sample.tsv) に置いた
- RDI006の穴埋めPDCAは [docs/archive/oem_remote_diagnostics/83_rdi006_program_gap_pdca.md](oem_remote_diagnostics/83_rdi006_program_gap_pdca.md) と [data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_program_gap_filled.tsv](../../data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_program_gap_filled.tsv) に置いた
- 次に作業する場合は、[docs/84_kaggle_problem_setting_lens.md](../84_kaggle_problem_setting_lens.md) を入口に、Bosch型をEPS製造 / EOL検査へ読み替える
- 過去のmotion health調査は [docs/archive/motion_health/79_motion_health_archive_index.md](motion_health/79_motion_health_archive_index.md) と [data/archive/motion_health/motion_health_archive_links.tsv](../../data/archive/motion_health/motion_health_archive_links.tsv) から参照する
- 「EPS交換時期を当てる」方向には戻さない
