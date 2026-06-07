# Steering Health Intelligence Notes

EPS / ステアリングECUを起点に、ECU内部信号からhealth / stress / control-effort indicatorを作る事業仮説メモ。

## 上位ルール

このRepoでは、以後の調査・仮説・デモ・ドキュメント更新を必ず以下の順で提示する。

> 市場需要 -> 未解決の痛み -> 仮説 -> 解決策 -> 買い手/利用者 -> 初期提供物 -> 検証方法 -> Kill条件

悪い提示:

> EPSにこういう公開事例がある。

良い提示:

> 市場ではloss of assist、低速高操舵、警告灯+DTC、intermittent assist loss、stop-start、software/failsafeなどのEPS共通pain familyが繰り返し問題化している。EPSサプライヤは、各scenarioに対して既存DTC/freeze frame/extended data、reader、HILS/bench評価がどこまで説明・再現できるかをCoverage Benchmarkとして提示できる。

### 自然言語優先

レポートや結論では、造語、商品名、略称、phase名を先に出さない。
必ず先に、自然言語で以下を説明する。

- 何を判断しているのか
- 誰のどの業務の話なのか
- 何が分かれば進み、何が分かれば止めるのか
- 既存業務、既存診断、既存評価と何が違う可能性があるのか

悪い提示:

> P1 paid assessmentとしてCoverage BenchmarkはNo-Go。P0 ScreeningだけProceed。

良い提示:

> 現時点では、有償サービスとして売りに行く段階ではない。内部資料を使わない前提では、対象EPSのHILS試験名、関連DTC、freeze frame / extended data項目、既存レビュー会議体を見られず、既存レビューとの差分を示せないためである。これらの4項目は、内部資料を使える条件になった場合だけの再開条件として扱う。

`Coverage Benchmark`、`P0`、`P1`、`Evidence Pack`、`Readiness`、`screening` のような言葉は使ってよい。
ただし、自然言語で意味を説明した後にだけ使う。

過去の探索メモはhistoricalとして扱う。
`EPS故障予測`、`劣化兆候通知`、`Health-ready EPS`、`ECU追加ログ`、`Market Pain Scenario Library単体`、`RFQ / Design Review Pack単体` は、最新結論ではない。
`RCA / 8D Evidence Case Pack` は単独主商品から下げる。
`EPS Diagnostic / Robustness Coverage Benchmark` も、内部資料を使わない現行方針ではNo-Goとして止める。

現在は、公開されている規制、標準、業界動向から、EPSサプライヤ側に実務負荷が増えている領域を探している。
直近の探索対象は以下の3つだったが、深掘り後は1だけを狭く残す。

1. Steer-by-wire safety / cybersecurity / redundancy
2. SOVD / next-generation diagnostics content design for EPS
3. Public recall / ODI / TSB monitor as input only

現在残すのは、Steer-by-wireの汎用安全支援ではない。
既存の安全・サイバー・診断・software update成果物を、OEM説明、RFQ回答、診断コンテンツ設計に転記しやすくするcomponent-boundary整理だけである。

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

## 現在の立ち位置

現時点では、以下を最新判断として扱う。

> Coverage Benchmarkは、内部資料なしでは止める。広いcyber/SBOM商品も既存業務・既存ツールと被るためKill寄りに下げる。SOVDと公開市場モニタは主商品にせず、Steer-by-wireのcomponent-boundary整理だけを狭く残す。

`ECU内に証跡を残す` こと自体は既存診断の範囲にあるため、新規性として扱わない。
`TARA/SBOM/CVE管理をやる` ことも既存CSMS/ISO21434/R155/R156対応と被るため、新規性として扱わない。
価値が残るとすれば、EPSサプライヤがcomponent boundaryで説明責任を持てる範囲を、OEM説明、設計レビュー、RFQ回答、診断コンテンツ設計に転記できる形にすることである。
Steer-by-wireでは、この範囲が従来EPSより広がる可能性がある。

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
| 最新ピボット | Public regulation / software / next-generation steering exploration |
| EPS向け軸 | Steer-by-wire component-boundary整理 |
| 初期検証軸 | 既存ISO 26262 / SOTIF / CSMS / TARA / 診断設計 / software update業務と被らず、EPSサプライヤがOEM説明や診断設計へ転記できる差分があるか |
| 近い商品名 | まだ作らない。商品名化前のKill-first探索 |
| RCA/8Dの扱い | 単独主商品から下げる。副次artifactとしてのみ扱う |
| Primary target | EPS supplier systems / functional safety / diagnostic engineering / cybersecurity / software calibration / customer technical interface |
| 初期データ前提 | 公開規制・標準・サプライヤ発表・公開NHTSA/recall/ODI/TSB |
| OEMデータ | Optional extension |
| AI / 予測 | 初期は故障予測モデルではなく、公開情報から設計レビュー・診断コンテンツ・RFQ質問へ転記できるかの探索 |
| 避ける主張 | 個車RUL断定、エンドユーザ故障通知、サプライヤ単独fleet監視、既存診断証跡の新規実装主張 |

