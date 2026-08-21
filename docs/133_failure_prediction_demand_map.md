# Failure Prediction Demand Map

## 結論

「故障予測の需要は誰にあり、どの形で欲しがられ、どの席が空いているか」を、リポジトリ内の既往調査(docs/75、79、98、103、105ほか)と最新の公開市場情報を統合して1枚にした。

全体の答えは次である。

> **需要は全セグメントで実在する。しかし「車両レベルのデータで予測を売る」席は、fleet側もOEM側も既に埋まっている。**
> fleet向けはUptake、Questar(Geotab/Webfleet経由)、Stratio、Intanglesらが故障予兆・修理推奨・放置コスト見積りまで商品化済み。OEM品質/保証向けはViaduct等が「保証請求の数週間前に新興不具合を検知する」商品を持つ。
> 空いている席は2つだけ:
> **(1) 部品内部のDTC未満信号とその意味づけ**(第1ラウンド=SPDで検証済み。既存プラットフォームは車両レベルのDTC/テレメトリから予測するため、部品内部の閾値未満contextには構造的に届かない)
> **(2) 群レベルの公開データによる故障リスク傾向**(未検証。個車RULではなく「この車種・車齢の操舵系は市場でどう壊れてきたか」という曲線。公開データだけで作れる可能性があり、フェーズB/Cの対象)

詳細表は [data/failure_prediction_demand_map.tsv](../data/failure_prediction_demand_map.tsv) に置く。

## 何を判断しているか

「故障予測」という言葉を分解している。誰が(買い手)、何のために(業務)、どの粒度で(個車RUL / 群傾向 / 入庫優先度 / 状態説明)、どのデータで(所有者は誰か)。
この分解をせずに「故障予測は売れるか」と問うと、答えが「個車RULはKill」で止まってしまう。目的地(需要調査→データ収集→Demo)に対しては、粒度別に席の空き状況を見る必要がある。

## Rule Check

