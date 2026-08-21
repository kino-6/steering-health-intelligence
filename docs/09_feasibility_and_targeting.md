# 09. Feasibility and Targeting

## Core Correction

前回の整理は、OTAを前に出しすぎていた。

OTAは重要だが、本件の主役ではない。
主役は、EPSそのものの付加価値である。

> EPSに、故障可能性・劣化兆候・予測に使える材料を持たせる。

OTA、remote diagnostics、サービス入庫、返却品解析、OEM cloudは、そのhealth indicatorを読むチャネルや利用先にすぎない。

## ECU Supplier Boundary

本Repoの立場はECUメーカー起点である。
そのため、OEMが持つ市場fleetデータ、車両クラウド、保証DB、苦情DB、タイヤ / 路面 / 地域情報を前提にした提案は、初期本体に入れない。

初期提案は、以下に限定する。

> ECUメーカーが、自ECU内部信号・診断設計・NVM証跡・開発評価ログを使って提供できるEPS health intelligence。

OEMデータがあると価値は広がるが、それはOptional extensionとして扱う。

| Layer | Positioning | Data assumption |
|---|---|---|
| Core | ECUメーカーが責任を持って定義・実装できるhealth indicator | ECU内部信号、DTC、NVM、HILS / bench / durability log |
| Optional | OEMのVHM / connected diagnostics / fleet trendに接続する拡張 | OEM cloud、保証DB、苦情、地域、車両側データ |

この分離をしないと、提案が「OEMデータがないと成立しない企画」に見える。
本件の肝は、OEMデータがなくてもEPS自体の付加価値として成立する最小パッケージを作ることである。

## Revised Concept

現時点の本命コンセプト:

> EPS Health Intelligence Package

One-line:

> EPSシステム内部の電流、トルク、センサ冗長、操舵負荷、熱、電源、制御追従などから、故障可能性・劣化兆候・予測用データ材料を提供し、EPSメーカー / ギアメーカーがOEMに対して高付加価値EPSとして提案できるようにする。

このコンセプトでは、売るものはクラウドやOTA運用ではない。
売るものは、EPSに内蔵または付随するhealth intelligenceである。

## Target Customer Structure

### Primary Target: EPS system / gear supplier

最初のターゲットは、車両OEMではなく、EPSシステム / ギアメーカー側が自然である。

理由:

- EPSの品質・保証・返却品解析に直接関心がある
- ギア、ラック、モータ、センサ、ECUを含むシステム劣化を見たい
- ECU内部信号をEPSシステムの付加価値に変換できる
- OEMに対して「このEPSはhealth-readyである」と提案できる

この相手に刺さる価値:

- EPS故障予測に必要なデータ材料を持てる
- 摩擦増加、センサずれ、電流異常、熱負荷などの兆候を見える化できる
- 市場返却品や保証解析に使える
- 次期設計や診断設計改善に戻せる
- 将来OEMのVehicle Health Managementに接続できるEPSとして差別化できる

### Required Buyer / Gatekeeper: Vehicle OEM

量産車で使うには、最終的にOEMの合意が必要である。

OEMが見る価値:

- Vehicle Health Managementに載せられるsubsystem health signal
- 市場品質・保証・リコール前段の兆候把握
- Connected diagnostics / OTA / サービス診断で読めるEPS状態
- 安全重要部品の説明性向上

OEM側のハードル:

- connected dataの権限
- 車両クラウド / gateway / 診断仕様への統合
- 誤通知や過検知の責任
- 通信量、セキュリティ、プライバシー

ECUメーカー起点の提案では、OEMは初期から必須データ提供者ではなく、量産採用・読み出しチャネル・将来拡張のgatekeeperとして扱う。

### Secondary Target: OEM market quality / service engineering

この層は、health indicatorの利用部門である。
初期の仕様決定者というより、価値検証の相手として見る。

## What Is the EPS Added Value?

EPSにとっての付加価値は、以下の3層で整理できる。

### 1. Health-ready EPS

従来:

> EPSは正常に動く。故障したらDTCを出す。

提案:

> EPSは正常に動くだけでなく、内部負荷・劣化兆候・予測用材料を説明可能な形で保持する。

これは、EPSを単なる制御部品から、connected vehicle時代のhealth-aware subsystemに引き上げる提案である。

### 2. Prognostic data package

いきなりRULや故障時期を当てるのではない。
まず、故障予測に必要な材料をEPS側で整備する。

例:

- 同条件でのアシスト電流増加傾向
- 操舵トルクとモータ電流の関係変化
- 電流追従偏差の増加
- センサ冗長差の増加
- 熱制限頻度の増加
- 高負荷操舵イベントの累積
- end-stop / curb-hit-like eventの累積
- 低電圧ストレス履歴

### 3. Supplier differentiation

EPSメーカー / ギアメーカーは、OEMに対して以下を言える。

> サプライヤEPSは、Vehicle Health ManagementやConnected Diagnosticsに接続可能なhealth indicatorを持つ。

これは「安く作るEPS」ではなく、「市場品質・保証・将来VHMに使えるEPS」という差別化になる。