## 推奨読書順

まず読むなら、この順番が分かりやすい。

1. [docs/54_steer_by_wire_business_deep_dive.md](docs/54_steer_by_wire_business_deep_dive.md): Steer-by-wire方向を事業成立性まで深掘りした最新判断。汎用安全支援ではなく、OEM説明・診断設計へ転記するcomponent-boundary整理だけを狭く残す。
2. [data/steer_by_wire_business_deep_dive.tsv](data/steer_by_wire_business_deep_dive.tsv): SbW方向の市場需要、未解決の痛み、仮説、初期提供物、Kill条件を整理したTSV。
3. [docs/57_sbw_8_material_verification.md](docs/57_sbw_8_material_verification.md): SbW内部8項目を公開情報で検証した結果。公開情報だけではProceed/Kill不可、1-4はPartial、5-8はUnknown。
4. [data/sbw_8_material_verification.tsv](data/sbw_8_material_verification.tsv): 8項目ごとのpublic verification result、公開情報で分からないこと、decision impact、次の内部確認。
5. [docs/56_sbw_decision_materials.md](docs/56_sbw_decision_materials.md): SbW方向をProceed / Killするために集めた判断材料。公開ソースから見えることと、内部で確認すべき8項目を分ける。
6. [data/sbw_decision_materials.tsv](data/sbw_decision_materials.tsv): ZF、Mercedes-Benz、Tesla、Lexus、HELLA、NHTSA、VCAの公開情報を、判断への使い方、強める点、弱める点へ対応づけたTSV。
7. [data/sbw_internal_decision_material_checklist.tsv](data/sbw_internal_decision_material_checklist.tsv): SbW方向を内部でProceed / Killするための8項目チェックリスト。
8. [data/steer_by_wire_minimum_artifact_request.tsv](data/steer_by_wire_minimum_artifact_request.tsv): SbW方向をProceed / Killするための最小artifact request。対象architecture、degraded state、FMEA、diagnostic content、software update、security access、OEM質問を確認する。
9. [docs/55_sbw_redundancy_degraded_one_page_sample.md](docs/55_sbw_redundancy_degraded_one_page_sample.md): road wheel actuator冗長低下を題材にした1ケースsample。既存safety caseの焼き直しか、横断整理として価値があるかを見る。
10. [data/steer_by_wire_redundancy_degraded_sample.tsv](data/steer_by_wire_redundancy_degraded_sample.tsv): 1ケースsampleのfield、supplier-owned source、OEM回答価値、Kill条件。
11. [docs/51_steer_by_wire_kill_first_review.md](docs/51_steer_by_wire_kill_first_review.md): Steer-by-wire安全・冗長・cyber方向の一次レビュー。市場変化はあるが、既存安全業務と被るためHold / explore next。
12. [data/steer_by_wire_kill_first_review.tsv](data/steer_by_wire_kill_first_review.tsv): Steer-by-wireの市場シグナル、EPSサプライヤが持てる手札、Kill条件を整理したTSV。
13. [docs/52_sovd_kill_first_review.md](docs/52_sovd_kill_first_review.md): SOVD / next-generation diagnostics方向の一次レビュー。主商品ではなく、EPS診断コンテンツ設計のextensionとしてのみ残す。
14. [data/sovd_kill_first_review.tsv](data/sovd_kill_first_review.tsv): SOVD標準・既存ツール・EPSサプライヤ残余価値・Kill条件を整理したTSV。
15. [docs/42_coverage_benchmark_artifact_intake_result.md](docs/42_coverage_benchmark_artifact_intake_result.md): Coverage BenchmarkのArtifact Intake実行結果。
16. [data/coverage_benchmark_artifact_intake_result.tsv](data/coverage_benchmark_artifact_intake_result.tsv): 10 artifactごとのplaceholder、実資料有無、今判定できること、できないこと、status。
17. [data/coverage_benchmark_artifact_intake_decision.tsv](data/coverage_benchmark_artifact_intake_decision.tsv): Artifact intake後のProceed/Hold/Kill判断表。
18. [data/coverage_benchmark_internal_placeholder_screening_sheet.tsv](data/coverage_benchmark_internal_placeholder_screening_sheet.tsv): 内部資料を使える場合だけ参照する4項目screening sheet。
19. [generated/coverage_benchmark_p1_assessment.html](generated/coverage_benchmark_p1_assessment.html): FAM08/FAM02/FAM11を使ったP1 assessment packageのクイックHTML。
20. [docs/40_coverage_benchmark_p1_assessment_package.md](docs/40_coverage_benchmark_p1_assessment_package.md): Coverage BenchmarkのP1 assessment最小構成。
21. [data/coverage_benchmark_p1_assessment_plan.tsv](data/coverage_benchmark_p1_assessment_plan.tsv): P1 workstream、入力、出力、owner、timebox、Proceed/Kill条件。
22. [data/coverage_benchmark_family_reuse_matrix.tsv](data/coverage_benchmark_family_reuse_matrix.tsv): FAM08/FAM02/FAM11で同じrow構造を再利用できるかのmatrix。
23. [data/coverage_benchmark_p1_decision_rubric.tsv](data/coverage_benchmark_p1_decision_rubric.tsv): P1のProceed / Hold / Kill判定ルーブリック。
24. [generated/fam08_immediate_visibility_review.html](generated/fam08_immediate_visibility_review.html): FAM08が今日すぐProceed / Hold / Kill判定できるかを見るクイックHTML。
25. [docs/39_fam08_immediate_visibility_review.md](docs/39_fam08_immediate_visibility_review.md): `FAM08 stop-start low-speed` の即時可視性レビュー。
26. [data/fam08_immediate_visibility_triage.tsv](data/fam08_immediate_visibility_triage.tsv): FAM08のmarket fit、HILS重複、DTC snapshot、workflow fitを即時triageするTSV。
27. [docs/38_fam08_stop_start_low_speed_coverage_benchmark_sample.md](docs/38_fam08_stop_start_low_speed_coverage_benchmark_sample.md): `FAM08 stop-start low-speed` の1ページcoverage benchmark sample。
28. [data/fam08_stop_start_low_speed_coverage_benchmark_sample.tsv](data/fam08_stop_start_low_speed_coverage_benchmark_sample.tsv): FAM08 sampleのreview item、expected EPS facts、coverage question、HILS/bench scenario、Kill条件。
29. [docs/37_eps_coverage_benchmark_business_value.md](docs/37_eps_coverage_benchmark_business_value.md): Coverage Benchmark線でビジネス価値が出るかを、買い手・予算・代替・Kill条件まで深掘りしたレポート。
30. [data/eps_coverage_benchmark_business_value.tsv](data/eps_coverage_benchmark_business_value.tsv): business model別に市場需要、未解決痛み、買い手、予算経路、proof demo、Kill条件を整理したTSV。
31. [docs/36_eps_common_pain_productization_scan.md](docs/36_eps_common_pain_productization_scan.md): EPS共通pain familyから、スケール可能な事業候補を再抽出したレポート。
32. [data/eps_common_pain_business_scores.tsv](data/eps_common_pain_business_scores.tsv): 13 familyの共通性、サプライヤ制御性、差別化、スケール性のスコア表。
33. [data/eps_common_market_pain_reclassification.tsv](data/eps_common_market_pain_reclassification.tsv): 公開EPS case 30件の共通pain family再分類。
34. [docs/35_rca_8d_case_pack_viability_report.md](docs/35_rca_8d_case_pack_viability_report.md): `RCA / 8D Evidence Case Pack` が単独主商品として弱いことを検証したレポート。
35. [data/rca_8d_case_pack_viability_assessment.tsv](data/rca_8d_case_pack_viability_assessment.tsv): 成立条件、代替品、EPSサプライヤ適合、収益モデル、Kill条件の評価表。
36. [docs/34_eps_supplier_business_model_reassessment.md](docs/34_eps_supplier_business_model_reassessment.md): 上位ルール後に既存データを再評価し、主商品をcase packへ寄せた判断。現在はhistorical寄り。
37. [data/eps_supplier_business_model_reassessment.tsv](data/eps_supplier_business_model_reassessment.tsv): EPSサプライヤ視点の再評価表。現在はhistorical寄り。
38. [docs/20_existing_diagnostics_oem_boundary.md](docs/20_existing_diagnostics_oem_boundary.md): 既存DEM/UDS診断との差分、OEM領分、サプライヤ側の現実的な手札。
39. [docs/22_public_proxy_data_reset.md](docs/22_public_proxy_data_reset.md): 内部ケースにアクセスできない前提で、公開市場情報/Kaggle/公開CANデータで補える範囲を再定義。
40. [docs/27_s2e001_diagnostic_evidence_gap_check.md](docs/27_s2e001_diagnostic_evidence_gap_check.md): S2E001を既存DTC/freeze frameで説明できるか見るgap check。
41. [docs/28_s2e001_diagnostic_evidence_review_template.md](docs/28_s2e001_diagnostic_evidence_review_template.md): 内部DTC仕様を入れてProceed/Kill/Holdを判定するレビュー手順。
42. [docs/29_business_model_rebranch_after_s2e001_hold.md](docs/29_business_model_rebranch_after_s2e001_hold.md): S2E001 Hold後のビジネスモデル再分岐。
43. [docs/30_bmr001_market_pain_scenario_cards.md](docs/30_bmr001_market_pain_scenario_cards.md): BMR001の初期3枚scenario cardと商品化境界。最新では主商品ではなく前段材料。
44. [docs/31_bmr002_rfq_design_review_pack.md](docs/31_bmr002_rfq_design_review_pack.md): BMR001をRFQ/設計レビュー1ページへ変換したBMR002 sample。最新では主商品ではなく副産物。
45. [docs/23_public_proxy_demo_plan.md](docs/23_public_proxy_demo_plan.md): `Steering Context Risk Explorer` の代理デモ計画。
46. [generated/bmr002_rfq_design_review_pack.html](generated/bmr002_rfq_design_review_pack.html): BMR002 Scenario Readiness Pageのブラウザ表示。
47. [generated/bmr001_market_pain_scenario_cards.html](generated/bmr001_market_pain_scenario_cards.html): BMR001 scenario cardのブラウザ表示。
48. [generated/business_model_rebranch_after_s2e001_hold.html](generated/business_model_rebranch_after_s2e001_hold.html): 再分岐の意思決定ビュー。
49. [generated/s2e001_diagnostic_evidence_review_template.html](generated/s2e001_diagnostic_evidence_review_template.html): S2E001 review templateの意思決定ビュー。
50. [generated/s2e001_diagnostic_evidence_gap_check.html](generated/s2e001_diagnostic_evidence_gap_check.html): S2E001 gap checkの意思決定ビュー。
51. [generated/eps_scenario_to_evidence_pack.html](generated/eps_scenario_to_evidence_pack.html): Scenario-to-Evidence Packの意思決定ビュー。
52. [generated/low_speed_high_steering_proxy.html](generated/low_speed_high_steering_proxy.html): Phase 2の代表window可視化。
53. [generated/steering_context_risk_explorer_phase1_ja.html](generated/steering_context_risk_explorer_phase1_ja.html): ブラウザで見られるPhase 1静的デモ日本語版。
54. [generated/steering_context_risk_explorer_phase1.html](generated/steering_context_risk_explorer_phase1.html): Phase 1静的デモ英語版。
55. [data/eps_public_market_pain_cases.tsv](data/eps_public_market_pain_cases.tsv): NHTSA/recall/investigationから抽出したdriver-visible EPS painケース。
56. [data/public_steering_dataset_inventory.tsv](data/public_steering_dataset_inventory.tsv): 公開steering / CAN / Kaggle dataset棚卸し。

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
  steer_by_wire_minimum_artifact_request.tsv
  steer_by_wire_redundancy_degraded_sample.tsv
  sbw_decision_materials.tsv
  sbw_internal_decision_material_checklist.tsv
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
- `EPS Diagnostic / Robustness Coverage Benchmark` は、内部資料を使わない現行方針ではNo-Goとして止める
- 広い `steering ECU software/cyber evidence pack` は、既存CSMS/TARA/SBOM/CVE運用と被るためKill寄りに下げる
- 次は `Steer-by-wire` を狭く見る。ただし、汎用安全支援ではなく、既存成果物をOEM説明・診断設計へ転記するcomponent-boundary整理に限定する
- `SOVD / next-generation diagnostics content design` は主商品ではなく、EPS診断コンテンツの整理・露出方針・UDSからSOVDへの接続に限定して残す
- `Public recall / ODI / TSB monitor` は単体商品にせず、Steer-by-wireとSOVDの設計質問・診断質問を作る入力としてだけ使う
- road wheel actuator redundancy degradedの1ケースsampleは作成済み。次は、このsampleが既存safety caseからすぐ出るか、部署横断でないと作れないかを見る
- 判断材料として、ZF、Mercedes-Benz、Tesla、Lexus、HELLA、NHTSA、VCAの公開情報を整理済み。公開情報だけでは商品価値は証明せず、内部8項目でProceed / Killを切る
- 8項目を公開情報で検証した結果、1-4はPartial、5-8はUnknown。公開情報だけではProceed/Killできない
