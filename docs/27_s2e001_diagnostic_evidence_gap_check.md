# S2E001 Diagnostic Evidence Gap Check

## 結論

`S2E001 low_speed_high_effort` は、まだKillではない。

ただし、追加証跡を入れる価値があるかは、現行DTC / freeze frame / extended dataでどこまで説明できるか次第。

公開データと既存Repo情報だけでの仮判定は以下。

| 判定 | 内容 |
|---|---|
| 既存で足りそう | 車速、操舵角、電圧、温度、occurrence counter / operation cycle |
| 要確認 | assist command、motor current、current tracking error、current limit / derating state、assist mode transition |
| 追加候補になり得る | DTC発火前1-3秒の最小summary、assist demand-to-output margin、current limit/derating snapshot |
| この時点で避ける | 波形保存、劣化兆候、RUL、driver向け故障予告 |

つまり続きは、`低速高操舵イベントを検出する` ではなく、

> この文脈でassist余裕が詰まった場合、現行診断snapshotで説明できるか。

を潰すこと。

## 生成物

| File | 内容 |
|---|---|
| `data/s2e001_diagnostic_evidence_gap_check.tsv` | S2E001の証跡要求、既存診断との重なり、仮判定、内部確認項目 |
| `generated/s2e001_diagnostic_evidence_gap_check.html` | 意思決定用HTMLビュー |

## S2E001の入力条件

Market pain:

- 低速で操舵力が重い
- assist loss時に手動操舵は可能だが負荷が高い
- warning / MILが出る場合もある

Public proxy:

- `LSHSD-001`: 7.2 m/s前後、`abs(steerFiltered)=1.0`、最大操舵角約39 deg
- `LSHSD-003`: 5.4 m/s前後、`abs(steerFiltered)` 最大約0.57、最大操舵角約22 deg
- `LSHSD-005`: 7.2 m/s前後、`abs(steerFiltered)` 最大約0.94、最大操舵角約24 deg

これらは正常走行proxyであり、assist lossではない。
評価シナリオの入力形状として使う。

## Gap Check

### 既存診断で足りそうなもの

以下は一般にfreeze frame / extended data / DEM / UDSの範囲に入りやすい。

- vehicle speed
- steering angle
- battery voltage
- ECU / motor temperature
- occurrence counter
- operation cycle / ignition cycle

これらが対象EPSでも既に残るなら、追加価値として主張しない。

### 足りない可能性があるもの

今回の本丸はここ。

| 候補 | なぜ必要か | 追加価値の条件 |
|---|---|---|
| assist demand-to-output margin | 高操舵要求に対してassistを出せたかを見る | assist command / actual current / current tracking errorが現行snapshotに無い |
| current limit / derating snapshot | assistが重い理由が上限到達か故障かを切り分ける | current limit / derating stateがDTCに残らない |
| pre-DTC 1-3 sec scalar summary | DTC発火瞬間だけでは直前の制御努力が見えない | 既存event memoryが直前summaryを持たない |
| assist mode transition edge | assist停止/復帰のdriver painを説明する | enable/disable edgeやlast state reasonが残らない |
| torque sensor residual summary | センサ/コネクタ由来の一過性を切り分ける | raw redundancy/residualが現行extended dataに無い |

## 現時点の推奨

追加候補は3つまでに絞る。

### Candidate A: Demand-to-output margin snapshot

保存する候補:

- peak assist command
- actual motor current at peak demand
- current tracking error max
- current limit active flag

狙い:

> 「操舵要求は高かったが、EPSがどこまでassistを出せていたか」を説明する。

Kill条件:

- 現行extended dataに同等の値がある
- motor currentやassist commandを顧客品質報告で使えない

### Candidate B: Limit / derating reason snapshot

保存する候補:

- current limit flag
- thermal derating level
- voltage limitation flag
- assist limitation reason

狙い:

> 「重くなった理由が電源/熱/電流上限/制御状態のどれに近いか」を断定せずに整理する。

Kill条件:

- 既存DTCが十分にこの理由を表現している
- reasonが内部実装依存すぎてOEM説明に出せない

### Candidate C: Pre-event scalar summary

保存する候補:

- last 1-3 sec max steering angle
- last 1-3 sec max assist command
- last 1-3 sec min voltage
- last 1-3 sec current limit count
- last assist mode transition reason

波形保存ではなく、scalar summaryに限定する。

狙い:

> DTC発火瞬間だけではなく、直前に低速高操舵要求が続いていたかを説明する。

Kill条件:

- NVM容量/書換頻度に収まらない
- 現行event memoryが同等のsummaryを持つ

## Chain-of-Verification

| 検証質問 | 確認結果 | Confidence | 修正 |
|---|---|---:|---|
| 公開データだけで既存診断の不足を断定できるか | できない。現行DTC / freeze frame / extended data仕様が必要。 | High | 不足断定ではなくgap check仮表にした |
| 低速高操舵windowは故障を示すか | 示さない。正常走行proxy。 | High | 評価入力形状として扱う |
| 追加証跡候補は既存診断の言い換えではないか | 車速/操舵角/電圧/温度/カウンタは言い換えになりやすい。 | High | それらは追加候補から下げた |
| 何が残ればサプライヤ価値になり得るか | assist demand-to-output, limit/derating reason, pre-event scalar summaryは既存に無ければ説明力を増やす可能性。 | Medium | 追加候補を3つに限定 |
| ここで商品化判断できるか | できない。内部仕様と返却品/NTFケースで確認が必要。 | High | 判定をConditional Proceedにした |

## 判定

S2E001は **Conditional Proceed**。

次に必要なのは、新しい解析ではなく内部仕様との突合。

必要資料:

1. assist loss / assist limited / torque sensor / voltage / thermal系DTC一覧
2. 各DTCのfreeze frame項目
3. 各DTCのextended data項目
4. 返却品解析readerで読めるDID一覧
5. NVMに追加保存できるbyte数、保存件数、書換頻度制約

この5つが揃えば、S2E001は以下のどちらかに落ちる。

- **Kill**: 既存診断で十分
- **Proceed**: Candidate A/B/Cのうち1-3個だけを最小追加証跡として提案

## 次に作るもの

次は `S2E001 Diagnostic Evidence Review Template`。

入力:

- DTC名
- 現行freeze frame項目
- 現行extended data項目
- 返却品解析readerで読める項目
- S2E001 Candidate A/B/Cとの対応

出力:

- 既存で十分
- 追加候補あり
- OEMデータが必要
- 価値なし/Kill
