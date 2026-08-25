# 190. 「Assyごと交換」は何を意味するか

[docs/189](189_five_limits_tested.md) の⑤で「EPS系の不具合にギアAssy交換が指示された車両が140万台」と書いた。
**この数字は誤りだった。**そして正しく数え直したところ、**元の解釈より強い結論が出た。**

## 訂正 — 140万台は 223,159台

docs/189 の照合は是正文に `replac` と `assembl` が**どこかに**あれば拾っていた。
これが 14V153000(1,373,177台)を巻き込んでいた。この是正文は

> GM will notify owners, and dealers will **perform one of four bulletins**.

であり、**Assy交換ではない。**この1件だけで当時の数の98%を占めていた。

部位名を明示した照合(是正文が gear / rack assembly の交換を指す)に絞ると:

| | キャンペーン | 台数 |
|---|---|---|
| EPS系 かつ ギアAssy交換 | **11** | **223,159** |

台数は下限である。是正文が短く部品名を書かない場合は拾えない。

## 本題 — Assy交換は2種類に割れる

| 是正の型 | キャンペーン | 台数 |
|---|---|---|
| **無条件**(全数交換) | 7 | 37,010 |
| **条件付き**(調べてから交換) | 4 | 186,149 |

**台数の83%は「全数交換」ではない。**
つまりメーカーはAssy丸替えを既定にしているのではなく、**選別できる根拠がある時は選別している。**

## 決定的な点 — 選別の根拠は2種類しかない

EPS系リコールで条件付き交換を指示した19キャンペーン(1,686,283台)を、
「何を見て決めるか」で分類した。

| 選別の根拠 | キャンペーン | 台数 |
|---|---|---|
| **動作履歴**(保存された故障コード・信号喪失の記録) | 4 | **1,346,528** |
| 製造ロット(シリアル番号・ロットコード・部品番号) | 4 | 142,044 |
| 記載なし | 11 | 197,711 |

根拠が書かれている8件は、**「どう動いたか」か「誰が作ったか」のどちらか**しかない。

動作履歴で選別している4件は同一の書式である(Ford系3件 + 同プラットフォームのMazda 1件):

> Ford will notify owners, and dealers will update the software for the power steering
> control module (PSCM) ... **If a vehicle shows a history of a loss of the torque sensor
> signal or fault codes relating to the PSCM** when the vehicle is brought in for the
> recall remedy, **the affected components will be replaced**, free of charge.
> — 14V284000 (740,878台)

> dealers will check the Power Steering Control Module (PSCM) for Diagnostic Trouble Codes (DTC).
> **If dealers find any loss of steering assist DTCs, the steering gear will be replaced.**
> **If no codes are found** ... the PSCM software will be updated.
> — 15V340000 (393,623台)

**ECU内部に保存された記録の有無だけで、134万台の交換/非交換が決まっている。**
記録がなければソフト更新だけで帰す。

## ここから言えること

1. **部品内部の記録で交換を選別する運用は、既に134万台規模で成立している。**
   仮説ではない。2014〜2015年に実施済みである。

2. **ただし判定材料は「故障の記録」である。**
   トルクセンサ信号の喪失、アシスト喪失のDTC——**すでに機能が失われた事実**の記録であって、
   劣化の予兆ではない。記録がない車は「まだ壊れていない」としか言えず、
   **今後壊れるかどうかは判別されないまま返される。**

3. **したがって空欄は「記録を使うこと」ではなく「記録の中身」である。**
   本研究が扱ってきた個体基準線・動作点正規化・k-of-N再発判定は、
   この既存の運用に載せる中身の側にあたる。土台は既にある。

## 言えないこと

- **無駄の量・金額**。無条件交換7件が過剰だったとは言えない。リコールの是正は
  欠陥確認済みの正しい交換であり、確実性・作業時間・責任を優先して全数交換を選ぶのは正常である。
- **「小部品で済んだはず」**。公開データに部位特定の情報はない。
- **選別の効き**。記録で選別した134万台のうち何台が実際に交換されたかは公開されていない。
- 「記載なし」11件が実際に何を見ていたか。是正文が書いていない。

## Rule Check

- **自分の誤りを先に書いた。**140万台は取り下げ、223,159台に訂正した
- 数え方を締めたら結論が弱くなるのではなく強くなった。**弱くなっていた場合も同じように書く**
- 「Assy丸替えは粗い」という当初の解釈は**データに否定された。**選別できる時は選別していた
- 台数は下限であることを明記した

再現: [scripts/eps_assembly_remedy_split.py](../scripts/eps_assembly_remedy_split.py) /
数表: [data/eps_assembly_remedy_split.tsv](../data/eps_assembly_remedy_split.tsv) /
出典: NHTSA FLAT_RCL_POST_2010 (S1, public domain)
