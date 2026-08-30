# 230. 棚卸しの失敗 — 使っていたリポジトリの中に、触っていない電子部品データが3件あった

**指摘を受けて確認したところ、私の棚卸しが漏らしていた。**

> 「公開データのうち、NASAやKaggleは何らかの兆候があるデータが公開されているはずでしょ？
> それなのにどうしてわざわざ再度解析して、無いと言っているの？」(2026-08-30)

## まず訂正 — 私の説明が誤っていた

前の報告で「MOSFETデータ：動作モードが違った」と書き、**データが使えないかのように述べた。誤りである。**

[docs/199](199_pulse_thermal_results.md) の訂正が壊したのは **capability値の物理的導出**であって、
**兆候が見えること自体ではない。**

| | |
|---|---|
| **兆候は見えるか** | **見える。**[docs/167](167_precursor_results_v2.md) NASA MOSFET **6/6**、故障の1〜2段階前、ノイズの**20〜300倍**。**一度も取り下げていない** |
| 兆候を「本来の何%」に変換できるか | できない([docs/203](203_cross_machine_replication_results.md)) |
| **無いのは何か** | **断続故障のデータ。**兆候一般ではない |

**「無い」と「変換できない」を混同させる書き方をした。**

## そして棚卸しが漏らしていた

[AGENTS.md](../AGENTS.md) 検証作法2は「**棚卸しは総覧論文を起点にする**」と定めている。
[docs/159](159_public_dataset_reinventory.md) も [docs/214](214_dataset_reinventory_2026_08.md) も
**キーワード検索だけで、総覧を起点にしていなかった。**

**NASA PCoE リポジトリ(S8で既に使っていた)の全21データセットを列挙したところ、
電子部品のrun-to-failureが3件あり、うち2件を取得していなかった。**

| # | データセット | 状態 |
|---|---|---|
| **8** | **IGBT Accelerated Aging** | **未取得だった → 本日取得** |
| 12 | Capacitor Electrical Stress | **未取得**(5.0 GB) |
| 13 | MOSFET Thermal Overstress Aging | 使用済み(S8) |
| 14 | Capacitor Electrical Stress-2 | **未取得** |

**同じリポジトリの中である。**探し方の問題であって、データが無かったのではない。

## 取得したもの: IGBT Accelerated Aging (S11)

**[docs/199](199_pulse_thermal_results.md) の欠陥が、このデータには当てはまらない。**

| | S8 (MOSFET、使用済み) | **S11 (IGBT、本日取得)** |
|---|---|---|
| 動作モード | **能動領域のみ**(素子をヒーターとして使用) | **矩形波ゲート(スイッチ動作)と DCゲート(能動領域)の両方** |
| 電圧信号 | drainSourceVoltage のみ | **GATE_VOLTAGE と COLLECTOR_VOLTAGE の両方** |
| 電流信号 | drainCurrent | **GATE_CURRENT と COLLECTOR_CURRENT** |
| 温度 | package / flange | **HEAT_SINK_TEMP / PACKAGE_TEMP** |
| パラメトリック特性 | 無し | **区間ごとに Turn On / LeakageIV / Breakdown** |
| 個体 | 6 | Device 2〜5 + SMU特性評価 20 MOSFET / 13 IGBT部品 |

**EPSのインバータはスイッチとしてMOSFETを使う。**
S8はスイッチとして一度も動いていなかった([docs/199](199_pulse_thermal_results.md))。
**S11のsquare signal側は、その動作モードで劣化させている。**

さらに **`Turn On.csv` は転送特性(しきい値)、`LeakageIV.csv` は漏れ電流、`Breakdown.csv` は降伏電圧**を
区間ごとに記録している。**これは「どのパラメータが先に動くか」を直接見られる形である。**

配布物には論文 `Sonnenfeld_Goebel_Celaya.pdf` と `Readme.doc` が同梱されている。
**[AGENTS.md](../AGENTS.md) 作法1のとおり、解析設計の前にこれを読む。**

## この失敗が意味すること

- **[docs/224](224_current_conclusion.md) の「到達できないこと」は、断続故障については変わらない。**
  IGBTデータも恒久劣化であり、断続は含まない見込みである(未確認)
- **しかし「解法に届いていない」の根拠は弱くなる。**
  [docs/199](199_pulse_thermal_results.md) の「動作モードが違う」はS8固有の問題であり、
  **S11で同じ検証をやり直せる**
- **棚卸しの作法を守っていなかった。**総覧を起点にせず、キーワードで探していた

## 次にやること

1. **配布論文とReadmeを読む**(作法1)
2. **square signal側の劣化runで、[docs/192](192_str_capability_rule_protocol.md)〜[199](199_pulse_thermal_results.md) の検証をやり直す**——
   **今度は正しい動作モードで**
3. Capacitor(12/14)の取得可否を判断する

**いずれも事前登録の後に行う。**

## Rule Check

- **自分の説明の誤り(「兆候が無い」と読める書き方)を冒頭で訂正した**
- **棚卸しの作法を守っていなかったことを、見つけたデータより先に書いた**
- 未取得の2件(Capacitor)も**同じ表に載せた。**見つけた1件だけを書かない
- IGBTデータが断続を含むかは**未確認**と明記した
- 解析の前に配布論文を読むと書いた(作法1)

出典: NASA PCoE, IGBT Accelerated Aging (S11, public domain)