今回の判断では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`: セグメント別の実需要(downtime削減、保証費の早期把握、診断時間短縮)から始めている
2. `Natural Language First`: 結論を平文で先に述べた
3. `EPS Supplier Lens`: 各セグメントで「EPSサプライヤの入り口」列を持つ
4. `Kaggle / Public Proxy Predictive Value Rule`: 個車RUL・交換時期・保証費削減断定を売り物にしない。群レベル傾向は「市場がどう壊れてきたか」の記述であり、個車の未来の断定ではない
5. 既往のKill判断(fleet外販、OEM remote diagnostics説明レイヤー)を名前を変えて再提案していないか → 席が埋まっている事実の再確認として整合。空席(1)(2)は既往Killの対象外

## 需要マップ

| セグメント | 欲しい予測の形 / 粒度 | 必要データと所有者 | 既存プレイヤー(公開確認済み) | EPSサプライヤの入り口 | 公開データでDemo可? | 判定 |
|---|---|---|---|---|---|---|
| **Fleet運行**(商用車群・AV) | 個車の故障予兆アラート、入庫優先度、修理推奨、放置コスト。downtime削減が目的 | テレメトリ+DTC+整備履歴(fleet/OEM/platform所有) | Uptake、Questar(Geotab Marketplace / Webfleet提携)、Stratio、Intangles | 直接販売はKill済み(docs/75)。入り口は既存platformへの**部品側semantics提供**のみ | 不可(データ非公開) | 席は埋まっている。再挑戦しない |
| **OEM品質/保証** | 群レベルの新興不具合早期検知(build cohort別故障率、請求前の予兆)、保証引当の精度 | 車両稼働データ+DTC発生率+保証請求(OEM所有) | Viaduct(DTC発生率+使用データで請求前に検知)、warranty analytics各社 | 車両レベルは埋まっている。**部品内部のDTC未満信号**は既存商品の入力に存在しない=空席(1) | **一部可**: 公開苦情/リコール/車検データで群レベル傾向の形は再現できる | 空席(1)は第1ラウンドで検証済み(限定Proceed) |
| **整備チェーン/service** | 診断時間短縮、fault criticality、次に読む手順、部品事前手配 | DTC+freeze frame+修理結果feedback(OEM/service所有) | OEM remote diagnostics、Bosch cloud diagnostics等 | 説明レイヤー外販はKill済み(docs/archive)。入り口は状態説明(SPD payload)のservice向け言い回しのみ | 不可 | 既存判断維持 |
| **保険/延長保証** | 車齢×車種×使用条件の故障リスク(価格付け用の群統計) | 請求データ(保険側所有)+車両データ | (本Repoでは初期対象外として除外済み、docs/75) | なし(対象外維持)。ただし空席(2)の群曲線は形として同種 | 形は可 | 対象外維持 |
| **Vehicle health基盤** | end-to-endのvehicle health ecosystem | 全車両データ | Bosch(Uptake買収、C-Hub/FleetME)、ZF Vehicle Health、Nexteer MotionIQ | 基盤を作る/売るはKill済み。入り口は**部品側contribution**(SPD payload)=空席(1) | 部分的に可(デモ済み) | 第1ラウンドで検証済み |
| **EPSサプライヤ内部**(品質改善・製品企画) | 群レベルのfield傾向(サプライヤ搭載車種の操舵系がどの車齢・条件で壊れてきたか)、設計・評価へのfeedback | **公開データで一部代替可能**(苦情・リコール・車検統計)+内部の保証データ | 各社内製(体系商品なし) | **サプライヤ業務なので入り口不要**。公開データの群曲線はここの道具になる=空席(2) | **可** | **未検証。フェーズB/Cの本命** |

## 統合して見えた構図

```
予測の粒度            席の状況
─────────────────────────────────────────
個車RUL/交換時期     × 誰にとってもKill(データ所在+禁止主張)
個車の故障予兆       × fleet/OEM側で商品化済み(Uptake/Questar/Viaduct)
入庫優先度/修理推奨   × 同上
─────────────────────────────────────────
部品内部のDTC未満    ○ 空席(1)。第1ラウンド(SPD)で検証済み=限定Proceed
群レベルの故障傾向    ○ 空席(2)。未検証。公開データで作れる可能性 ← フェーズB/C
```

空席(2)の需要の言い方(自然言語):

> 「この車種・この車齢・この地域の操舵系は、市場で実際にどんなペースで、どんな壊れ方をしてきたか」を曲線で持ちたい。
> 使い道は、EPSサプライヤ内部なら次期設計・評価の重点決め、RFQ回答の裏付け、品質改善の優先度。個車の未来は断定しない。

## フェーズB(データ当たり付け)の候補

空席(2)を公開データで作れるかの確認対象。次で検証する。

1. **NHTSA苦情データベース(公開)**: 車種×年式×部品カテゴリ(steering)の苦情時系列。群レベルの「苦情ハザード曲線」が作れるか
2. **NHTSAリコール/ODI調査データ(公開)**: 故障モードのラベル付き実例(第1ラウンドで精読済みの文書群を定量側から使い直す)
3. **英国DVSA MOT車検データ(公開)**: 年次車検の不合格項目に操舵系カテゴリがある。車齢×車種×操舵系不合格率という、苦情より客観的な群曲線の候補。**要確認**(データ粒度と操舵項目の分類)
4. 既存のKaggle/proxy資産(commaSteeringControl等): 使用条件側の補完として再利用可能か

判定条件: 上記から「車齢に対する操舵系不具合率の曲線」が1本でも誠実に引けるなら、フェーズC(Demo v2)へ進む。引けなければ、空席(2)は公開データでは埋まらないと記録して区切る。

## 言ってはいけないこと(このマップの範囲でも変わらず)

個車のRUL・交換時期・故障日、安全保証、保証費削減の断定、root cause断定、特定OEM/車種の設計優劣の断定。
群曲線は「市場で観測された過去の記述」であり、個車の未来の予測として売らない。

## 次の作業

1. フェーズB: 上記データ候補1〜3の実在・粒度・取得可否を確認する(公開情報のみ)
2. 取得可能なら、まず1車種系列で「車齢×操舵系不具合率」曲線を試作し、誠実に引けるかを見る
3. 引けたらフェーズC: Demo v2(群レベル操舵系リスク曲線)を `scripts/` + `generated/` に実装する

## Sources

市場側の公開確認:

- [Geotab: Best Predictive Fleet Maintenance Tools 2026](https://www.geotab.com/blog/predictive-fleet-maintenance-tools/)
- [Questar on Geotab Marketplace(Heavy Duty Trucking)](https://www.truckinginfo.com/news/questar-predictive-fleet-health-platform-now-available-through-geotab-marketplace)
- [Webfleet × Questar 提携(Bridgestone EMEA)](https://press.bridgestone-emea.com/webfleet-and-questar-launch-pioneering-ai-powered-predictive-maintenance-solution/)
- [Stratio](https://stratioautomotive.com/) / [Uptake Fleet](https://uptake.com/subject-matter/fleet/) / [Intangles](https://www.intangles.ai/blog/fleet-predictive-maintenance-in-fleet-management-explained-2026-guide/)
- [Viaduct: warranty data analysis](https://www.viaduct.ai/blog/the-top-3-pitfalls-to-avoid-when-analyzing-warranty-data)

リポジトリ内の既往結論: docs/75、79、98、103、105、およびarchive(motion health / oem remote diagnostics)。
