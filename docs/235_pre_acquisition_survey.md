# 235. 取得せずに候補を評価した — 8件、うち取得ゼロ

**[data/dataset_prospect.tsv](../data/dataset_prospect.tsv) の運用を、実際に回した。**
**1件もダウンロードしていない。**配布ページとReadmeだけで判定した。

## 評価した8件

| 候補 | 容量 | 動作点 | 判定 | 理由 |
|---|---|---|---|---|
| **PHM Servomotor-Driven Ballscrew** | **21.3 GB** | — | **decline** | **Simulinkのシミュレーション。**実測ではない |
| **NASA Capacitor Electrical Stress 12/14** | 5.0 GB | **保持**(10/12/14 V 固定) | **decline** | 動作点は良質だが**[docs/224](224_current_conclusion.md) の空欄を埋めない** |
| OpenLKA | 500 GB+ | 不明 | decline | **DBC未整備で温度信号の有無が確認できない**([docs/214](214_dataset_reinventory_2026_08.md)) |
| Paderborn Bearing | — | 4条件で保持 | decline | ベアリングの振動。EPSの電気系に対応しない |
| DAMADICS Actuator | — | — | decline | 化学プラントのバルブ |
| IMAD-DS | — | — | decline | 音響・振動。EPSの電気内部量に対応しない |
| IEEE DataPort 誘導機ロータバー | — | — | decline | 誘導機。EPSはPMSM |
| 同 合成データ版 | — | — | decline | 合成データ |

**合計 526 GB 以上を、取得せずに落とした。**

## 効いた判定は2件

### 1. サーボモータ+ボールねじ(21.3 GB)

**機構としてはEPSに最も近い候補だった。**EPSのラックはボールねじをサーボモータで駆動する。
名前も "Modeling Health in Mechanisms with Typically **Intermittent** Operation" で、
**断続という語が入っている。**

**しかし配布ページを読むと「Simulinkで設計したサーボモータ**シミュレータ**の入出力と注釈の記録」である。**

- 実測ではない。**実機の挙動を立証できない**
- そして "intermittent operation" は**機械が間欠的に動く**という意味であり、
  **故障が出たり消えたりする**という意味ではない。**本研究が探しているものではない**

**取得していれば21.3 GBを費やしたうえで、この2点に気づいた。**

### 2. NASA Capacitor(5.0 GB)

**動作点は保持である**(10 V / 12 V / 14 V の固定水準)。
これまで失敗した3件(NASA MOSFET、インバータPMSM、NASA IGBT)と違い、**試験機がランプしていない。**

**それでも取得しない。**理由は動作点ではなく、**答えられる問いが無い**ことである
——[docs/224](224_current_conclusion.md) の残る空欄(ECU内部信号の観測床、検出確率)は、
コンデンサでは埋まらない。断続故障も含まない。

> **「良質だが、うちの問いに答えない」を判定できるようになった。**
> これまでは「良質そうだから取る」で取っていた。

## 断続故障は、三度目の探索でも見つからなかった

| 探索 | 日付 | 結果 |
|---|---|---|
| [docs/175](175_close_contact_question.md) | 2026-08-23 | 無し |
| [docs/214](214_dataset_reinventory_2026_08.md) | 2026-08-30 | 無し |
| **本文書** | **2026-08-30** | **無し** |

**「出たり消えたりする故障」を含む公開データは、依然として存在しない。**

## 積み残し(正直に書く)

**総覧論文([arXiv 2403.13694](https://arxiv.org/abs/2403.13694))の付録表が、3通りの方法で読めなかった。**
HTML版、PDF版、ar5iv版のいずれでも表が描画されない。

**[AGENTS.md](../AGENTS.md) の作法2は「棚卸しは総覧論文を起点にする」と定めているが、
本文書はその総覧を読めていない。**
今回の8件は個別の検索とリポジトリ一覧から拾ったものであり、**網羅性の保証は無い。**

**表が読める形で入手できたら、もう一度回す。**観測台帳へ。

> **解消(2026-08-31, [docs/242](242_survey_appendix_read.md))**: **取得時にローカル保存されていたPDFから読めた。**
> 110件中、intermittent/connector/contact/relay/solder/fretting はすべて **0件**。
> **ただし総覧自体に4件の穴があり(SOReDD・KAIST・comma・インバータ)、「0件」は不在の証明にならない。**

## Rule Check

- **1件もダウンロードしていない。**配布ページとReadmeのみで判定した
- **最も有望に見えた候補(ボールねじ)を落とした理由**を、機構の近さより先に書いた
- **動作点が良質でも落とす**という判定を初めて行い、その理由を書いた
- **総覧論文を読めていないこと**を、成果と同じ節に書いた。網羅性を主張しない

出典: PHM Society Data Repository / NASA PCoE / GitHub awesome-industrial-datasets(いずれも公開ページ)
