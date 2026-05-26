# Steering Health Intelligence Notes

EPS / ステアリングシステムに、故障可能性・劣化兆候・予測用データ材料を持たせる事業仮説メモ。

現在の本命仮説は **EPS Health Intelligence Package**。

> EPSを、故障してからDTCを出す部品ではなく、劣化兆候と予測材料を持つhealth-aware subsystemにする。

追加の見せ方として、以下の表現が有効。

> EPS Health Intelligence Package は、既存EPS ECU信号からhealth indicatorを作る **virtual health sensor layer for EPS** である。

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
| 別表現 | virtual health sensor layer for EPS |
| 自分たちの立場 | EPS ECU / 制御 / 診断 / 内部信号を持つサプライヤ |
| Primary value target | EPS system / gear supplier |
| Required gatekeeper | Vehicle OEM |
| 主価値 | EPSをhealth-aware subsystemとして差別化する |
| 初期成果物 | EPS Health Indicator Set for Prognostic Readiness |
| 直近の検証軸 | 開発・耐久評価で使えるECU信号ベースのhealth / stress / control effort indicator |
| AI / 予測 | 初期は故障予測モデルではなく、予測に使える材料整備 |
| OTA / remote diagnostics | health indicatorを読むチャネルの一つ |
| 避ける主張 | 個車RUL断定、エンドユーザ故障通知、サプライヤ単独fleet監視 |

## Current Focus: Development Evaluation First

ここまでの議論で、返却品解析・保証解析を主語にしすぎると、開発目線では事後対応に寄りすぎることが分かった。

現在の仕切り直し仮説は以下。

> EPS ECU信号を使って、ギア / ラック設計、機械負荷、control effort、ストレス蓄積、耐久前後変化を開発・評価段階で比較できる指標を作る。

返却品解析や保証解析は残すが、初期価値の中心ではなく、後段用途とする。

### Core Question

> ギア / EPSシステム開発チームは、ギア / ラック設計や耐久条件を、ECU信号ベースのcontrol effort / stress / margin indicatorで比較できると嬉しいか？

### Revised Value Hierarchy

```text
L1: Development Evaluation Indicator
  ギア / ラック / 機械負荷をECU信号で評価する

L2: Durability Stress Indicator
  耐久試験・ベンチ試験でストレス蓄積を見る

L3: Health-ready EPS Package
  量産EPSに同じ指標を持たせる

L4: Service / Warranty / Market Quality Support
  量産後の診断・品質解析に使う

L5: Return-part Analysis Evidence
  返却品解析時の補助証跡
```

## Previous Focus: Gear Supplier Value Hypothesis

前段の仮説では、EPSサプライヤとして、ギアメーカー / EPSシステムメーカーにどう付加価値を出すかを整理した。

Vehicle OEM向けのVehicle Health Managementや市場fleet監視は重要だが、初期仮説としては遠い。まずは、ECU側が持つ内部信号・診断・制御情報を使って、ギア / ラック / 機械負荷に対する説明力を上げられるかを見る。

### Earlier Core Question

> ギアメーカーは、ECU側から見えるモータ電流・操舵トルク・操舵角速度・車速・温度・電圧などを使って、ギア / ラックの負荷履歴や説明力を高めたいか？

### Target Hypotheses

| ID | Hypothesis | Why it matters |
|---|---|---|
| G1 | ギアメーカーは、市場でのギア / ラック負荷・摩耗・使用履歴が見えずに困っている | ここがNoなら、health indicatorは技術的に面白いだけになる |
| G2 | EPS ECU内部信号から、ギア / ラック負荷やharsh usageのproxyを作れる | ECUサプライヤとして出せる価値の中心 |
| G3 | そのproxyは、開発評価・耐久評価・OEM説明・返却品解析に使える | 「ログ追加」ではなく、解析価値に変換する |
| G4 | ギアメーカーは、この機能をhealth-ready EPSとしてOEM向け差別化に使える | 商品価値・商談価値の仮説 |
| G5 | OEMは、エンドユーザ通知ではなく、解析・診断・将来VHM用のsubsystem health signalとしてなら受け入れる余地がある | 量産採用のゲート条件 |

