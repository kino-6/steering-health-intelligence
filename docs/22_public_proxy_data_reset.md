# 22. Public Proxy Data Reset

## Purpose

`chain-of-verification` で前提を潰した結果、内部の返却品・NTF・再現不能案件にはアクセスできないことが分かった。

したがって、次の仮説は成立しない。

> EPSサプライヤ内部の過去20-50件の返却品・NTFケースを分類し、不足証跡を特定する。

このメモでは、代替として、市場情報、NHTSA、Kaggle、公開CAN / steering datasetで何を補えるかを整理する。

## Updated User-Provided Assumptions

| Question | Answer | Impact |
|---|---|---|
| 内部返却品・NTF案件にアクセスできるか | できない。抽象的なことしか書けない | 内部backlog analysisは初期手段にできない |
| 20-50件分類の現実性 | 対象車種の市場規模による | 公開市場規模・公開苦情件数から対象選定が必要 |
| 明確に困っているサプライヤ内部門 | いない。強いて言うならエンドユーザ | サプライヤ品質業務ではなく、driver value / market valueに寄せる必要 |
| 現在の困りごと | 特にない。ただし市場需要と付加価値としてあると思う | 顕在課題ではなく、価値仮説として検証する |
| DTC以外の診断証跡 | 少し | 既存診断との差分は小さく、公開データでは内部証跡は見えない |

## Corrected Conclusion

現時点の結論:

> 内部NTF / 返却品ケースにアクセスできないなら、`診断証跡改善` を直接検証することはできない。公開データでできるのは、EPS関連の市場痛み、ドライバーが感じる危険・不安、通常走行時のステアリング挙動、異常検知デモの代理検証までである。

つまり、公開データで補えるのは `原因解析` ではなく、次の3つ。

1. EPS不具合が市場でどんなドライバー痛みとして現れるか
2. 正常走行時のsteering / speed / lateral dynamicsから、どんな文脈特徴量を作れるか
3. その特徴量が、将来のEPS付加価値仮説を説明するデモに使えるか

## What Public Data Can And Cannot Do

| Item | Public / Kaggle data can do | Public / Kaggle data cannot do |
|---|---|---|
| 市場痛み | NHTSA complaints / recallsから、loss of assist、steering effort、warning、driver concernを分類する | サプライヤ内部の真因や保証解析を知る |
| 正常挙動 | steering angle、vehicle speed、lateral acceleration、CAN信号から通常挙動モデルを作る | EPS内部のmotor current、assist torque、DTC、freeze frame不足を知る |
| 異常代理 | 急なsteering effort proxy、steering response mismatch、driver style / road contextを模擬する | 実際のEPS劣化や故障予測を検証する |
| エンドユーザ価値 | ドライバーが不安に感じる状況を説明する | ドライバーが直接この機能に払うかを証明する |
| OEM提案 | 公開事例と代理デモで問題設定を見せる | OEMが量産診断仕様に入れる価値を証明する |

## Public Data Sources Worth Using

| Source | Useful signals | Use |
|---|---|---|
| NHTSA EPS report / VOQ / recall material | loss of assist, increased steering effort, driver complaint pattern, recall causal categories | Market pain and driver concern taxonomy |
| NHTSA recalls / investigations | affected population, complaints, field reports, crash allegations, repair action | Market signal and failure scenario taxonomy |
| commaSteeringControl | steerFiltered, lateral acceleration, roll, EPS firmware version, steering-related dynamics | Normal steering behavior and control-response proxy |
| nuScenes CAN bus expansion | steering angle feedback, vehicle speed, acceleration, wheel speed | Public CAN-based steering context demo |
| Kaggle OBD-II / CAN driving behavior | OBD/CAN driving style and raw driving behavior features | Driver behavior / usage-context proxy |
| Kaggle self-driving behavioral cloning datasets | steering angle with road images | Steering demand / road context proxy |
| LiRA-CD | vehicle CAN / AutoPi signals including steering angle and road-condition context | Road-condition / steering-context proxy |

