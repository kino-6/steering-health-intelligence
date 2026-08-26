# 183. 誤り条件1の点検 — AUTOSARは「宛先」を標準化し、「中身」を標準化していない

## 判断

**[docs/182](182_business_judgment_update.md) の誤り条件1(部品レベル指標の規格化)は、一部だけ踏まれている。**

| 何が | 状態 |
|---|---|
| **アクチュエータが能力(capability)をADSへ報告するという枠組み** | **標準化済み**(AUTOSAR VMC)。差別化にならない |
| **その能力が劣化でどう縮むかを、いつ・どう知るか** | **標準化されていない**。仕様に「劣化」「摩耗」「熱」の語が一度も無い |

**判断は維持する。ただし余白は狭まった。**

そして副産物として、**本研究の出力に標準化された宛先が見つかった。**

## 一次仕様で確認したこと

AUTOSAR CP R22-11 `EXP_AIADASAndVMC`(Explanation of Application Interface of AD/ADAS vehicle motion control)より。

### 操舵アクチュエータ層の役割は「capability情報と fail diagnostic」と定義されている

仕様の層構造表に、3系統が同じ形で並んでいる。

| 系統 | アクチュエータ層の役割(原文) |
|---|---|
| 駆動 | **PT capability information** and fail diagnostic |
| 制動 | **Brake capability information** and fail diagnostic |
| **操舵** | **STR capability information** and fail diagnostic |

**「故障診断」と「能力情報」が別々に並んでいる。** つまり規格は最初から、
**faultの有無とは別に「今どこまでできるか」を報告する枠**を持っている。

### capability は「実現できる値」として定義されている

駆動系の具体信号を見ると定義が分かる。

> **Powertrain acceleration capability upper limit** — Indicates the upper limit for the powertrain acceleration capability
> that can be realized as motion control. **Defined as a value that can be realized within ** msec**

**capability = 指定時間内に実現できる値。** 性能の包絡線であって、故障フラグではない。
関連して `PT system reliability`(PT internal status)、`system availability for ADAS request` も定義されている。

### そして劣化に関する語は一度も出てこない

| 語 | 出現数 |
|---|---|
| capability | 7 |
| availability | 1 |
| **degradation / degraded** | **0** |
| **health** | **0** |
| **wear** | **0** |
| **thermal / derating** | **0** |

**「能力を報告せよ」は書いてあるが、「能力が劣化でどう縮むかを知る方法」は書かれていない。**

## これが意味すること

### 1. 誤り条件1は部分的に踏まれている(=差別化の余白は狭い)

「アクチュエータがcapabilityを報告する」という**枠組みは既に標準**である。
これを提案しても新規性は無い。**インターフェースの発明では差別化できない。**

### 2. しかし肝心の部分は開いている

規格が書いていないのは次である。

- **capability値を、劣化を織り込んでどう決めるか**
- **capabilityが縮み始めたことを、どれだけ早く・どれだけ細かく知れるか**
- **その根拠として何を観測するか**

**これは [docs/153](153_sotif_eooc_assumption_sheet.md) のEooC仮定シートが書いている内容そのものである。**

[docs/182](182_business_judgment_update.md) の類型判断——「規制は結果を義務化し方法を開けている」——が、
**規格の側でも同じ形で成り立っていた。** AUTOSARは宛先(capability報告)を決め、中身(その値の根拠)を決めていない。

### 3. 副産物: 出力の宛先が標準化されていた

[docs/170](170_thermal_headroom_translation.md) が計算した「持続アシスト熱余裕の13〜50%喪失」は、
**まさに STR capability の縮小である。** faultは立たないが、実現できる操舵能力が減っている。

> **補足([docs/191](191_degradation_demand_and_sotif.md))**: この状態がSOTIFの担当であることを docs/191 で確定した。
> DTC未到達は「故障が既にあり閾値に達していない(ISO 26262)」と「故障が無いまま性能包絡が縮んだ(ISO 21448)」に割れる。

つまり本研究の出力は、**独自payloadを発明しなくても、既存の標準信号に載る。**

| 本研究の観測 | AUTOSARの宛先 |
|---|---|
| 熱余裕の喪失([docs/170](170_thermal_headroom_translation.md)) | **STR capability** の縮小 |
| 個体基準からの逸脱([docs/167](167_precursor_results_v2.md)) | 同上、または `system reliability` 相当 |
| DTC未満のcontext([docs/121](121_steering_predictive_diagnostics_power_monitor_case.md) payload) | fail diagnostic とは別枠の情報として |

**これは主張を強めるのではなく、実装の摩擦を下げる話である。** 宛先が標準にあるということは、
「新しいインターフェースを通す」交渉が要らないということである。

## 誤り条件1の書き直し

**旧**: 部品レベルの劣化指標が、規格または規制で具体的に規定される

**新(2段に分ける)**:

1. ~~アクチュエータの能力報告インターフェースが標準化される~~ → **既に標準化済み(AUTOSAR VMC)。踏まれた**
2. **capability値を劣化から導く方法(観測項目・閾値・時間分解能)が規格で具体的に規定される** → **未。これが残る誤り条件**

**2が起これば差別化は消える。** 監視すべきはAUTOSARの将来リリースであり、
とくに VMC/Chassis ドメインの application interface に劣化由来の capability 決定則が入るかである。

## Rule Check

- **自分が出した判断([docs/182](182_business_judgment_update.md))の誤り条件を、自分で点検した**
- 一次仕様(AUTOSAR CP R22-11 の公開PDF)にあたり、語の出現数まで数えた。二次情報で済ませていない
- **「部分的に踏まれている」を「踏まれていない」と丸めなかった**。差別化の余白が狭いことを先に書いた
- 副産物(宛先の標準化)を、主張を強める材料としてではなく**実装摩擦の話**として位置づけた
- 誤り条件を2段に分け、**次に何を監視すべきか**を具体化した
