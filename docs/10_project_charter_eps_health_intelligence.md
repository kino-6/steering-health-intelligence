# 10. Project Charter: EPS Health Intelligence Package

## 1. Project Name

**EPS Health Intelligence Package**
EPSヘルス・インテリジェンス・パッケージ

## 2. Purpose

本プロジェクトは、EPS / ステアリングシステムにおいて、故障後にDTCを出すだけではなく、故障可能性・劣化兆候・予測用データ材料を提供できるhealth-aware subsystemを定義することを目的とする。

主な狙いは、EPSメーカー / ギアメーカーがOEMに対して、以下を提案できるようにすることである。

> このEPSは、Vehicle Health Management、Connected Diagnostics、保証解析、返却品解析、将来の故障予測に使えるhealth indicatorを持つ。

本提案は、個車ごとの故障時期やRULを断定するものではない。
また、OTA運用そのものを主商品にするものでもない。
さらに、OEMの市場fleetデータ、保証DB、苦情DB、車両クラウドを初期前提にしない。
それらは将来のOptional extensionとして扱う。

## 3. Background

EPSは通常、メンテナンスフリーで長期使用されることを前提に設計される。
そのため、従来は「正常に動くこと」と「故障時にDTCを出すこと」が中心だった。

一方で、車両のConnected化、Vehicle Health Management、ソフトウェア定義車両、保証費削減、市場品質監視の流れにより、EPSにも以下のような付加価値が求められ得る。

- EPSシステムの劣化兆候を把握したい
- ギア / ラック / モータ / センサ / ECUを含むシステム状態を見たい
- 故障予測に使えるデータ材料を市場から蓄積したい
- 返却品解析や保証解析に、使用履歴・負荷履歴を使いたい
- OEMのVehicle Health Managementに接続できるEPSとして差別化したい

この文脈では、単にログを増やすことは価値ではない。
価値があるのは、EPSが将来の予測・解析・品質改善に使えるhealth indicatorを持つことである。

本Repoの立場はECUメーカー起点であるため、まずはECU内部信号、診断設計、NVM証跡、HILS / bench / durability logで成立する最小パッケージを定義する。
OEMデータとの接続は価値を広げるが、初期成立条件にはしない。

## 4. Problem Statement

現状の課題は、EPSの故障が起きた後でなければ状態が見えにくいことである。

具体的には、以下の問題がある。

- DTC発生前の劣化兆候が残りにくい
- ギア摩擦、ラック負荷、センサずれ、熱負荷などが見えにくい
- EPSメーカー / ギアメーカーが市場使用中の負荷・兆候を直接把握しにくい
- 故障予測モデルを作ろうとしても、必要なデータ材料が揃っていない
- 市場返却品や保証解析で、使用履歴・ストレス履歴が不足する
- OEMに対して、EPSをVehicle Health Managementに接続する提案材料が弱い

つまり、いきなり故障予測を売る以前に、**故障予測や劣化解析に使えるEPS health data foundationが不足している**。

## 5. Goals

### Primary Goal

EPS内部信号から、故障可能性・劣化兆候・予測用データ材料として使えるhealth indicator setを定義する。

### Secondary Goals

- EPSメーカー / ギアメーカーがOEMに提案できるhealth-ready EPSの仕様を作る
- 故障予測そのものではなく、prognostic readinessを高めるデータパッケージを定義する
- 返却品解析、保証解析、市場品質解析、VHMに使える出力形式を整理する
- OTA / remote diagnostics / service / return-part analysisを読み出しチャネルとして使える形にする
- HILS / bench / durability log / fault injectionで、指標の妥当性を検証できる計画を作る
- OEMデータなしで成立するCoreと、OEMデータ接続で広がるOptional extensionを分離する

## 6. Non-Goals

本プロジェクトでは以下を目的としない。

- 個車ごとのRUL断定
- エンドユーザ向け故障通知
- EPS単体での故障予測精度保証
- OEM市場fleetのサプライヤ単独監視
- OEM cloud / 保証DB / 苦情DBを初期前提にした分析
- OTA platformそのものの構築
- リコール判断の自動化
- 保証判断の自動化
- 大量波形ログの常時送信
- ECU内部での重いAI推論

## 7. Proposed Solution

### 7.1 EPS Health Indicator Set

EPS内部信号から、劣化兆候や故障可能性の材料となる指標を定義する。

