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
```

## Current Position

現時点では、以下を中心仮説として扱う。

> ECUメーカーが、自ECU内部信号・診断設計・NVM・開発評価ログから、開発評価・耐久評価・診断・将来VHMに使えるhealth / stress evidenceを作る。

重要な境界:

- OEMの市場fleetデータ、保証DB、苦情DB、車両クラウドを初期前提にしない
- OTAやremote diagnosticsは主商品ではなく、読み出しチャネルの一つ
- 個車RULやエンドユーザ故障通知は初期主張にしない
- まずはECUメーカーが責任を持てるCore packageを作る
- OEMデータ接続やfleet analyticsはOptional extensionに置く

## Current Focus

| 観点 | 現在の見立て |
|---|---|
| 最新ピボット | Common ECU Hardware Health Layer |
| EPS向け軸 | EPS Health Intelligence Package |
| 初期検証軸 | Development / bench / durability evaluation |
| 近い商品名 | ECU Power Health Evidence Package |
| Primary target | EPS system / gear supplier, ECU development / validation teams |
| 初期データ前提 | ECU内部信号、DTC、NVM、HILS / bench / durability log |
| OEMデータ | Optional extension |
| AI / 予測 | 初期は故障予測モデルではなく、予測に使える材料整備 |
| 避ける主張 | 個車RUL断定、エンドユーザ故障通知、サプライヤ単独fleet監視 |

## Recommended Read Order

まず読むなら、この順番が分かりやすい。

1. [docs/16_common_ecu_hardware_health_pivot.md](docs/16_common_ecu_hardware_health_pivot.md): EPS固有からECU共通hardware healthへ広げる最新ピボット。
2. [docs/13_business_scheme_reset.md](docs/13_business_scheme_reset.md): 誰が払うか、どの予算に刺すかを整理した事業スキーム再考。
3. [docs/12_reset_hypothesis_development_evaluation.md](docs/12_reset_hypothesis_development_evaluation.md): 返却品解析ではなく、開発・耐久評価を初期価値に置くリセット仮説。
4. [docs/09_feasibility_and_targeting.md](docs/09_feasibility_and_targeting.md): EPS Health Intelligenceの実現性とターゲット整理。
5. [docs/10_project_charter_eps_health_intelligence.md](docs/10_project_charter_eps_health_intelligence.md): EPS Health IntelligenceのProject Charter。
6. [data/best5_business_model_candidates.md](data/best5_business_model_candidates.md): 100案から選んだBest5と推奨初手。
7. [data/business_model_feasibility_100.tsv](data/business_model_feasibility_100.tsv): ビジネスモデル成立性を100案で整理した表。
8. [data/eps_health_indicator_candidates.tsv](data/eps_health_indicator_candidates.tsv): EPS内部信号から作れるhealth / degradation indicator候補。

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

EPSを、故障してからDTCを出す部品ではなく、劣化兆候と予測材料を持つhealth-aware subsystemにする。

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

### Common ECU Hardware Health Layer

EPS固有メカ指標に閉じず、電源、温度、リップル、brownout、reset、capacitor stressなど、ECU横断で使えるhardware health evidenceへ広げる。

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

data/
  business_model_research.tsv
  business_model_feasibility_100.tsv
  business_model_feasibility_sources.md
  best5_business_model_candidates.md
  demo_eps_health_summary_examples.tsv
  useful_items_for_steering_diagnostic_evidence.md
  ota_connected_health_market_signals.tsv
  target_feasibility_matrix.tsv
  eps_health_indicator_candidates.tsv
```

## Current Next Actions

- 100案のBest5を、最新のCommon ECU Hardware Healthピボットに照らして再評価する
- EPS向け候補とECU共通hardware health候補を分けた2層の事業案にする
- `data/development_evaluation_indicator_hypothesis.tsv` を作る
- `eps_health_indicator_candidates.tsv` を、指標式・保存条件・false positive要因まで拡張する
- HILS / bench / durability log / fault injectionで検証できる指標を選ぶ
