# 23. 公開データ代理デモ計画: Steering Context Risk Explorer

## 目的

公開データ前提で、`1. 市場痛みの公開分類`、`2. 公開ステアリングデータセット棚卸し`、`3. 代理デモ案` をつなげる。

内部のEPS DTC、freeze frame、返却品解析、NTF案件にはアクセスできない。
したがって、ここで作るデモは `EPS故障予測` ではない。

## 正しいデモの位置づけ

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

## 入力

### 市場痛みケース

使用ファイル:

- `data/eps_public_market_pain_cases.tsv`

抽出するもの:

- driver-visible pain
- scenario context
- scale signal
- reported or suspected cause
- proxy feature hint

初期の痛み分類:

| 痛みカテゴリ | 公開例 |
|---|---|
| Increased steering effort | GM、Ford、Tesla、Mazda、Acuraのrecall / investigation |
| Warning / lamp / chime | GM、Ford、Chrysler、Hyundai系ケース |
| Low-speed maneuver risk | GMやTeslaの公開資料では、低速時に操舵努力が増える説明が繰り返し出る |
| Intermittent assist loss | Ford Fusion、Cadillac/GM ignition-cycleケース、Chrysler Pacifica gradual-turnケース |
| Road / pothole context | Tesla Model S/X recall |
| Gradual-turn sticking / sudden assist return | Chrysler Pacifica PE25009 |
| Component / supply-chain defect | Hyundai / Kia / Mando MDPS power packケース |

### 公開ステアリングデータセット

使用ファイル:

- `data/public_steering_dataset_inventory.tsv`

最初に見る候補:

1. `commaSteeringControl`
2. `nuScenes CAN bus expansion`
3. Kaggle OBD-II / CAN driving behavior dataset

## Proxy Feature

デモでは、公開データで近似できるproxy featureを計算または可視化する。

| Proxy feature | 必要信号 | 意味 |
|---|---|---|
| Low-speed high steering demand | speed + steering angle / steerFiltered | assist lossが起きると低速時ほどドライバー負担が大きい |
| Steering rate / rapid steering | steering angle or steerFiltered over time | 急操舵需要を捉える |
| Steering response mismatch | desired lateral acceleration vs steering-derived lateral acceleration | 期待する応答とsteering由来応答の差を見る |
| Repeated high-demand maneuvers | rolling count of high steering demand events | 使用文脈proxy。劣化証明ではない |
| Road / roll context | roll + steering + lateral acceleration | road/roll影響を見て、driver behaviorをEPS問題と誤認しないため |
| Warning-context placeholder | public signalなし。simulated fieldのみ | EPS-local dataがあれば何が足されるかを示す |

## デモ画面

### View 1: Market Pain Map

入力:

- `data/eps_public_market_pain_cases.tsv`

表示するもの:

- pain category counts
- scenario context counts
- source type distribution
- model/year examples
- public scale signals

目的:

> 公開ソース上にdriver-visible EPS painが存在することを示す。ただし、直接の事業需要までは主張しない。

### View 2: Steering Context Explorer

入力:

- public steering time-series dataset

表示するもの:

- speed vs steering demand
- steering demand over time
- low-speed high-demand segments
- outlier segments vs normal segments
- optional road / roll context if available

目的:

> assist lossが起きた場合にドライバー負担が大きくなりそうな文脈を、公開データから特定できることを示す。

### View 3: Evidence Gap Overlay

入力:

- market-pain categories
- proxy features

表示するもの:

| 問い | 公開データで見えること | まだ必要なEPS/OEMデータ |
|---|---|---|
| 操舵要求は高かったか | steering / speed / lateral dynamicsで見える | EPS assist current / motor torque |
| 低速高操舵負荷に晒されていたか | speed + steering demandで見える | driver effort / torque sensor |
| warningやDTCがあったか | 公開テキストに書かれていれば見える | DTC / freeze frame / event memory |
| EPSは故障していたか | 見えない | fault label / service record / return-part analysis |
| warranty / NTF案件か | 見えない | OEM warranty / supplier quality data |

目的:

> デモが言えることと言えないことの境界を明確にし、過剰主張を避ける。

## 最小実装計画

### Phase 1: 静的分析

TSVだけから生成する:

- pain category counts
- source counts
- proxy feature hint counts
- top scenario contexts

データセットのダウンロードは不要。

### Phase 2: Dataset notebook

公開データセットを1つ選ぶ:

- 容量とアクセスが現実的なら `commaSteeringControl`
- 既に使えるなら `nuScenes CAN bus`
- Kaggleアクセスが通るなら小さめのOBD/CAN dataset

計算するもの:

- speed distribution
- steering demand distribution
- low-speed high-demand events
- steering rate events
- context windows around events

### Phase 3: デモページまたはNotebook

作るもの:

- notebookまたはstatic HTML
- visualization
- `このデモが証明していないこと` セクション

## Chain-of-Verification

### Draft claim

> Public datasets can support a demo for EPS reliability value.

### 検証質問

1. 公開steering datasetには実EPS故障ラベルがあるか
2. 公開ケースからdriver-visible painは見えるか
3. 公開steering dataから高負担文脈は見えるか
4. これでEPSサプライヤ向け診断機能の価値を証明できるか
5. 過剰主張せずに綺麗なデモにできるか

### Evidence checks

| 問い | Evidence | Confidence | Impact |
|---|---|---:|---|
| 公開steering datasetには実EPS故障ラベルがあるか | Dataset inventoryではsteering dynamicsやCAN信号はあるが、EPS故障ラベルや返却品結果はない。 | High | 故障予測とは言わない。 |
| 公開ケースからdriver-visible painは見えるか | NHTSA / recall casesにはloss of assist、increased effort、warning、low-speed risk、intermittent assist behaviorが繰り返し出る。 | High | market-pain taxonomyは維持。 |
| 公開steering dataから高負担文脈は見えるか | commaSteeringControlやnuScenesにはsteering / speed / lateral dynamicsがあり、low-speed high-demandやsteering response contextを作れる。 | Medium-High | diagnosisではなくcontext proxyを作る。 |
| これでEPSサプライヤ向け診断機能の価値を証明できるか | 内部buyer、DTC gap、warranty、return-part dataがない。 | High | market/demo explorationに留める。 |
| 過剰主張せずに綺麗なデモにできるか | public proxy featureとmissing EPS/OEM evidenceを明示的に分ければ可能。 | Medium | Evidence Gap Overlayを入れる。 |

## 成功条件

Proxy demoが有用と言えるのは、次に答えられる場合。

1. 公開EPS painは何が繰り返し出るか
2. assist lossが痛くなる運転文脈は何か
3. その文脈を示せる公開信号は何か
4. まだ足りないEPS-local / OEM信号は何か
5. EPS固有の話として残るか、generic ADAS / vehicle healthに埋もれるか

## 撤退条件

停止またはピボットすべき条件:

1. 公開pain caseが一回限りのrecallばかりで、再利用できるdriver pain patternがない
2. 公開steering dataからmeaningfulなlow-speed / steering-demand context featureが作れない
3. デモがgeneric driving behavior analyticsに見える
4. missing evidenceの方がdemo valueより大きい
5. OEMが買える機能仮説に接続できない

## 推奨する次アクション

まずPhase 1を作る:

> `data/eps_public_market_pain_cases.tsv` から、static market-pain and proxy-feature summaryを作る。

大きな公開データセットをダウンロードする前に、最短で仮説の筋を確認できる。
