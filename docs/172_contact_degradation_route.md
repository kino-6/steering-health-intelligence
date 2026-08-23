# 172. 接点劣化(A'')の検証経路

## 判断

**1. リコール記録はA''に答えられない。** 進行性を示すように見えた語は定型句だった。

**2. 文献レベルでは、frettingは接触抵抗の進行的上昇を起こす。ただし軌跡は「膝」型であり、水準ベースの指標では先行時間が短い可能性が高い。**

**3. 検証できる公開データが見つかった**——SOReDD(Stuttgart Open Relay Degradation Dataset、DOI 10.18419/darus-2785)。**開閉サイクルごとの接触抵抗を故障まで記録**している。

## 1. リコール記録では決着しない(自分の集計の誤りを含む)

EPSリコール183キャンペーンで進行性の語を数えたところ54.1%が該当した。**しかしこれは誤りである。**

fretting/corrosion を含む6キャンペーンを原文で確認すると、進行性語 `increasing` の実体は次だった。

> "A greater steering effort would be needed to control the vehicle if power steering is lost, **increasing the risk of a crash**."

**「crash riskが増える」という定型句**であり、接触抵抗の進行とは無関係である。GMの4キャンペーン(16V160/17V382/19V801/20V254)すべてが同じ文である。

原因記述は一貫して次の形で、**進行の記述が無い**。

> "Corrosion of the connector between the electric power steering module and the torque sensor connector **may cause a loss of electric power steering assist**."

原因(腐食)と結果(アシスト喪失)だけで、その間の時間発展が書かれていない。
これは [docs/171](171_eps_wearout_mechanism_scan.md) が特定した「リコールは摩耗故障を構造的に見られない」の具体例である。**この経路は閉じる。**

## 2. 文献が言っていること(二次情報として扱う)

公開文献では、fretting corrosion による接触抵抗の増加は確立した現象である。ただし軌跡の形が重要である。

> 接触抵抗の急激な増加は概ね**数千fretting cycleのオーダー**で起こり、抵抗変化は**数十mΩからΩ、さらに開放**まで及ぶ。
> 膜の破断と再酸化により、抵抗は**不安定に変動**する。

**含意は2つある。**

- **膝型の軌跡**: 長く低位安定 → 閾値後に急上昇。**水準を見る指標では先行時間が短い**
- **不安定性が先行しうる**: 膜の破断・再酸化による変動は、水準が上がる前から現れる可能性がある

後者は [docs/168](168_transfer_reduces_to_spec.md) が立てた仮説「単調量は水準ではなく**発生率**ではないか」と同じ方向を指す。
そして [docs/121](121_steering_predictive_diagnostics_power_monitor_case.md) の payload は最初から `recurrence` を持っている。

**ただしこれは他者の測定であり、本研究では再導出していない。** [AGENTS.md](../AGENTS.md) 1条の意味で、二次情報として扱う。

## 3. 検証経路: SOReDD

| 項目 | 内容 |
|---|---|
| データ | Stuttgart Open Relay Degradation Dataset (SOReDD) |
| 出典 | <https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/darus-2785> / 論文 [arXiv:2204.01626](https://arxiv.org/abs/2204.01626) |
| 内容 | 電磁リレーを異なる負荷条件で**故障まで開閉し続けた**試験。**開閉サイクルごとの接触抵抗**を記録 |
| なぜ効くか | **接点界面の劣化 → 接触抵抗**という、A''と同じ対象クラス。しかもrun-to-failureで**サイクル単位の時系列**がある |
| 何が測れるか | ①軌跡が膝型か ②**水準が上がる前に変動(不安定性)が先行するか** ③先行時間 |

**限界(先に固定)**: リレーは自動車用コネクタではない。接点の開閉によるアーク侵食・膜形成が主機構であり、
frettingは微摺動が主機構である。**言えるのは「接点界面劣化において、水準より変動が先行するか」という機構レベルまで**である。

## 棚卸しへの第3軸の追加

[docs/159](159_public_dataset_reinventory.md) は棚卸しを「用途軸 / 部品軸」の2軸で行うと決めた。
[docs/168](168_transfer_reduces_to_spec.md) / [docs/171](171_eps_wearout_mechanism_scan.md) を経て、**第3軸「接点・接続の劣化」**を追加する。

| 軸 | 検索語の例 |
|---|---|
| 用途軸 | steering / EPS / chassis / vehicle |
| 部品軸 | PMSM / BLDC / inverter / winding / MOSFET / IGBT |
| **接点軸(新)** | **connector / contact resistance / fretting / relay / terminal / crimp** |

この軸で今回見つかったのが SOReDD である。**2軸のままなら見つからなかった。**

## Rule Check

- **自分の集計(進行性54.1%)が定型句に汚染されていたことを発見し、否定した**
- リコール経路を「閉じる」と明記し、未解決項目として残していない
- 文献の記述を**二次情報**として明示し、本研究の測定と区別した
- 検証経路の限界(リレー ≠ 自動車コネクタ、機構が違う)を、着手前に固定した
- 棚卸しの軸を1つ増やし、手順として記録した