### What to avoid

以下のような断定は避ける。

- ギア摩耗を検出します
- ラック劣化を予測します
- EPSが何km後に壊れるかを予測します
- OEM市場fleetをサプライヤ単独で監視します

より安全な表現:

- ギア / ラック負荷のproxyを提供します
- 高負荷操舵履歴を可視化します
- 摩擦増加の可能性を示すhealth indicatorを定義します
- 開発・耐久・診断で使えるcontrol effort / stress indicatorを提供します

## Recommended Read Order

まず読むなら、この順番が分かりやすい。

1. [docs/12_reset_hypothesis_development_evaluation.md](docs/12_reset_hypothesis_development_evaluation.md): 返却品解析中心から、開発・評価指標中心へ仕切り直した最新仮説。
2. [docs/09_feasibility_and_targeting.md](docs/09_feasibility_and_targeting.md): OTA中心ではなく、EPS自体の付加価値としてHealth Intelligenceを整理。
3. [docs/10_project_charter_eps_health_intelligence.md](docs/10_project_charter_eps_health_intelligence.md): EPS Health IntelligenceのProject Charter。
4. [docs/11_virtual_health_sensor_market.md](docs/11_virtual_health_sensor_market.md): `virtual health sensor layer for EPS` としての市場フレーミング。
5. [data/eps_health_indicator_candidates.tsv](data/eps_health_indicator_candidates.tsv): EPS内部信号から作れるhealth / degradation indicator候補。
6. [data/target_feasibility_matrix.tsv](data/target_feasibility_matrix.tsv): ターゲット別の実現性・魅力度・初期ピッチ。
7. [docs/08_ota_connected_health_market.md](docs/08_ota_connected_health_market.md): OTA / connected diagnosticsを、主商品ではなく読み出しチャネルとして整理。

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

Gear Supplier Value Hypothesis
  -> ECU側信号からギア / ラック負荷・使用履歴・説明材料を作れるかを検証する

Virtual Health Sensor Layer
  -> 既存EPS ECU信号から、ギア / ラック負荷proxy、ストレス履歴、劣化兆候を作る市場フレーミング

Development Evaluation First
  -> 返却品解析を主語にしすぎず、ギア / ラック設計・耐久評価・control effort比較を最初の検証軸にする
```

## Key Product Idea

`EPS Health Intelligence Package` は、以下を含む。

- EPS Health Indicator Set
- Development Evaluation Indicator
- Durability Stress Indicator
- Prognostic Data Package
- Health Summary Output
- Health Indicator Dictionary
- Use-case Specific Views
- Offline Validation Plan
- Virtual Health Sensor Layer for EPS

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
- 開発・耐久評価で使える指標であれば、量産後の市場データを待たずに価値検証できる
- OEMに対して「health-ready EPS」として差別化できる

ただし、量産採用や市場データ活用にはVehicle OEMの合意が必要。

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

data/
  business_model_research.tsv
  useful_items_for_steering_diagnostic_evidence.md
  ota_connected_health_market_signals.tsv
  target_feasibility_matrix.tsv
  eps_health_indicator_candidates.tsv
```

## Current Next Actions

- ギア / EPSシステム開発チーム視点のPain Hypothesisを整理する
- ギア / ラック / 機械負荷と利用可能信号のマトリクスを作る
- `data/development_evaluation_indicator_hypothesis.tsv` を作る
- `eps_health_indicator_candidates.tsv` を、指標式・保存条件・false positive要因まで拡張する
- HILS / bench / durability log / fault injectionで検証できる指標を選ぶ
- EPSメーカー / ギアメーカー向けの短いOEM-facing pitchを作る
- Project Charterを提案資料形式に変換する
