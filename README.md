# Steering Health Intelligence Notes

EPS / ステアリングECUを起点に、ECU内部信号からhealth / stress / control-effort indicatorを作る事業仮説メモ。

## 上位ルール

このRepoでは、以後の調査・仮説・デモ・ドキュメント更新を必ず以下の順で提示する。

> 市場需要 -> 未解決の痛み -> 仮説 -> 解決策 -> 買い手/利用者 -> 初期提供物 -> 検証方法 -> Kill条件

悪い提示:

> EPSにこういう公開事例がある。

良い提示:

> 市場ではNTF、返却品解析、保証claim、SCAR/8D、顧客品質説明で、サプライヤ側が使えるproduct-side evidence不足が痛みになっている。EPSサプライヤは、scenario別に必要factsを定義し、既存DTC/freeze frame/extended dataで説明できるかを確認するEvidence Readiness Packを提供できる。

過去の探索メモはhistoricalとして扱う。
`EPS故障予測`、`劣化兆候通知`、`Health-ready EPS`、`ECU追加ログ`、`Market Pain Scenario Library単体`、`RFQ / Design Review Pack単体` は、最新結論ではない。
最新の主仮説は `EPS Warranty / RCA Evidence Readiness Pack` である。

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
```

## 現在の立ち位置

現時点では、以下を中心仮説として扱う。

> EPSサプライヤが、NTF、返却品解析、保証claim、SCAR/8D、顧客品質説明で必要になるproduct-side factsをscenario別に定義し、既存DTC / freeze frame / extended dataで説明できるかを確認する `EPS Warranty / RCA Evidence Readiness Pack` を作る。

`ECU内に証跡を残す` こと自体は既存診断の範囲にあるため、新規性として扱わない。
新規性があるとすれば、公開市場caseや代表scenarioを使って、RCA/8D/顧客品質報告で必要な事実項目、未確認事項、推定禁止事項を整理し、既存診断で足りる/足りないを判断できる形にすること。

重要な境界:

- OEMの市場fleetデータ、保証DB、苦情DB、車両クラウドを初期前提にしない
- OTAやremote diagnosticsは主商品ではなく、読み出しチャネルの一つ
- 個車RULやエンドユーザ故障通知は初期主張にしない
- まずはECUメーカーが責任を持てるCore packageを作る
- OEMデータ接続やfleet analyticsはOptional extensionに置く
- OEMに無手で聞きに行くのではなく、サプライヤ側の過去案件から不足証跡仮説を作ってから検証する
- `8D回答` という曖昧な言い方は避け、顧客品質報告、返却品解析報告、NTF調査メモ、D2 / D4向けの事実整理として扱う

## 現在の焦点

| 観点 | 現在の見立て |
|---|---|
| 最新ピボット | Market Demand To Warranty / RCA Evidence |
| EPS向け軸 | EPS Warranty / RCA Evidence Readiness |
| 初期検証軸 | NTF / 返却品解析 / 保証claim / 8Dで使えるproduct-side factsを定義できるか |
| 近い商品名 | EPS Warranty / RCA Evidence Readiness Pack |
| Primary target | EPS supplier warranty / supplier quality / diagnostic engineering / customer quality |
| 初期データ前提 | 公開NHTSA/recall/ODI/TSB、公開走行proxy、既存DTC/freeze frame/extended dataのレビュー観点 |
| OEMデータ | Optional extension |
| AI / 予測 | 初期は故障予測モデルではなく、NTF/RCA/品質報告に使う証拠整理 |
| 避ける主張 | 個車RUL断定、エンドユーザ故障通知、サプライヤ単独fleet監視、既存診断証跡の新規実装主張 |

## 推奨読書順

まず読むなら、この順番が分かりやすい。

1. [docs/32_market_demand_solution_framing.md](docs/32_market_demand_solution_framing.md): 市場需要から解決策へ組み替えた最新結論。
2. [generated/market_demand_solution_framing.html](generated/market_demand_solution_framing.html): Demand-to-solution framingのブラウザ表示。
3. [data/market_demand_solution_map.tsv](data/market_demand_solution_map.tsv): 市場需要、未解決の痛み、解決仮説、買い手、demo、Kill条件の対応表。
4. [docs/20_existing_diagnostics_oem_boundary.md](docs/20_existing_diagnostics_oem_boundary.md): 既存DEM/UDS診断との差分、OEM領分、サプライヤ側の現実的な手札。
5. [docs/22_public_proxy_data_reset.md](docs/22_public_proxy_data_reset.md): 内部ケースにアクセスできない前提で、公開市場情報/Kaggle/公開CANデータで補える範囲を再定義。
6. [docs/27_s2e001_diagnostic_evidence_gap_check.md](docs/27_s2e001_diagnostic_evidence_gap_check.md): S2E001を既存DTC/freeze frameで説明できるか見るgap check。
7. [docs/28_s2e001_diagnostic_evidence_review_template.md](docs/28_s2e001_diagnostic_evidence_review_template.md): 内部DTC仕様を入れてProceed/Kill/Holdを判定するレビュー手順。
8. [docs/29_business_model_rebranch_after_s2e001_hold.md](docs/29_business_model_rebranch_after_s2e001_hold.md): S2E001 Hold後のビジネスモデル再分岐。
9. [docs/30_bmr001_market_pain_scenario_cards.md](docs/30_bmr001_market_pain_scenario_cards.md): BMR001の初期3枚scenario cardと商品化境界。最新では主商品ではなく前段材料。
10. [docs/31_bmr002_rfq_design_review_pack.md](docs/31_bmr002_rfq_design_review_pack.md): BMR001をRFQ/設計レビュー1ページへ変換したBMR002 sample。最新では主商品ではなく副産物。
11. [docs/23_public_proxy_demo_plan.md](docs/23_public_proxy_demo_plan.md): `Steering Context Risk Explorer` の代理デモ計画。
12. [docs/24_steering_context_risk_phase1.md](docs/24_steering_context_risk_phase1.md): TSVだけで作ったPhase 1静的分析結果。
13. [docs/25_low_speed_high_steering_proxy_phase2.md](docs/25_low_speed_high_steering_proxy_phase2.md): commaSteeringControlで作った低速・高操舵要求proxy抽出結果。
14. [docs/26_scenario_to_evidence_pack_direction.md](docs/26_scenario_to_evidence_pack_direction.md): Phase 2をEPSサプライヤ向けの評価・診断証跡設計へ変換する方向性。
15. [generated/bmr002_rfq_design_review_pack.html](generated/bmr002_rfq_design_review_pack.html): BMR002 Scenario Readiness Pageのブラウザ表示。
16. [generated/bmr001_market_pain_scenario_cards.html](generated/bmr001_market_pain_scenario_cards.html): BMR001 scenario cardのブラウザ表示。
17. [generated/business_model_rebranch_after_s2e001_hold.html](generated/business_model_rebranch_after_s2e001_hold.html): 再分岐の意思決定ビュー。
18. [generated/s2e001_diagnostic_evidence_review_template.html](generated/s2e001_diagnostic_evidence_review_template.html): S2E001 review templateの意思決定ビュー。
19. [generated/s2e001_diagnostic_evidence_gap_check.html](generated/s2e001_diagnostic_evidence_gap_check.html): S2E001 gap checkの意思決定ビュー。
20. [generated/eps_scenario_to_evidence_pack.html](generated/eps_scenario_to_evidence_pack.html): Scenario-to-Evidence Packの意思決定ビュー。
21. [generated/low_speed_high_steering_proxy.html](generated/low_speed_high_steering_proxy.html): Phase 2の代表window可視化。
22. [generated/steering_context_risk_explorer_phase1_ja.html](generated/steering_context_risk_explorer_phase1_ja.html): ブラウザで見られるPhase 1静的デモ日本語版。
23. [generated/steering_context_risk_explorer_phase1.html](generated/steering_context_risk_explorer_phase1.html): Phase 1静的デモ英語版。
24. [data/eps_public_market_pain_cases.tsv](data/eps_public_market_pain_cases.tsv): NHTSA/recall/investigationから抽出したdriver-visible EPS painケース。
25. [data/public_steering_dataset_inventory.tsv](data/public_steering_dataset_inventory.tsv): 公開steering / CAN / Kaggle dataset棚卸し。

## プロジェクトSkill

このRepoでは、事業仮説の探索と検証をCodex側に寄せるため、プロジェクトSkillを追加している。

- `future-need-interviewing`: 顧客の最初のニーズ、最悪の未来、最高の未来、欲しい感情から本当のニーズを掘る。
- `chain-of-verification`: 叩き台の結論を検証質問に分解し、エビデンスで潰してから修正版を出す。

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
  public_proxy_data_sources.tsv
  useful_items_for_steering_diagnostic_evidence.md
  ota_connected_health_market_signals.tsv
  target_feasibility_matrix.tsv
  eps_health_indicator_candidates.tsv

generated/
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
- 主仮説は `EPS Warranty / RCA Evidence Readiness Pack`
- BMR001/BMR002は主商品ではなく、Warranty / RCA evidence readinessの前段材料として扱う
- 次は `SCN001 low-speed high effort` で、NTF / returned-part RCA向けのEvidence Readiness Pack sampleを作る
- sampleには、market demand statement、case narrative、required product-side facts、existing diagnostic coverage check、confirmed / unconfirmed / do-not-infer table、customer quality / 8D D2-D4 attachment sample、Kill条件を入れる
- RCA/8D/顧客品質報告に転記できない場合、この方向はKillまたは大幅修正する
