# SPD008 Payload Replay Demo

## 結論

公開文書に記録された実在の3ケースを、SPD008の最小payload([docs/122](122_steering_predictive_diagnostics_power_monitor_payload_sample.md))で**再演**する動くデモを作成した。

デモが見せるのは次の対比である。

| ケース | 実務が持っていた判断材料(公開文書) | 再演: その場で出せた状態説明 |
|---|---|---|
| GM 17-NA-158(依存signal無効) | steering gearに残ったcode。gearが犯人に見え、直らない交換が連鎖 | 「EPSは依存signal(冷却水温)の無効を観測。補償機能が停止。外部ECU原因の断定でもgear整備判断でもない。先に依存元を確認」 |
| Ford SSM 49530(始動時電圧8V未満) | 部品内部故障に見えるcode(U3000:96)。PSCM交換に向かいやすい | 「EPSは始動時にしきい値未満の供給電圧を観測。その間assist使用不能。モジュールやバッテリーの整備判断ではない」 |
| Ford 15S18(DTCなしの断続喪失) | 「DTC有無」という1bitのみ。DTCなしは対象外へ | 「故障確定未満の過渡的乱れが、アシスト途切れ近傍でkey cycleをまたぎ再発したことを観測」 |

さらに、**境界ガード**を実装した。
payloadの全fieldと状態説明文は禁止主張パターン(原因断定、交換判断、無罪主張、RUL、安全保証、保証費、故障予測)を機械的に検査され、違反があれば出力自体が拒否される。
デモでは各ケースに「安直な言い方」の例(『原因はバッテリー』『EPSは悪くない』『今すぐgearを交換』)を与え、**3件とも拒否されること**を実行結果として確認した。

- 実行: `python3 scripts/spd008_payload_replay.py`
- 出力: [generated/spd008_payload_replay.html](../generated/spd008_payload_replay.html) / [data/spd008_payload_replay_cases.tsv](../data/spd008_payload_replay_cases.tsv)

## 何を判断しているか

このデモは価値の証明ではない。判断済みの結論([docs/129](129_steering_predictive_diagnostics_public_case_crosscheck.md)、[docs/130](130_steering_predictive_diagnostics_comm_validity_public_crosscheck.md))を、**見せられる形**にしたものである。

見せたい相手と目的:

1. 診断企画・品質改善・顧客技術説明: 「状態説明」という売り物の具体的な形(field構成、言える範囲、言えない範囲)を1画面で見せる
2. 安全・法務系の懸念に対して: 禁止主張が設計レベルで拒否されること(境界ガード)を動作で見せる
3. 将来のOEM/vehicle health接続の議論: payloadのJSON形をそのまま叩き台にする

## Rule Check

今回の作業では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`: デモの各ケースは公式文書に記録された実在の痛み(誤交換・対象外放置・空振り修理)から始まる
2. `Natural Language First`: 各ケースの状態説明は日本語の平文を先に置いた
3. `EPS Supplier Lens`: 出力はEPS componentの観測に限定し、外部原因断定・整備判断を境界ガードで拒否する
4. `Steering Predictive Diagnostics Value Rule`: デモは副次artifactであり、本体は状態説明価値。診断読み順は recommended_read という1 fieldに留めた
5. 禁止主張: ガードのパターン表そのものが禁止主張リストの実装である
6. 公開情報のみ使用。合成データですらなく、公開文書に書かれた事実の再構成に限定した

## 設計上の注意(正直に)

1. **再演は「後知恵」である**: 各ケースの原因は今では公知だが、runtimeのEPSは原因を知らない。だからこそpayloadは「観測+近接+境界」だけを言い、原因に触れない設計にしてある。再演の正しさは「当時これが出せたら切り分けが速かったか」であり、「原因を当てられたか」ではない
2. **retained_fieldsは仮置き**: 実車で本当にこのfieldが取れるかは、実行段階(docs/123質問シート)の確認事項のまま
3. **境界ガードは正規表現の見本**: 実装の主張は「この種のガードが設計に組み込める」ことであり、このパターン表が完全だという主張ではない

## 次の作業

1. 案B(固定スコープassessmentの商品仕様化)に進む場合、このデモのHTMLを「成果物サンプル」として仕様書に添付する
2. デモへのフィードバック(fieldの過不足、状態説明文の言い回し)が出たら、docs/122のpayload定義に反映して両方を更新する

## Sources

デモ内の事実は、docs/129-130で精読済みの次の公開文書のみに基づく。

- [GM Service Bulletin 17-NA-158](https://static.nhtsa.gov/odi/tsbs/2017/MC-10137654-9999.pdf)
- [Ford SSM 49530](https://static.nhtsa.gov/odi/tsbs/2021/MC-10187919-0001.pdf)
- [Ford Safety Recall 15S18 dealer letter](https://static.nhtsa.gov/odi/rcl/2015/RCMN-15V340-8835.pdf)