## Revised Exploration Tracks

### Track A: Driver-visible market pain

Question:

> EPS issues appear to the driver as what kind of problem?

Use:

- NHTSA complaints
- recalls
- safety investigation summaries
- public repair / complaint narratives if needed

Outputs:

- loss-of-assist scenario taxonomy
- driver pain words: heavy steering, warning, inability to turn, low-speed risk, tow, intermittent failure
- target vehicle segment / market size hypothesis

Value:

This validates whether the end-user pain exists.

Limit:

It does not prove a supplier-side feature solves it.

### Track B: Public steering behavior model

Question:

> Can public steering / CAN datasets create a useful context model without EPS internals?

Use:

- commaSteeringControl
- nuScenes CAN bus
- Kaggle OBD-II / CAN datasets

Possible features:

- steering angle vs speed
- steering rate
- lateral acceleration vs steering angle
- steering demand during low-speed maneuver
- driver style / aggressive steering proxy
- road roll / curvature / vehicle dynamics context

Value:

This can produce a demo that explains `context-aware steering evidence` without claiming real EPS failure prediction.

Limit:

It cannot validate DTC / freeze frame / internal motor current evidence.

### Track C: Public proxy demo

Question:

> If we cannot access internal EPS fault data, what demo can still show the idea?

Better demo:

> Steering Context Risk Explorer

It would show:

- high steering demand at low speed
- steering behavior outliers vs normal data
- contexts where loss of assist would be driver-visible
- what additional EPS-local data would be needed to move from proxy to real diagnosis

Bad demo:

> EPS failure prediction from public data

Reason:

Public data lacks real EPS fault labels and internal EPS signals.

## Chain-of-Verification Result

### Draft claim

> Public and Kaggle data can replace internal NTF case classification.

### Verification

| Question | Evidence / reasoning | Confidence | Impact |
|---|---|---:|---|
| Does public data contain EPS internal DTC / freeze frame / return-part evidence? | Public steering/CAN datasets mainly contain steering angle, speed, acceleration, driver behavior, or dynamics signals. | High | Revise. It cannot replace internal case classification. |
| Does public data show driver-visible EPS market pain? | NHTSA and recall materials include loss of assist, increased steering effort, complaints, field reports, and investigations. | High | Keep. Good for market pain taxonomy. |
| Can Kaggle/public CAN data support a technical demo? | commaSteeringControl and nuScenes CAN include steering-related dynamics; Kaggle OBD/CAN datasets provide driving behavior proxies. | High | Keep, but only as proxy demo. |
| Can it prove business value to EPS suppliers? | No direct buyer or internal workflow owner is established. End-user is named as the closest beneficiary, but the purchase channel is OEM. | Medium | Revise. Business value remains hypothetical. |
| Can it support failure prediction? | No real EPS failure labels or internal assist/current/freeze-frame signals. | High | Remove failure prediction claim. |

### Corrected claim

> Public data cannot replace internal EPS NTF / return-part case classification. It can only create a market-pain taxonomy and a steering-context proxy demo. This is still useful if the next goal is to test whether driver-visible EPS reliability or steering-confidence value exists, but it cannot validate supplier diagnostic evidence value.

## New Kill Criteria

Stop or pivot if:

1. Public EPS complaints are too rare or too brand/model-specific to generalize
2. Driver pain exists but cannot be connected to an OEM-buyable feature
3. Public steering data only supports generic ADAS / autonomous driving demos, not EPS value
4. No measurable proxy can distinguish high-value steering contexts
5. The concept collapses into generic vehicle health monitoring

## Next Step

最初の自動探索は次がよい。

1. NHTSA / recall public dataから、EPS loss-of-assist / increased steering effort事例を30-100件抽出する
2. Kaggle / public CAN datasetsを棚卸しし、使える信号と使えない信号を表にする
3. `driver-visible EPS pain taxonomy` と `public steering proxy feature list` を作る
4. それでも価値が残るかをCoVeで再検証する