候補:

- assist current baseline deviation
- steering torque to motor current ratio
- current tracking warning count
- torque sensor redundancy delta
- torque sensor zero offset trend
- steering angle sensor redundancy delta
- thermal derating accumulation
- low voltage stress history
- assist limitation recurrence
- high-load low-speed event count
- end-stop / curb-hit-like event count
- transient abnormal recovery count

これらは故障断定ではなく、watch / check recommended / degradation tendency observed のようなengineering review向け指標として扱う。

### 7.2 Prognostic Data Package

将来の故障予測、cohort分析、市場品質解析に使える最小データセットを定義する。

候補:

- EPS variant
- software version
- calibration ID
- production lot / traceability ID
- cumulative operation proxy
- health indicator value
- event count
- last event condition
- normalization context
- related DTC
- validity condition

初期Coreでは、ECU内部またはECUサプライヤが責任を持てる項目に限定する。
vehicle model、地域、保証履歴、苦情情報、fleet trendなどは、OEM側データと接続するOptional extensionとして扱う。

### 7.3 Health Summary Output

大量ログではなく、解釈しやすいhealth summaryを出力する。

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

### 7.4 Health Indicator Dictionary

各指標について、OEM / EPSメーカー / ギアメーカー間で解釈できる辞書を作る。

項目:

- indicator name
- physical meaning
- related degradation / failure mode
- required signals
- unit
- update condition
- storage condition
- reset condition
- normalization condition
- false positive factors
- related DTC
- intended use
- interpretation caution

### 7.5 Use-case Specific Views

同じhealth indicatorを、利用先ごとに見せ方を変える。

| User | View |
|---|---|
| EPSメーカー / ギアメーカー | 劣化兆候、ロット差、設計改善材料 |
| OEM VHM team | 車両health signalとしてのEPS状態、Optional |
| OEM market quality | 車種 / 地域 / calibration別の兆候偏り、Optional |
| OEM service engineering | 追加診断要否 |
| Return-part analysis | 使用履歴・負荷履歴 |
| OTA / remote diagnostics | 読み出しチャネルの一つ、Optional |

## 8. Scope

### In Scope

- EPS内部信号に基づくhealth indicator候補定義
- 劣化・故障モードと利用可能信号のマッピング
- prognostic readiness datasetの定義
- health summary出力形式の定義
- health indicator dictionaryの作成
- 正常ばらつき、false positive要因、正規化条件の整理
- HILS / bench / durability log / fault injectionでのoffline検証計画
- OEM提案に向けたhealth-ready EPSの価値整理
- ECU-local CoreとOEM-connected Optional extensionの分離

### Out of Scope

- OEM cloud / VHM基盤の構築
- OEM市場データを前提にしたfleet analytics
- OTA platform構築
- 常時ストリーミング基盤
- 個車RULモデルの量産提供
- ユーザ通知UI
- 保証 / リコール判断の自動化
- EPS以外の全車両health統合

## 9. Target Customer and Stakeholders

### Primary Target

**EPS system / gear supplier**

理由:

- EPS品質、保証返却、システム劣化に直接関心がある
- ギア、ラック、モータ、センサ、ECUを含むEPS全体の付加価値として提案しやすい
- OEMに対してhealth-ready EPSとして差別化できる

### Required Gatekeeper

**Vehicle OEM**

理由:

- 量産採用、車両データ、connected diagnostics、VHM接続の権限を持つ
- EPS health signalを市場品質、保証、サービス、VHMに接続できる

ただし、Vehicle OEMは初期Coreの成立条件ではない。
OEMは量産採用、読み出しチャネル、将来のVHM接続におけるgatekeeperとして扱う。

### Secondary Users

- OEM market quality
- OEM service engineering
- OEM VHM / connected vehicle team
- return-part analysis team
- diagnostic engineering team
- OTA / remote diagnostics team

## 10. Business Value

このプロジェクトの価値は、EPSを単なる制御部品から、health-aware subsystemに引き上げることである。

期待価値:

- EPSメーカー / ギアメーカーのOEM向け差別化
- Vehicle Health Managementに接続可能なEPS付加価値
- 故障予測に必要なデータ材料の蓄積
- 市場返却品・保証解析での使用履歴確認
- 次期設計、診断仕様、キャリブレーション改善へのfeedback
- DTC発生前の劣化兆候やストレス履歴の可視化
- connected diagnostics / service / OTAを通じた低帯域health readout

