# Steering Health Intelligence Notes

EPS / ステアリングシステムに、故障可能性・劣化兆候・予測用データ材料を持たせる事業仮説メモ。

現在の本命仮説は **EPS Health Intelligence Package**。

> EPSを、故障してからDTCを出す部品ではなく、劣化兆候と予測材料を持つhealth-aware subsystemにする。

## Why This Repo Exists

当初の問いは、EPS / ステアリング制御系ECUの故障予測をVehicle Health Management市場で事業化できるか、だった。

検討の結果、以下の考えに寄っている。

- 個車ごとのEPS故障時期やRULを直接売るのは難しい
- エンドユーザ向け「壊れそうです」通知は、誤通知・不安・責任が重い
- フリート向けEPS単体予兆保全は、故障頻度が低く主価値になりにくい
- 「ログを増やす」だけでは付加価値にならない
- OTAやremote diagnosticsは重要だが、主商品ではなく読み出しチャネルの一つ
- まずはEPS内部信号から、劣化兆候・異常傾向・予測用データ材料を作るのが現実的

## Current Position

現時点の整理:

| 観点 | 現在の見立て |
|---|---|
| 主コンセプト | EPS Health Intelligence Package |
| Primary target | EPS system / gear supplier |
| Required gatekeeper | Vehicle OEM |
| 主価値 | EPSをhealth-aware subsystemとして差別化する |
| 初期成果物 | EPS Health Indicator Set for Prognostic Readiness |
| 初期データ前提 | ECU内部信号、DTC、NVM、HILS / bench / durability log |
| OEMデータ | Optional extension |
| AI / 予測 | 初期は故障予測モデルではなく、予測に使える材料整備 |
| OTA / remote diagnostics | health indicatorを読むチャネルの一つ |
| 避ける主張 | 個車RUL断定、エンドユーザ故障通知、サプライヤ単独fleet監視 |

## Recommended Read Order

まず読むなら、この順番が分かりやすい。

1. [docs/09_feasibility_and_targeting.md](docs/09_feasibility_and_targeting.md): 現在の軸。OTA中心ではなく、EPS自体の付加価値としてHealth Intelligenceを整理。
2. [docs/10_project_charter_eps_health_intelligence.md](docs/10_project_charter_eps_health_intelligence.md): 現在の本命案をProject Charter化したもの。
3. [data/eps_health_indicator_candidates.tsv](data/eps_health_indicator_candidates.tsv): EPS内部信号から作れるhealth / degradation indicator候補。
4. [data/target_feasibility_matrix.tsv](data/target_feasibility_matrix.tsv): ターゲット別の実現性・魅力度・初期ピッチ。
5. [docs/08_ota_connected_health_market.md](docs/08_ota_connected_health_market.md): OTA / connected diagnosticsを、主商品ではなく読み出しチャネルとして整理。

## Concept Evolution

このRepoでは、仮説が以下のように変化している。

```text
ECU故障予測
  -> EPS単体の故障予測は頻度・責任・データ面で弱い

Diagnostic Evidence Package
  -> 市場不具合解析には効くが、単体では「ログ追加」に見えやすい

Field Issue Triage Evidence
  -> NTF削減や責任分界には効くが、事後解析中心で付加価値がやや弱い

OTA / Connected Health
  -> 読み出し機会としては有効だが、OTAが主価値ではない

EPS Health Intelligence Package
  -> EPS自体をhealth-aware subsystemとして差別化する
```

## Key Product Idea

`EPS Health Intelligence Package` は、以下を含む。

- EPS Health Indicator Set
- Prognostic Data Package
- Health Summary Output
- Health Indicator Dictionary
- Use-case Specific Views
- Offline Validation Plan

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

## Business Hypothesis

最初の買い手は、車両OEMそのものより **EPS system / gear supplier** が自然。

理由:

- EPS品質、保証返却、システム劣化に直接関心がある
- ギア、ラック、モータ、センサ、ECUを含むEPS全体の付加価値として提案しやすい
- OEMに対して「health-ready EPS」として差別化できる

ただし、量産採用や市場データ活用にはVehicle OEMの合意が必要。

ECUメーカー起点の提案としては、OEMの市場fleetデータ、保証DB、苦情DB、車両クラウドを初期前提にしない。
まずはECU内部信号と開発評価ログで成立するCore packageを作り、OEMデータ接続はOptional extensionに置く。

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

data/
  business_model_research.tsv
  useful_items_for_steering_diagnostic_evidence.md
  ota_connected_health_market_signals.tsv
  target_feasibility_matrix.tsv
  eps_health_indicator_candidates.tsv
```

## Current Next Actions

- EPSの劣化・故障モードと利用可能信号のマトリクスを作る
- `eps_health_indicator_candidates.tsv` を、指標式・保存条件・false positive要因まで拡張する
- HILS / bench / durability log / fault injectionで検証できる指標を選ぶ
- EPSメーカー / ギアメーカー向けの短いOEM-facing pitchを作る
- Project Charterを提案資料形式に変換する
