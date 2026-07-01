# 04. Project Charter: Steering Diagnostic Evidence Package

## 1. Project Name

**Steering Diagnostic Evidence Package**  
操舵ECU診断エビデンス・パッケージ

## 2. Purpose

本プロジェクトは、EPS / ステアリング制御系ECUにおいて、DTCだけでは不足する内部状態・一時異常・使用条件を診断エビデンスとして残し、OEM / Tier1間の市場不具合解析・原因候補分類・品質説明を支援することを目的とする。

本提案は、個車の故障予測やエンドユーザ向け警告を目的としない。  
また、ECU単体で市場車両群を監視するものでもない。

## 3. Background

EPS / ステアリング制御系ECUは、通常メンテナンスフリーを前提として設計される。  
そのため、エンドユーザ向けに故障予測警告を出すことは、メーカーにとって追加入庫、保証要求、誤警告リスクを増やす可能性がある。

一方で、操舵系は安全影響が大きい。  
市場で不具合が発生した場合、DTCだけでは原因切り分けが不十分なことがある。

特に以下のような情報は、発生時点で保存されていなければ後から再現・確認しにくい。

- 電源電圧状態
- 温度状態
- モータ電流追従状態
- センサ冗長差
- 補正量
- 制御モード
- 一時異常と復帰履歴
- DTC確定前の注意イベント

## 4. Problem Statement

現状の課題は、単にログが少ないことではない。

より本質的には、**市場不具合解析時に、DTCだけでは原因候補を十分に絞り込めないこと**である。

その結果、以下の問題が発生する。

- 再現困難不具合の原因調査に時間がかかる
- ECU起因か、車両側 / 電源側 / 環境側要因かの切り分けが難しい
- 返却品解析時に、使用中の一時異常履歴が分からない
- DTC発生前の兆候が残らない
- OEM / Tier1間の説明に時間がかかる
- 次期設計や診断仕様へのフィードバックが弱くなる

## 5. Goals

### Primary Goal

操舵ECUの市場不具合解析において、原因候補を早期に絞り込むための診断エビデンスを定義・提供する。

### Secondary Goals

- DTC発生時の原因切り分けに必要なExtended Dataを強化する
- DTC未満の一時異常を履歴化する
- 返却品解析時に有用なNVM証跡を残す
- ECU内部状態に基づく原因候補カテゴリを提示できるようにする
- 将来的にOEM側市場データと組み合わせやすいデータ辞書を整備する

## 6. Non-Goals

本プロジェクトでは以下を目的としない。

- 個車ごとのRUL予測
- エンドユーザ向け故障警告
- ECU内部での重いAI推論
- ECU単体での集団監視
- OEMクラウドや市場品質基盤の構築
- 保証判断の自動化
- リコール判断の自動化
- 通常メンテナンスの増加

## 7. Proposed Solution

### 7.1 Diagnostic Evidence Set

DTC発生時、注意イベント発生時、または返却品解析時に有用な診断エビデンスを定義する。

候補:

- 車速
- 電源電圧
- ECU温度
- モータ温度
- 操舵角
- 操舵トルク
- 目標モータ電流
- 実モータ電流
- 電流追従偏差
- トルクセンサ冗長差
- 操舵角センサ冗長差
- 制御モード
- アシスト制限状態
- フェイルセーフ未満の一時異常履歴
- ソフトウェアバージョン
- キャリブレーションID

### 7.2 DTC-below-threshold Event Counters

DTC確定には至らないが、解析時に有用な一時イベントをカウントする。

候補:

- 電流追従偏差が注意領域に入った回数
- センサ冗長差が注意領域に入った回数
- 低電圧状態で制御余裕が低下した回数
- 温度制限領域に入った回数
- 一時異常から正常復帰した回数
- アシスト制限が発生した回数

### 7.3 Suspected Cause Categories

診断エビデンスに基づき、原因候補カテゴリを提示する。

例:

- Power supply related
- Thermal limitation related
- Motor current tracking related
- Sensor redundancy related
- Transient event likely
- Persistent degradation tendency
- External vehicle-side factor suspected
- Additional data required

これは断定診断ではなく、**engineering review 用の原因候補分類**として扱う。

### 7.4 Data Dictionary

OEM / Tier1間で誤解なく使えるように、各データの意味を定義する。

項目:

- signal name
- physical meaning
- unit
- update condition
- storage condition
- reset condition
- valid / invalid condition
- related DTC
- suspected failure mode
- caution for interpretation

## 8. Scope

### In Scope

- 操舵ECU内部信号に基づく診断エビデンス定義
- DTC未満イベントカウンタ定義
- Extended Data / Freeze Frame 拡張案
- 返却品解析向けNVM証跡
- 原因候補カテゴリ分類
- データ辞書
- 既存ログ / HILS / 台上評価ログによる妥当性確認

### Out of Scope

- OEM市場全体のRisk Triage
- OTA後の市場監視そのもの
- ADAS可用性保証
- リコール対象の自動絞り込み
- 全車両の常時ログ取得
- エンドユーザ通知

## 9. Business Value

このプロジェクトの価値は、故障予測ではなく、**不具合解析の初動高速化と説明性向上**である。

期待価値:

- 市場不具合解析の初動を早める
- DTCだけでは分からない内部状態を補完する
- 再現困難不具合の原因候補を絞る
- 返却品解析時の証跡を強化する
- OEM / Tier1間の説明をしやすくする
- 次期DTC設計や診断仕様改善に活用する
- 将来的なOEM側市場傾向分析の材料になる

## 10. Success Criteria

- DTC発生時に、原因切り分けに有用な追加情報が取得できる
- 返却品解析時に、一時異常や使用条件の履歴を確認できる
- 既存DTCだけでは分からない原因候補を提示できる
- ECU負荷 / NVM使用量を許容範囲に収められる
- OEM / Tier1間で解釈可能なデータ辞書を作成できる
- HILS / 台上評価ログで、異常モードごとの指標有効性を確認できる

## 11. Risks

- OEMが追加診断エビデンスの価値を認めない可能性
- DTC未満カウンタが故障予測と誤解される可能性
- NVM容量やCPU負荷の制約
- 診断指標が正常ばらつきと区別しにくい可能性
- 原因候補分類が断定診断と誤解される可能性
- OEM側データと接続されず、活用範囲が限定される可能性

## 12. Mitigation

- 個車警告ではなく、解析用エビデンスとして位置づける
- 断定診断ではなく、suspected cause category として提示する
- 既存信号から低コストに算出できる指標に限定する
- DTC / Freeze Frame / Extended Data の自然な拡張として提案する
- まずはHILS / 台上 / 既存ログで有効性を確認する
- 将来拡張としてOEM側市場分析への接続可能性を示す

## 13. One-line Pitch

操舵ECUのDTCだけでは不足する内部状態・一時異常・使用条件を診断エビデンスとして残し、OEM / Tier1間の市場不具合解析と原因候補分類を高速化する。

## 14. English Pitch

A steering ECU diagnostic evidence package that preserves internal states, transient events, and operating conditions beyond DTCs to support faster field issue analysis and suspected-cause classification between OEMs and Tier1 suppliers.
