# Predictive Value ID Status Inventory

> Correction: この文書は、後続レビューで補正済みである。
> EPS内部状態、DTC、freeze frame、交換結果が見えないことを主Kill理由にしすぎていた。
> 最新判断は [docs/96_predictive_value_internal_fact_correction.md](96_predictive_value_internal_fact_correction.md) と [data/predictive_value_corrected_status.tsv](../data/predictive_value_corrected_status.tsv) を参照する。
> 修正後は、`PVC001`、`ULC008`、`ULC004`、`PVC004` を公開proxy価値の検証候補として残す。

## 結論

手持ちのPVC、ULC、KGL IDに、公開情報とKaggle proxyだけで継続深掘りするものは残さない。

一番可能性が残ったのは、EPSがいつ壊れるかを当てる話ではなく、車両や用途がEPSにとって厳しい使われ方に入りやすいかを先に分類する話だった。
しかし、公開proxyだけではEPS内部状態、DTC、freeze frame、extended data、assist state、limit state、交換結果、既存診断や既存評価との差分が見えない。

そのため、現時点では外販商品として進めない。
残すのは、EPSサプライヤ内で既存業務との差分を確認するサプライヤ内レビュー材料だけである。

最終判断の詳細は [docs/95_predictive_value_continue_final_decision.md](95_predictive_value_continue_final_decision.md) に置く。
ID別の作業表は [data/predictive_value_id_status_inventory.tsv](../data/predictive_value_id_status_inventory.tsv) と [data/predictive_value_continue_final_decisions.tsv](../data/predictive_value_continue_final_decisions.tsv) に置く。

## 何を判断しているか

判断しているのは、公開proxyでEPS故障、残寿命、交換時期を予測できるかではない。

判断しているのは、公開proxyから見える速度、操舵要求、stop-start、路面・振動、交通状態、通信異常が、EPSサプライヤの業務判断に使える先読み価値になるかである。

先読み価値とは、以下のいずれかに転記できることである。

1. 製品企画で、用途別のEPS価値説明に使える
2. 診断企画で、DTCやfreeze frameだけでは説明しにくい使用contextを補助できる
3. 品質改善で、field issueを使用条件別に読み直す入口になる
4. 評価企画で、既存評価がどのusage classを代表しているか確認できる
5. 顧客技術説明で、故障原因を断定せずに使用条件の可能性を説明できる

今回の最終判断は、「その可能性はあるが、公開proxyだけでは外販商品にできない」である。

## 市場需要

低速取り回し、駐車操作、荒れた路面、段差、stop-start、操舵感、音、振動、違和感は、ユーザやサービス現場にとって分かりやすい困りごとになりやすい。

EPSサプライヤ側では、それをすぐに故障原因や残寿命へ飛ばさず、使用条件のclassとして整理したい。
その整理ができれば、製品企画、診断企画、品質改善、評価企画が同じ言葉で議論できる。

## 未解決の痛み

現行の公開proxyでは、EPS内部状態は見えない。
DTC、freeze frame、assist state、limit state、motor current、temperature、交換結果も見えない。

一方で、速度、操舵要求、路面・振動、stop-start、運転状態のproxyはある。
この間を無理につなぐと、すぐに故障予測や原因断定になってしまう。

したがって、公開調査としてはここで止める。
次に進める場合は、外部調査の継続ではなく、EPSサプライヤ内のサプライヤ内レビューで既存業務との差分を確認する。

## ID Conclusions

### PVC

| ID | Status | Conclusion | Next |
|---|---|---|---|
| PVC001 | Final: internal review only / no external offer | 使用負荷classの先読みは公開proxyだけでは外販商品にしない | サプライヤ内レビューを行う場合だけ、ULC008の2枚sampleを製品企画・診断企画に見せる |
| PVC002 | Final: merged / closed | 操舵要求 x 路面・振動はPVC001内のULC004として閉じる | ULC004の補助材料としてだけ使う |
| PVC003 | Final: merged / closed | 都市/駐車場低速高操舵はULC008/ULC001へ統合 | ULC008の用途contextとしてだけ使う |
| PVC004 | Final: boundary material only / no product | 通信異常contextは診断信頼性・禁止主張の境界材料 | 診断企画が必要と言う場合だけ精緻化する |
| PVC005 | Final: out of current scope / archive | 評価時間予測は評価効率テーマ | 現本線では深掘りしない |
| PVC006 | Final: out of current scope / archive | 製造・EOLリスクscreeningは工程検査テーマ | 現本線では深掘りしない |
| PVC007 | Final: companion only / no active item | 熱・EV実走行contextは補助列 | 必要時だけULC009に使う |

### ULC