## Feasibility by Offering Level

| Level | Offering | Feasibility | Business value | Comment |
|---|---|---:|---:|---|
| L1 | Health evidence set | High | Medium | 既存DTC / Extended Data / NVM証跡の拡張。単体価値は弱いが土台になる |
| L2 | EPS health indicator set | Medium-High | High | 電流、トルク、センサ冗長、熱、電源、イベント累積から指標化する |
| L3 | ECU-local degradation trend package | Medium | High | ECU内baseline、NVM履歴、開発ログで成立する範囲に限定する |
| L4 | Connected fleet health analytics | Medium-Low | High | OEMデータ基盤が必要。EPSサプライヤ単独では難しい |
| L5 | Individual vehicle failure prediction / RUL | Low | Medium-High | 低頻度・教師データ不足・責任が重い。初期主張にしない |

## Recommended Beachhead

最初の攻め筋はこれ。

> EPS Health Indicator Set for Prognostic Readiness

狙い:

- 故障予測そのものを売らない
- 予測に使える材料と兆候指標をEPSの付加価値として売る
- EPSメーカー / ギアメーカーがOEMに提案できる仕様に落とす

## Candidate Health Indicators

### A. Assist current / load proxy

狙い:

- ギア摩擦、ラック負荷、機械抵抗、タイヤ/路面負荷の変化を間接的に見る

候補:

- 同一車速・操舵角速度・操舵トルク条件での必要モータ電流
- 目標電流と実電流の偏差
- steering torque to motor current ratio
- assist current baseline deviation
- high assist current event count

注意:

- タイヤ、路面、温度、アライメント、積載、運転癖の影響が大きい
- 単純な絶対値ではなく、同条件比較かcohort比較が必要

### B. Sensor health / drift

狙い:

- トルクセンサ、操舵角センサ、冗長系のずれや一時異常を見る

候補:

- torque sensor redundancy delta
- torque sensor zero offset trend
- steering angle sensor redundancy delta
- sensor plausibility warning count
- transient sensor recovery count

注意:

- DTC確定前の小さなずれをどう保存するかが鍵
- 断定故障ではなく、drift tendencyとして扱う

### C. Thermal stress

狙い:

- モータ、ECU、パワー素子の熱負荷やderating履歴を見る

候補:

- ECU temperature peak
- motor temperature peak
- thermal derating count
- thermal derating duration
- high-temperature operation accumulation

注意:

- 地域・季節・使用条件による正常差が大きい

### D. Power supply stress

狙い:

- 低電圧や電源不安定に起因するEPSイベントを切り分ける

候補:

- minimum supply voltage
- voltage dip count
- low-voltage assist limitation count
- power recovery event count

注意:

- EPS劣化というより車両側条件の場合が多い
- ただし、故障可能性の誤判定を防ぐ補正材料として重要

### E. Assist availability / limitation history

狙い:

- ユーザ症状や安全重要性に近い状態を捉える

候補:

- assist limitation count
- last assist limitation reason
- assist limitation duration
- fail-safe below-threshold event count
- transient abnormal recovery count

注意:

- 故障予測というより、health state summaryに向く

### F. Mechanical shock / harsh usage proxy

狙い:

- end-stop、縁石接触、据え切り、高負荷操舵など、機械系に効く使用履歴を見る

候補:

- end-stop event count
- high torque at low speed count
- high current at low speed count
- rapid steering reversal under high load
- suspected curb-hit-like event count

注意:

- センサだけで衝撃原因を断定しない
- EPSメーカー / ギアメーカーには有用な可能性が高い

## What Should Be Delivered?

単なるログではなく、以下のセットにする。

### 1. Health indicator dictionary

各指標について定義する。

- physical meaning
- related failure / degradation mode
- required signals
- update condition
- storage condition
- normalization condition
- interpretation caution
- false positive factors
- related DTC
- intended use

### 2. Health summary output

例:

```text
eps_health_state: watch
dominant_indicator: assist_current_baseline_deviation
secondary_indicator: thermal_derating_accumulation
degradation_hint: mechanical_load_or_friction_increase_possible
prediction_readiness: sufficient_for_cohort_trend
missing_context: tire_condition, road_surface, alignment
recommended_use: supplier_engineering_review
```

### 3. Prognostic readiness dataset

将来の故障予測モデルやcohort分析に使える形で、最小データセットを決める。

必要な軸:

- EPS variant
- software version
- calibration ID
- vehicle model
- production lot
- cumulative operation proxy
- indicator value
- event count
- last event condition
- normalization context

このdatasetは、初期段階ではECU内部で生成・保存できる項目に限定する。
vehicle model、地域、保証履歴、苦情情報などOEM側データは、将来結合する外部キーまたはOptional extensionとして扱う。

### 4. Use-case specific views

同じデータでも、利用先ごとに出力を変える。

| User | View |
|---|---|
| EPSメーカー / ギアメーカー | 劣化兆候、ロット差、設計改善材料 |
| OEM VHM team | vehicle health signalとしてのEPS状態、Optional |
| OEM market quality | 車種 / 地域 / calibration別の兆候偏り、Optional |
| Service engineering | 追加診断要否 |
| Return-part analysis | 使用履歴・負荷履歴 |
| OTA / remote diagnostics | 読み出しチャネルの一つ、Optional |

