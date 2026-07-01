# Public Data Validation: SCN001 Evidence Readiness

## 結論

Kaggleなどを含む公開データで、`EPS Warranty / RCA Evidence Readiness Pack` の一部は検証できる。

ただし、検証できるのは以下まで。

> 市場痛みと正常走行proxyを使い、RCA/8D/顧客品質説明で必要になるproduct-side factsの骨格を作れる。

検証できないのは以下。

> 対象EPSの既存DTC / freeze frame / extended dataが足りるか、assist currentやlimit stateが残るか、返却品readerで読めるか、実際のroot causeは何か。

したがって、公開データPoCの価値は `故障を当てること` ではない。

価値は、

> 返却品/NTF/RCA/8Dで何を確認すべきかを、公開データから事前に構造化できること。

## 使った公開データ

| Source | 用途 | 判断 |
|---|---|---|
| commaai `commaSteeringControl` | 低速高操舵の正常走行proxy window抽出 | 主データとして利用可能 |
| Kaggle OBD-II & CAN-Based Driving Behavior Dataset | 一般CAN/OBD文脈の候補 | Kaggle取得制約とEPS固有信号不足のため今回は補助候補 |
| Kaggle PVS Passive Vehicular Sensors Dataset | GPS/IMU/路面文脈候補 | EPS/RCA直接用途は限定的 |
| Zenodo Vehicle CAN bus data with GPS | steering angle / wheel speedを持つ二次proxy候補 | 将来の外部確認用 |
| NHTSA EPS public cases | 市場痛み、driver-visible symptom、case narrative | 市場需要/症状文脈に利用 |

Webで確認できた範囲では、`commaSteeringControl` には `vEgo`、`steeringAngleDeg`、`steeringPressed`、`steerFiltered`、`latActive`、`latAccelDesired`、`epsFwVersion` などがある。
Repo内では `CHRYSLER_PACIFICA_2018` について、2,091,708 samples、低速samples 87,334、高需要samples 8,412、candidate windows 231を抽出済み。

## SCN001でできたこと

対象scenario:

> `SCN001 low_speed_high_effort`

市場需要:

> 低速時に操舵が重くなったというdriver-visible symptomを、返却品/NTF/RCA/8Dで説明したい。

公開case:

- NHTSA MKT003 / MKT004: low-speedでincreased steering effortが問題化
- MKT009: warning / MILつきloss assist、低速時リスク

公開proxy:

- LSHSD-001: mean speed 7.21 m/s、max steering angle 39.19 deg、steerFiltered 1.0
- LSHSD-003: mean speed 5.43 m/s、mean steering angle 19.41 deg
- LSHSD-005: mean speed 7.23 m/s、max steering angle 24.00 deg

この結果、RCA/8Dで最低限必要なfactsを以下のように整理できる。

| Fact group | 公開データで確認できるか | 判断 |
|---|---|---|
| 車速 | Yes | 低速文脈はproxy化できる |
| 操舵角 / 操舵要求proxy | Yes | 高操舵文脈はproxy化できる |
| driver override / latActive | Yes | 正常走行proxyとして境界を説明できる |
| assist command vs motor current | No | 内部診断仕様が必要 |
| current limit / derating reason | No | 内部診断仕様が必要 |
| voltage / thermal state | No | 内部診断仕様が必要 |
| torque sensor residual / connector context | No | 内部診断仕様が必要 |
| DTC / warning timing | No | 対象EPSのfreeze frame/extended dataが必要 |
| supplier reader / DID | No | 返却品解析フロー確認が必要 |

## 1ページsample

### Market demand statement

NTF、返却品解析、保証claim、8Dでは、部品単体で再現しない場合でも、車両上でどのような低速高操舵文脈が発生していたかを説明する必要がある。

### Case narrative

公開NHTSA caseでは、低速時に操舵が重くなるdriver-visible painが繰り返し示されている。
公開走行データでは、5-8 m/s程度、操舵角15-40 deg程度の低速高操舵windowを抽出できる。
これは故障再現ではないが、RCA/8Dで確認すべき事実項目を定義するには使える。

### Required product-side facts

| Required fact | Why |
|---|---|
| vehicle speed | 低速時のmanual effort文脈を説明する |
| steering angle / demand | 高操舵文脈を説明する |
| assist command vs actual current | 要求assistに対して実assistが出たかを見る |
| limit / derating reason | 重くなった理由を制御制限、熱、電源、故障検知に分ける |
| voltage / thermal state | 電源/熱起因を切り分ける |
| torque sensor residual | センサ/コネクタ文脈を切り分ける |
| DTC/warning timing | driver-visible symptomと診断発生を対応づける |
| readout path | 返却品解析で実際に読めるかを確認する |

### Confirmed / unconfirmed / do-not-infer

| Category | 内容 |
|---|---|
| Confirmed | 公開市場痛みとしてlow-speed increased effortが存在する。公開走行データで低速高操舵proxy windowは作れる。 |
| Unconfirmed | 対象EPSのDTC/freeze frame/extended dataが必要factsを保持するか。サプライヤ返却品readerで読めるか。 |
| Do not infer | 故障予測できる、劣化兆候がある、既存診断が不足している、root causeが分かる、保証費が下がる。 |

### Customer quality / 8D D2-D4 attachment sample

Observed facts:

- Public symptom family: low-speed increased steering effort / loss of expected assist.
- Representative public driving context: 5-8 m/s, elevated steering angle/demand, no driver override in selected proxy windows.
- Current evidence boundary: public data does not include EPS DTC, motor current, limit state, voltage, thermal state, or returned-part reader data.

Need to confirm:

- Does the target EPS freeze frame retain vehicle speed and steering angle for assist-related DTCs?
- Does extended data retain assist state, limit/derating reason, voltage, thermal state, and torque sensor plausibility?
- Can supplier returned-part analysis read the relevant DIDs without OEM-only tooling?

Do not conclude:

- Root cause
- Defect frequency
- Predictive detection
- Existing diagnostic insufficiency

## 検証結果

公開データでPoCは成立する。

ただし成立するPoCは、

> 故障検知PoCではなく、Evidence Readiness Packの骨格PoC。

この方向で次に作るべきものは、追加データ分析ではなく、`SCN001` の1ページ成果物である。

## 次の内部確認

公開データ検証後に必要な確認:

1. assist-related DTCのfreeze frame項目
2. extended dataにassist state / limit reason / voltage / thermal / torque sensor residualがあるか
3. 返却品解析で読めるDID / reader / ODX
4. 8Dまたは顧客品質報告テンプレートに転記できるか
5. 既存診断で十分なら追加証跡案はKill

## Chain-of-Verification

| 検証質問 | 結果 | Confidence | 修正 |
|---|---|---:|---|
| Kaggle/公開データでEPS故障やRCAを直接検証できるか | できない。EPS内部信号やDTCが不足する。 | High | 故障検知ではなくEvidence Readiness検証に限定 |
| 公開データで市場需要に接続できるか | できる。NHTSA caseでdriver-visible pain、commaで走行context proxyを作れる。 | High | 市場痛み + proxy windowに分解 |
| SCN001で1ページsampleを作れるか | 作れる。必要facts、confirmed/unconfirmed/do-not-inferを整理可能。 | High | 次アクションをsample化に変更 |
| 既存診断不足を主張できるか | できない。対象EPS内部仕様が必要。 | High | 不足断定を禁止 |
| 事業価値は何で判定するか | RCA/8D/顧客品質報告に転記できるか。 | Medium | Kill条件を転記可能性に置く |