Core value:

- ECUメーカーが自ECU内部信号と診断設計で提供できるhealth indicator
- EPSサプライヤがOEM提案に使えるhealth-ready EPS仕様
- HILS / bench / durability logで検証可能なprognostic readiness dataset

Optional value:

- OEM VHMやconnected diagnosticsへの接続
- OEM市場fleetでのcohort analysis
- 保証DB、苦情DB、地域情報との相関分析

## 11. Success Criteria

### Concept Success

- EPS health indicator候補が、主要な劣化・故障モードに紐づいている
- 各指標について、物理的意味、必要信号、解釈注意、false positive要因が説明できる
- EPSメーカー / ギアメーカーがOEM提案に使える価値表現になっている

### Technical Success

- 既存または低追加コストのECU内部信号から指標を算出できる
- HILS / bench / durability log / fault injectionで指標の変化を確認できる
- 正常ばらつきと異常傾向の初期baselineを作れる
- ECU負荷、NVM、通信量が許容範囲に収まる見込みがある

### Business Success

- OEMに対して、VHM / connected diagnostics / service / warrantyに接続できるEPS付加価値として説明できる
- EPSメーカー / ギアメーカーが、health-ready EPSを差別化要素として扱える
- OEMデータがなくてもCore packageとして説明できる
- 将来のconnected fleet dataやcohort analysisに接続できるデータ構造になっている

## 12. Risks

- 劣化兆候がタイヤ、路面、アライメント、温度、積載、運転癖に強く影響される
- ギア摩擦やラック負荷は直接観測できず、proxy推定になる
- EPS故障頻度が低く、教師あり故障予測モデルを作りにくい
- health indicatorが故障予測や保証判断と誤解される
- OEMが市場データをサプライヤへ返さない可能性がある
- OEMデータ接続を前提にしすぎると、ECUメーカー提案として実現性が下がる
- ECUリソース、NVM容量、通信量に制約がある
- EPSメーカー / ギアメーカーにとって、OEM提案価値が十分に見えない可能性がある

## 13. Mitigation

- 初期はRUL予測ではなく、health indicator / prognostic readinessとして位置づける
- 出力は `watch`、`check recommended`、`degradation tendency observed` などに留める
- 絶対値判定ではなく、同条件比較、車両内baseline、cohort比較を前提にする
- false positive factorsをindicator dictionaryに明記する
- HILS / bench / durability log / fault injectionでoffline検証から始める
- OTAは主商品ではなく、読み出しチャネルの一つとして扱う
- OEMデータ連携はOptional extensionとし、まずEPS側に持たせるECU-local data packageを定義する

## 14. Initial Work Plan

### Phase 0: Degradation Mode Mapping

目的:

- EPSで見たい劣化・故障候補を整理する

成果物:

- degradation mode x available signal matrix
- false positive factor list
- indicator feasibility score

### Phase 1: Offline Indicator Validation

目的:

- HILS、bench、durability log、fault injectionで候補指標が反応するか確認する

成果物:

- candidate indicator formulas
- normal variation baseline
- warning threshold draft
- missing signal list

### Phase 2: ECU-local Health Indicator Specification

目的:

- EPSメーカー / ギアメーカー向けの仕様としてまとめる

成果物:

- health indicator dictionary
- health summary format
- storage / reset policy
- diagnostic readout concept
- resource estimate
- OEM-data dependency classification

### Phase 3: EPS Supplier-facing Proposal

目的:

- EPSメーカー / ギアメーカーに対して、OEMへ持ち込めるhealth-ready EPS仕様として提案する

成果物:

- EPS supplier-facing pitch
- Core feature list
- Optional OEM-connected extension list
- validation plan

### Phase 4: OEM-facing Extension Proposal

目的:

- OEMに対して、VHM / connected diagnostics / service / warrantyに接続できるEPS付加価値として提案する

成果物:

- OEM-facing pitch
- use-case specific views
- data ownership model
- limited pilot plan

## 15. One-line Pitch

EPSを、故障してからDTCを出す部品ではなく、劣化兆候と予測材料を持つhealth-aware subsystemにする。

## 16. English Pitch

An EPS Health Intelligence Package that turns electric power steering from a fault-reporting component into a health-aware subsystem with degradation indicators and prognostic data materials for EPS suppliers and OEM vehicle health programs.
