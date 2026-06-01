# Steering Health Intelligence Notes

EPS / ステアリングECUを起点に、ECU内部信号からhealth / stress / control-effort indicatorを作る事業仮説メモ。

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
```

## Current Position

現時点では、以下を中心仮説として扱う。ただし、`ECU内に証跡を残す` こと自体は既存診断の範囲にあるため、新規性として扱わない。

> EPS / ECUサプライヤが、過去の返却品・NTF・再現不能案件を棚卸しし、現行DTC / freeze frame / extended dataで足りなかった証跡を分類し、NVM制約内で追加すべき最小証跡セットと顧客品質報告向けの事実整理を作る。

重要な境界:

- OEMの市場fleetデータ、保証DB、苦情DB、車両クラウドを初期前提にしない
- OTAやremote diagnosticsは主商品ではなく、読み出しチャネルの一つ
- 個車RULやエンドユーザ故障通知は初期主張にしない
- まずはECUメーカーが責任を持てるCore packageを作る
- OEMデータ接続やfleet analyticsはOptional extensionに置く
- OEMに無手で聞きに行くのではなく、サプライヤ側の過去案件から不足証跡仮説を作ってから検証する
- `8D回答` という曖昧な言い方は避け、顧客品質報告、返却品解析報告、NTF調査メモ、D2 / D4向けの事実整理として扱う

## Current Focus

| 観点 | 現在の見立て |
|---|---|
| 最新ピボット | Existing Diagnostics / OEM Boundary Check |
| EPS向け軸 | EPS Warranty / NTF Case Backlog Analysis |
| 初期検証軸 | 過去20-50件の返却品・市場不具合・NTF・再現不能案件の棚卸し |
| 近い商品名 | EPS Diagnostic Evidence Design Review for Customer Quality |
| Primary target | EPS supplier warranty / customer quality / diagnostic engineering |
| 初期データ前提 | 既存DTC、freeze frame、extended data、返却品解析結果、社内品質台帳 |
| OEMデータ | Optional extension |
| AI / 予測 | 初期は故障予測モデルではなく、解析不能ケースの証跡不足分類 |
| 避ける主張 | 個車RUL断定、エンドユーザ故障通知、サプライヤ単独fleet監視、既存診断証跡の新規実装主張 |

## Recommended Read Order

まず読むなら、この順番が分かりやすい。

1. [docs/20_existing_diagnostics_oem_boundary.md](docs/20_existing_diagnostics_oem_boundary.md): 既存DEM/UDS診断との差分、OEM領分、サプライヤ側の現実的な手札。
2. [docs/19_market_research_eps_event_context.md](docs/19_market_research_eps_event_context.md): EPSサプライヤ視点で、Warranty / NTF / 返却品解析 / 顧客品質報告に刺す市場調査。
3. [docs/18_market_research_customer_pain.md](docs/18_market_research_customer_pain.md): Warranty / supplier quality市場の買い手痛み。
4. [docs/17_customer_value_reality_check.md](docs/17_customer_value_reality_check.md): 「誰が嬉しいのか」「外付けモニタと何が違うのか」の現実確認。
5. [docs/16_common_ecu_hardware_health_pivot.md](docs/16_common_ecu_hardware_health_pivot.md): EPS固有からECU共通hardware healthへ広げる将来ピボット。
6. [docs/13_business_scheme_reset.md](docs/13_business_scheme_reset.md): 誰が払うか、どの予算に刺すかを整理した事業スキーム再考。
7. [data/eps_ntf_case_review_template.tsv](data/eps_ntf_case_review_template.tsv): 内部一次調査用の返却品・NTFケース棚卸しテンプレート。
8. [data/eps_event_context_market_research.tsv](data/eps_event_context_market_research.tsv): EPS Event Context Memory向けの市場シグナル表。

## Business Model Feasibility Work

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

## Key Product Ideas

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

## Repository Structure

```text
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

data/
  business_model_research.tsv
  business_model_feasibility_100.tsv
  business_model_feasibility_sources.md
  best5_business_model_candidates.md
  demo_eps_health_summary_examples.tsv
  customer_pain_market_signals.tsv
  eps_event_context_market_research.tsv
  eps_ntf_case_review_template.tsv
  useful_items_for_steering_diagnostic_evidence.md
  ota_connected_health_market_signals.tsv
  target_feasibility_matrix.tsv
  eps_health_indicator_candidates.tsv
```

## Current Next Actions

- 過去20-50件のEPS返却品・市場不具合・NTF・再現不能案件を `data/eps_ntf_case_review_template.tsv` の観点で棚卸しする
- 現行DTC / freeze frame / extended dataで解析が進んだケースと止まったケースを分ける
- 足りない証跡を、外部市場調査の答えではなく、内部案件レビューから分類する
- OEMに聞く前に、サプライヤ側の不足証跡仮説とNVM制約内の最小追加案を作る
- `8D回答` ではなく、顧客品質報告・返却品解析報告・NTF調査メモ・D2/D4向け事実整理として表現する