| ID | Status | Conclusion | Next |
|---|---|---|---|
| ULC001 | Final: support input only | 低速高操舵はULC008の根拠入力 | 単独深掘りしない |
| ULC002 | Final: merged / closed | 据え切りに近い操舵はULC008へ統合 | 独立させない |
| ULC003 | Final: merged / closed | stop-start + 反復操舵は都市/渋滞context | ULC001/008に付ける |
| ULC004 | Final: internal review sample only | 荒れた路面 + 操舵はサプライヤ内レビューsampleのみ | 品質改善・評価企画が既存業務との差分を示す場合だけ再開 |
| ULC005 | Final: merged / closed | 段差/凹凸 + 操舵はULC004/008へ統合 | 独立させない |
| ULC006 | Final: support input only | 連続振動路 + 操舵はULC004の補助入力 | 単独深掘りしない |
| ULC007 | Final: archive / risky | 荒い運転 + 荒れた路面は誤解リスクが高い | 当面深掘りしない |
| ULC008 | Final: internal review sample only | 駐車場 + 低速 + 大舵角 + 凹凸は最初のサプライヤ内レビューsampleのみ | 製品企画と診断企画の両方が具体用途を示す場合だけ再開 |
| ULC009 | Final: companion only / no active item | 長時間都市走行 + 反復操舵は補助列 | 単独テーマにしない |

### KGL

| ID | Status | Conclusion | Next |
|---|---|---|---|
| KGL001 | Final: archive input / out of current scope | 製造・EOL予測。現テーマ外 | 製造枝を再開する場合だけ見る |
| KGL002 | Final: archive input / out of current scope | 評価時間予測。現テーマ外 | 評価効率枝を再開する場合だけ見る |
| KGL003 | Final: input only | 速度、stop-start、運転状態proxy | ULC001/003/008の入力に限る |
| KGL004 | Final: boundary input only | CAN攻撃/異常境界 | KGL011と束ねてPVC004へ |
| KGL005 | Final: input only | 操舵要求proxy | ULC001/004/008の入力に限る |
| KGL006 | Final: input only | 路面・振動proxy | ULC004の入力に限る |
| KGL007 | Final: input only | traffic / driving style / road condition | ULC003/004 contextに限る |
| KGL008 | Final: input only | 凹凸・段差proxy | ULC004/008の入力に限る |
| KGL009 | Final: schema only | feature schemaだけ借りる | 実証扱いしない |
| KGL010 | Final: schema only | driver behavior schemaだけ借りる | 実証扱いしない |
| KGL011 | Final: boundary input only | steering spoofing / DoS境界 | KGL004と束ねてPVC004へ |
| KGL012 | Final: companion only / no active item | thermal / trip context補助 | EPS thermal推定には使わない |

## 次にやるなら

次にやるべきことは、Kaggleや公開情報をさらに掘ることではない。

次にやるなら、サプライヤ内レビューで次の4問を確認する。

1. 製品企画は、`ULC008` を用途別のEPS価値説明に使えるか
2. 診断企画は、`ULC008` を既存DTC / freeze frame / extended dataでは粗い使用context説明に使えるか
3. 品質改善または評価企画は、`ULC004` を既存NVH、耐久、評価scenarioとは違う切り口として使えるか
4. 診断企画またはサイバー担当は、`PVC004` を通信異常時の診断信頼性境界として使えるか

この4問に具体的な使い道が出なければ、このブランチは完全Archiveでよい。

## CoVe

| 検証質問 | 回答 | Confidence | 反映 |
|---|---|---:|---|
| 市場需要から始まっているか | Yes。低速取り回し、駐車、凹凸、操舵感、違和感を、原因断定せず整理したい需要から始めている。 | Medium | PVC001/ULC008を最後まで検証した |
| 故障予測に戻っていないか | Yes。故障、残寿命、交換時期、保証費、安全性はすべて禁止主張へ置いた。 | High | 外販Stop、サプライヤ内レビュー材料のみとした |
| EPSサプライヤの部署に転記できるか | Partly。製品企画・診断企画は可能性があるが未証明。品質改善・評価企画は二次。 | Low-Medium | サプライヤ内レビュー再開条件にした |
| 既存業務の言い換えではないか | Unknown。既存DTC/freeze frame、既存評価、既存RFQ回答との重複は未確認。 | Low | Kill gateとして残した |
| OEM保証DBやfleet dataに依存していないか | 現時点では依存しない形にした。ただし、その分外販価値は弱くなった。 | Medium | 外販商品化を止めた |
| 次の判断が可能か | Yes。サプライヤ内レビュー4問で、完全Archiveかサプライヤ内限定再開かを切れる。 | Medium | 次アクションをサプライヤ内レビュー確認にした |

## EPSサプライヤとしての言い方

言ってよいこと:

> 公開proxyだけではEPS内部状態や残寿命は分からない。ただし、低速、大舵角、路面外乱、stop-start、凹凸、通信異常contextを分けると、EPSサプライヤ内の製品企画や診断企画で使える可能性がある。現時点では商品ではなく、既存業務との差分を確認するサプライヤ内レビュー材料である。

まだ言ってはいけないこと:

> 使用負荷classからEPS故障、残寿命、交換時期、保証費削減、安全性が分かる。

> 駐車操作、低速高操舵、荒れた路面、通信異常がEPS故障原因である。

> 公開proxyからEPS内部stress、thermal limit、assist limitation、DTC不足を断定できる。
