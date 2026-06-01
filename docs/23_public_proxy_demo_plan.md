# 23. Public Proxy Demo Plan: Steering Context Risk Explorer

## Purpose

公開データ前提で、`1. 市場痛みの公開分類`、`2. 公開ステアリングデータセット棚卸し`、`3. 代理デモ案` をつなげる。

内部のEPS DTC、freeze frame、返却品解析、NTF案件にはアクセスできない。
したがって、ここで作るデモは `EPS故障予測` ではない。

## Correct Demo Frame

良い言い方:

> Steering Context Risk Explorer

目的:

> 公開データから、ドライバーがEPS assist lossやsteering effort増加を痛く感じやすい運転文脈を可視化し、将来EPS-local evidenceやOEMデータが必要になる境界を示す。

悪い言い方:

> Public dataでEPS故障を予測する。

理由:

- 公開steering datasetにはEPS内部故障ラベルがない
- DTC / freeze frame / assist current / motor currentがない
- 返却品解析やNTF分類は検証できない

## Inputs

### Market-pain cases

Use:

- `data/eps_public_market_pain_cases.tsv`

Extract:

- driver-visible pain
- scenario context
- scale signal
- reported or suspected cause
- proxy feature hint

Initial pain taxonomy:

| Pain category | Public examples |
|---|---|
| Increased steering effort | GM, Ford, Tesla, Mazda, Acura recalls/investigations |
| Warning / lamp / chime | GM, Ford, Chrysler, Hyundai cases |
| Low-speed maneuver risk | GM and Tesla public materials repeatedly mention greater effort at low speeds |
| Intermittent assist loss | Ford Fusion, Cadillac/GM ignition-cycle cases, Chrysler Pacifica gradual-turn case |
| Road / pothole context | Tesla Model S/X recall |
| Gradual-turn sticking / sudden assist return | Chrysler Pacifica PE25009 |
| Component / supply-chain defect | Hyundai/Kia/Mando MDPS power pack cases |

### Public steering datasets

Use:

- `data/public_steering_dataset_inventory.tsv`

Preferred first dataset:

1. `commaSteeringControl`
2. `nuScenes CAN bus expansion`
3. Kaggle OBD-II / CAN driving behavior dataset

## Proxy Features

The demo should compute or visualize public-data proxy features.

| Proxy feature | Signals needed | Why it matters |
|---|---|---|
| Low-speed high steering demand | speed + steering angle / steerFiltered | Loss of assist is more painful at low speeds |
| Steering rate / rapid steering | steering angle or steerFiltered over time | Captures sudden steering demand |
| Steering response mismatch | desired lateral acceleration vs steering-derived lateral acceleration | Shows context where steering response differs from expectation |
| Repeated high-demand maneuvers | rolling count of high steering demand events | Usage-context proxy, not degradation proof |
| Road / roll context | roll + steering + lateral acceleration | Helps avoid overclaiming driver behavior as EPS issue |
| Warning-context placeholder | no public signal; simulated field only | Shows what EPS-local data would add |

## Demo Views

### View 1: Market Pain Map

Input:

- `data/eps_public_market_pain_cases.tsv`

Show:

- pain category counts
- scenario context counts
- source type distribution
- model/year examples
- public scale signals

Purpose:

> Show that driver-visible EPS pain exists in public sources, without claiming direct business demand.

### View 2: Steering Context Explorer

Input:

- public steering time-series dataset

Show:

- speed vs steering demand
- steering demand over time
- low-speed high-demand segments
- outlier segments vs normal segments
- optional road / roll context if available

Purpose:

> Show that public data can identify contexts where assist loss would be more noticeable to the driver.

### View 3: Evidence Gap Overlay

Input:

- market-pain categories
- proxy features

Show:

| Question | Public data can show | EPS/OEM data still needed |
|---|---|---|
| Was steering demand high? | Yes, via steering/speed/lateral dynamics | EPS assist current / motor torque |
| Was driver exposed to low-speed high effort? | Yes, via speed + steering demand | Driver effort / torque sensor |
| Was there a warning or DTC? | No, unless public case text says so | DTC / freeze frame / event memory |
| Was EPS failing? | No | fault label / service record / return-part analysis |
| Is this a warranty/NTF case? | No | OEM warranty / supplier quality data |

Purpose:

> Make the boundary clear so the demo does not overclaim.

## Minimal Implementation Plan

### Phase 1: Static analysis

Generate from TSV only:

- pain category counts
- source counts
- proxy feature hint counts
- top scenario contexts

No dataset download required.

### Phase 2: Dataset notebook

Pick one public dataset:

- Start with `commaSteeringControl` if download is practical
- Fallback to `nuScenes CAN bus` if already available
- Fallback to a small Kaggle OBD/CAN dataset if Kaggle access works

Compute:

- speed distribution
- steering demand distribution
- low-speed high-demand events
- steering rate events
- context windows around events

### Phase 3: Demo page or notebook

Create:

- a notebook or static HTML
- visualizations
- a section explicitly titled `What this does not prove`

## Chain-of-Verification

### Draft claim

> Public datasets can support a demo for EPS reliability value.

### Verification questions

1. Do public steering datasets include real EPS fault labels?
2. Do public cases show driver-visible pain?
3. Can public steering data identify high-pain contexts?
4. Can this prove an EPS supplier diagnostic feature has value?
5. Can this become a clean demo without overclaiming?

### Evidence checks

| Question | Evidence | Confidence | Impact |
|---|---|---:|---|
| Do public steering datasets include real EPS fault labels? | Dataset inventory shows steering dynamics and CAN signals, but not EPS fault labels or return-part outcomes. | High | Do not claim fault prediction. |
| Do public cases show driver-visible pain? | NHTSA/recall cases repeatedly mention loss of assist, increased effort, warnings, low-speed risk, intermittent assist behavior. | High | Keep market-pain taxonomy. |
| Can public steering data identify high-pain contexts? | commaSteeringControl and nuScenes expose steering/speed/lateral dynamics usable for low-speed high-demand and steering response contexts. | Medium-High | Build context proxy, not diagnosis. |
| Can this prove supplier diagnostic feature value? | No internal buyer, DTC gap, warranty, or return-part data is available. | High | Keep as market/demo exploration only. |
| Can this become a clean demo without overclaiming? | Yes if the demo explicitly separates public proxy features from missing EPS/OEM evidence. | Medium | Add Evidence Gap Overlay. |

## Success Criteria

The proxy demo is useful if it can answer:

1. What public EPS pain appears repeatedly?
2. What driving contexts make assist loss more painful?
3. Which public signals can show those contexts?
4. Which EPS-local/OEM signals are still missing?
5. Does the idea remain EPS-specific, or does it collapse into generic ADAS / vehicle health?

## Kill Criteria

Stop or pivot if:

1. Public pain cases are mostly one-off recalls with no reusable driver pain pattern
2. Public steering data cannot produce meaningful low-speed / steering-demand context features
3. The demo looks like generic driving behavior analytics
4. The missing evidence list is larger than the demonstrated value
5. No plausible OEM-buyable feature emerges from the demo

## Recommended Next Action

Build Phase 1 first:

> A static market-pain and proxy-feature summary from `data/eps_public_market_pain_cases.tsv`.

This is the fastest check before downloading large public datasets.
