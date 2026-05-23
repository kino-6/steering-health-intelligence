# Useful Items for Steering Diagnostic Evidence

`business_model_research.tsv` の100件から、現時点の本Repoの本命案である `Steering Diagnostic Evidence Package` に有効そうな知識を抽出した。

## 1. Positioning

本Repoで強く使うべき位置づけ:

- 売るものは「個車の故障予測」ではなく「市場不具合解析を早める診断エビデンス」。
- 価値は、発生率の高い保全費削減ではなく、低頻度だが重大な操舵系問題の説明性、切り分け速度、再現困難不具合の調査効率。
- 顧客は、エンドユーザやフリート運行者より、OEMの市場品質、診断設計、サービスエンジニアリング、EPSシステム担当、Tier1品質解析チーム。
- サプライヤ単独で市場全体を監視するとは言わない。OEM側データと接続できる下位証跡を提供する。

## 2. Product Items

優先して成果物化するアイテム:

| Item | Why useful |
|---|---|
| Extended Data / Freeze Frame拡張表 | 既存診断仕様の自然な拡張として提案しやすい |
| DTC-below-threshold event counters | 再現困難、No Trouble Found、一時異常の解析に効く |
| Return-part NVM evidence map | 返却品から使用中の一時状態を復元できる |
| Suspected cause categories | 「More Logs」ではなく、調査初動を早める価値に変換できる |
| Diagnostic data dictionary | OEM / Tier1間の誤解を減らし、データを使える状態にする |
| Investigation flow by symptom | 操舵違和感、EPS警告、アシスト制限などの調査手順を標準化できる |
| Resource budget table | ECU実装で問題になるCPU、RAM、NVM、通信量の議論に入れる |
| Offline evidence analyzer prototype | 小さなCLIやNotebookで、ログ追加以上の価値を実演できる |

## 3. Candidate Evidence Signals

初期パッケージの候補:

- 車速
- 電源電圧、最低電圧、電圧低下回数
- ECU温度、モータ温度
- 操舵角、操舵角センサ冗長差
- 操舵トルク、トルクセンサ冗長差
- 目標モータ電流、実モータ電流、電流追従偏差ピーク
- 制御モード
- アシスト制限状態、アシスト制限回数、直近発生条件
- DTC未満の注意イベント回数
- 一時異常から正常復帰した回数
- ソフトウェアバージョン
- キャリブレーションID
- ECU生産ロットまたはトレーサビリティID

## 4. Event Counters

優先度が高いDTC未満イベント:

- current tracking deviation warning count
- torque sensor redundancy warning count
- steering angle sensor redundancy warning count
- low voltage assist limitation count
- thermal derating count
- transient abnormal recovery count
- assist limitation count
- latest event record index or ring-buffer summary

## 5. Cause Categories

断定診断ではなく、engineering review向けの仮説カテゴリとして扱う。

- Power supply related
- Thermal limitation related
- Motor current tracking related
- Sensor redundancy related
- Assist limitation context
- Transient event likely
- Persistent degradation tendency
- External vehicle-side factor suspected
- Software / calibration cohort check recommended
- Additional data required

## 6. Data Dictionary Fields

各信号に最低限持たせる項目:

- signal name
- physical meaning
- unit
- sampling / update condition
- storage condition
- reset condition
- valid condition
- invalid condition
- related DTC
- related symptom
- suspected cause relevance
- resource cost
- interpretation caution
- recommended next check

## 7. Business Model Implications

収益化の現実路線:

- 初期はSaaSではなく、診断仕様拡張のNRE、部品単価上乗せ、または車種開発パッケージとして扱う。
- 将来、OEM側データ基盤と接続された場合のみ、市場品質analyticsやrisk triageへ拡張する。
- 「AI」を前面に出すより、原因候補分類、証跡サマリ、不足データ提示を小さく実装する方が通りやすい。
- 成果指標は故障予測精度ではなく、原因候補の絞り込み、解析初動時間、NTF削減、DTC説明力、返却品解析の成功率に置く。

## 8. Suggested Next Data Assets

次に `data/` へ追加するとよいもの:

- `candidate_evidence_signals.tsv`
- `dtc_below_threshold_events.tsv`
- `suspected_cause_categories.tsv`
- `data_dictionary_template.tsv`
- `symptom_investigation_flows.md`
- `offline_validation_plan.md`

## 9. Best Current Proposal Sentence

操舵ECUのDTCだけでは不足する内部状態、一時異常、使用条件を診断エビデンスとして標準化し、OEM / Tier1の市場不具合解析における原因候補分類、返却品解析、品質説明を早める。

## 10. Market Need Reframe

ここまでの議論で、重要な前提を更新する。

市場は「ログを増やしてほしい」とは思っていない。
市場が欲しいのは、不具合、保証、稼働停止、責任分界に関する意思決定を早くすることである。

したがって、Extended Data、Freeze Frame、NVM証跡、DTC未満イベントカウンタは、それ自体では付加価値になりにくい。
価値が出るのは、それらが以下の利用先に接続された場合である。

- No Trouble Found / 再現なし返却を減らす
- 原因不明の市場不具合を初動分類する
- OEM / Tier1間の責任分界を早める
- 保証解析や返却品解析の工数を下げる
- 品質会議で説明可能なEvidence Summaryを作る
- DTCを次の調査アクションに変える

この観点では、`Steering Diagnostic Evidence Package` よりも、以下の方が市場要求に近い。

- `Steering Field Issue Triage Package`
- `EPS Field Issue Triage Evidence`
- `EPS No-Trouble-Found Reduction Package`
- `Steering Warranty Investigation Support`

現時点の一番強い表現:

> EPS市場不具合の再現なし・原因不明・責任分界不明を減らすための Field Issue Triage Evidence。

短く言うなら:

> DTCを、原因候補と次アクションに変える。
