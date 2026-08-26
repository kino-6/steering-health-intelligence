# 206. 車検データの原因別分解 — 事前登録

**結果を1つも見る前に書き、単独でコミットする。**

## なぜやるか

[docs/150](150_advisory_precedence_verification.md) は英国車検2024/2025を車両IDで連結し、
**兆候(advisory)のみが付いた個体は翌年の操舵系不合格が最大24.1倍**であることを示した。
本研究の実車側の結果として最も強い。

**しかし操舵系をひとまとめにしており、原因別に分けていない。**

一方 [docs/189](189_five_limits_tested.md) ① は `Electronic power steering` 配下の**9項目だけ**を見て
「兆候の記録が2,177万台中64台しかない」と結論した。

**その中間が空いている。**乗用車のパワーステアリング項目は **59件**あり、
うち **25件が兆候(advisory)と不合格(fail)の対を持つ。**

| 兆候 | 不合格 |
|---|---|
| wiring slightly corroded | wiring excessively corroded |
| wiring slightly damaged | wiring excessively damaged |
| has slight seepage | leaking |
| slightly corroded | excessively corroded |
| — | malfunctioning / inoperative / warning lamp indicates a failure |

**この59項目は使ったことがない。**

## 原因の分類(実行前に固定)

`rfr_desc` と `rfr_advisory_text` の語で分ける。**59項目の内訳は既に数えた**(下記)。
**値は見ていない——これは項目定義ファイルの集計であって、車両の記録ではない。**

| 族 | 判定語 | 項目数 |
|---|---|---|
| corrosion | corrod | 4 |
| damage | damag / fractur / split / cut | 10 |
| leak | leak / seepage / fluid / reservoir | 7 |
| security | insecure / loose / missing / removed / disconnect | 8 |
| **function** | inoperative / malfunction / warning lamp / not working | **6** |
| geometry | misalign / fouling | 8 |
| modification | modif / repair | 16 |

## 母集団(docs/150 と同一)

乗用車(test_class_id = 4)、通常検査(test_type = NT)、結果が P/F/PRS、**2024年と2025年の両方で受検した車両**。
2024年の状態は `fail`(F または P) / `sign`(A または M、failを含まない) / `clean` の3群。

## 3つの問い

### M1. 原因によって先行率は違うか

2024年に族Xの兆候が付いた車両の、2025年パワーステアリング不合格率。**族ごとに分母つきで報告する。**

### M2. 先行は原因特異的か

```
S_X = P(2025に族Xで不合格 | 2024に族Xの兆候) / P(2025に族Xで不合格 | 2024に何らかのPS兆候)
```

**S_X が大きいほど「同じ欠陥が悪化しただけ」に近い。**小さければ、兆候は部位を越えた系の劣化を指している。

### M3. EPSの橋 — 配線の兆候は機能不全に先行するか

**これが本研究の中心に最も近い。**

配線・電気系の兆候(`wiring slightly corroded` / `wiring slightly damaged`)が付いた車両は、
翌年 **function 族**(inoperative / malfunctioning / warning lamp)で落ちやすいか。

配線の腐食・損傷は**接触不良を通じて断続故障を生む**機構であり、
[docs/175](175_close_contact_question.md) が公開データ不足で閉じた接点系の問いに、
**実車側から別経路で触れることになる。**

## 判定基準(いま固定する)

| # | 基準 | 閾値 |
|---|---|---|
| **M1** | 族ごとの率と倍率を報告 | **閾値なし。n も併記する** |
| **M2 原因特異性** | S_X ≥ 2.0 | **n ≥ 1,000 の族の半数以上で成立すれば「原因特異的」と判定** |
| **M3 EPSの橋** | 配線兆候群の function 不合格率が clean 群の **3.0倍以上**、かつ配線兆候群の **n ≥ 100** | **両方を満たせば「橋が架かった」と判定** |

- **n が閾値に届かない族・群は「検定不能」と書く。**率だけを出して倍率を語らない
- M3が落ちたら、**配線の兆候は機能不全に先行しなかったと書く**
- **v2は作らない**

## 事前に認めておくこと

- **これは検査員の目視所見である。**部品内部の状態ではない
- **兆候は放置され、不合格は修理される**([docs/150](150_advisory_precedence_verification.md) の副次発見)。
  群間の比較にはこの非対称が入る
- **選択効果を除去できない。**兆候が付く車種・車齢は、もともと壊れやすい可能性がある
- **英国市場のデータである。**他市場へそのまま移さない
- **`Electronic power steering` の9項目は [docs/189](189_five_limits_tested.md) ① で検定不能と確定済み。**
  本件は一般の `Power steering` 59項目であり、量がどれだけあるかは**未知である**

## Rule Check

- **59項目の族別内訳は項目定義ファイルの集計であり、車両の記録ではない。**その区別を明記した
- n の下限を先に決め、**届かない場合は倍率を語らないと縛った**
- M3が落ちた場合に何と書くかを先に決めた
- 選択効果と修理の非対称を、結果より先に書いた

出典: DVSA MOT test extracts 2024/2025 (S4, Open Government Licence v3.0)