## Why This Is More Feasible Than Failure Prediction

故障予測は、以下が必要になる。

- 十分な故障件数
- 正確な故障ラベル
- 使用条件の正規化
- モデル検証
- 誤通知時の責任設計

EPSでは故障頻度が低いため、初期からここを狙うのは厳しい。

一方、health indicatorは以下で始められる。

- HILS / bench / durability log
- 故障注入
- 正常ばらつき評価
- 返却品解析データ
- サプライヤ内fleetや開発車両

つまり、量産connected fleetやOEM cloud dataがなくても、初期開発ができる。

## Practical Phase Plan

### Phase 0: Failure / degradation mode mapping

まず、EPSで見たい劣化・故障候補を決める。

候補:

- gear friction increase
- rack load increase
- bearing degradation
- motor current tracking degradation
- torque sensor drift
- steering angle sensor drift
- thermal stress accumulation
- power supply stress
- harsh usage accumulation

Output:

- degradation mode x available signal matrix
- indicator feasibility score
- false positive factor list

### Phase 1: Offline indicator validation

HILS、bench、durability log、fault injectionで、候補指標が分離できるかを見る。

Output:

- candidate indicator formulas
- normal variation baseline
- warning threshold draft
- missing signal list

### Phase 2: ECU-local Health Indicator Set specification

EPSメーカー / ギアメーカー向けに仕様化する。

Output:

- health indicator dictionary
- health summary format
- storage / reset policy
- DID / diagnostic readout concept
- resource estimate
- OEM-data dependency classification

### Phase 3: EPS supplier-facing proposal

EPS system / gear supplierに対して、OEMへ持ち込めるhealth-ready EPS仕様として提案する。

Output:

- EPS supplier-facing value proposition
- ECU-local core feature list
- optional OEM-connected extension list
- validation plan

### Phase 4: OEM-facing extension proposal

OEMに対して、VHM / Connected Diagnostics / service / warranty / OTAなどに接続できるEPS付加価値として提案する。

Output:

- OEM-facing value proposition
- use-case specific views
- data ownership model
- pilot plan

## Hard Parts

### 1. Mechanical degradation is not directly observable

ギア摩擦やラック負荷は直接測れないことが多い。
電流、トルク、操舵角速度、温度などからproxyとして推定する必要がある。

### 2. Normalization is the main technical barrier

同じ電流増加でも、原因は多数ある。

- タイヤ空気圧
- 路面
- アライメント
- 車速
- 温度
- 積載
- バッテリ状態
- 運転癖

そのため、絶対値で判定せず、同条件比較、車両内baseline比較、cohort比較を使う。

### 3. Label scarcity

故障件数が少ないため、教師あり予測モデルは難しい。
初期はanomaly / trend / stress accumulationを主にする。

### 4. Responsibility

出力は「故障します」ではなく、以下に留める。

- watch
- check recommended
- degradation tendency observed
- supplier review recommended
- insufficient context for prediction

### 5. Data ownership

市場データはOEMが持つ。
EPSメーカー / ギアメーカーは、health indicator定義と解釈ロジックを提供し、OEMから集計・匿名化されたfeedbackを受ける形が現実的。

ただし、これはOptional extensionである。
Core proposalは、OEMからの市場データfeedbackがなくても成立するECU-local packageとして定義する。

## Best Current Target Statement

現時点の攻め筋:

> EPS system / gear supplierをPrimary Targetとして、EPS内部信号から故障可能性・劣化兆候・予測用データ材料を出す `EPS Health Intelligence Package` を作る。

OTAは主価値ではなく、読み出しチャネルの一つに置く。
OEM cloud、保証DB、苦情DB、fleet trendはOptional extensionに置く。

Short version:

> EPSを、故障してからDTCを出す部品ではなく、劣化兆候と予測材料を持つhealth-aware subsystemにする。

## Source Notes

- EPS anomaly detection research identifies EPS failures and impending failures around sensors, actuators, stator insulation, bearings, and friction, and demonstrates anomaly detection on simulated drift and outlier cases.
- EPS design research has examined multiple degradations such as gear stiffness, gear friction, and rack displacement.
- Automotive electric drive monitoring literature points to supervision of electrical, thermal, magnetic, and mechanical states, incipient fault detection, and long-term degradation trending.
- EPS fault estimation research models unknown actuator / motor faults and external disturbances including mechanical friction and tire / road effects.

References:

- EPS anomaly detection research: https://pmc.ncbi.nlm.nih.gov/articles/PMC9699008/
- EPS multiple degradation design research: https://academic.oup.com/jcde/article/11/4/1/7693726
- Automotive electric drive monitoring review: https://www.mdpi.com/2079-9292/14/19/3950
- EPS rack-driving motor fault estimation: https://www.mdpi.com/2079-9292/11/24/4149
- EPS parameter and disturbance analysis: https://www.mdpi.com/1999-4893/12/3/57
