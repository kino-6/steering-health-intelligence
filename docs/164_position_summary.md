# 164. 現在地の1枚まとめ(2026-08-23)

## 一言で

**EPSの「故障と判定される手前の兆候」は、部品内部でなら明瞭に観測でき、外部からは原理的に見えない。
観測の基準を書けるのは出荷前のEOL検査を持つ部品サプライヤだけである。
ただし「兆候が故障に先行する」ことは、EPS内部信号については未証明のまま残っている。**

## やること(製品の形)

| 工程 | 内容 | 根拠 |
|---|---|---|
| ① 出荷時(EOL) | 既存のEOL検査に、その個体の健全signatureを記録してECUへ書き込む工程を足す | [docs/163](163_per_unit_baselining.md) |
| ② 運用中(車載) | その個体**自身の出荷時基準**からの逸脱を監視。特徴量ごとに窓長とk-of-N判定則を変える | [docs/155](155_window_recurrence_verification.md) |
| ③ 報告 | fault未満の状態説明としてOEMへ。SOTIF運用フェーズのEooC仮定の市場検証として乗る | [docs/121](121_steering_predictive_diagnostics_power_monitor_case.md), [docs/153](153_sotif_eooc_assumption_sheet.md) |

売り方は [docs/146](146_business_framework_and_roadmap.md) 第1層のまま(RFQ差別化 + 診断コンテンツNRE)。
**NREの実体が具体化した**: program固有の閾値較正 + EOL指紋工程の設計。

## 証明できたこと

| # | 主張 | 数字 | 出典 |
|---|---|---|---|
| 1 | **兆候は掴める** | 巻線3.35%短絡で同一個体のゆらぎの**15倍**、21.69%で31倍 | [docs/162](162_pmsm_model_validation_results.md) |
| 2 | **仕組みは作れる** | 60秒の走行logから応答遅れ0.3s・ゲイン0.10・バイアス0.10を90%検出(誤検出3.6%)。設計則は4車種で一致 | [docs/144](144_synthetic_sensitivity_results.md), [docs/155](155_window_recurrence_verification.md) |
| 3 | **外からは見えない**(4経路) | 苦情ベース識別は不成立(precision 0.48/recall 0.26)／見逃しcohortの苦情は中央値1件／車検不合格の99%はリンケージでEPS系は0.1%／制御器が打ち消し巻線1/5短絡でも不平衡は4倍止まり | [docs/143](143_recall_detection_results_v2.md), [156](156_train_era_miss_structure.md), [157](157_mode_split_and_corsa_correction.md), [162](162_pmsm_model_validation_results.md) |
| 4 | **横断比較は成立しない**(5経路) | 同じ健全機でもセットアップ差でUが2〜8倍動く。帰属できるのは同一個体の時間変化だけ | [docs/147](147_multiplatform_and_variant_verification.md), [162](162_pmsm_model_validation_results.md) |
| 5 | **他社には構成できない** | 個体基準を書ける時点が出荷前にしかない。OEM基盤は出荷済み車両からしか観測できない | [docs/163](163_per_unit_baselining.md) |
| 6 | **閾値未満の観察には予測情報が乗る**(一般命題) | 英国車検1,700万個体で、兆候のみ→翌年不合格が最大24.1倍 | [docs/150](150_advisory_precedence_verification.md) |

## 証明できていないこと

| # | 未証明 | なぜ埋まらないか | 公開データで埋まるか |
|---|---|---|---|
| ~~**A**~~ | ~~兆候→故障の橋~~ → **機構レベルで証明済**([docs/167](167_precursor_results_v2.md))。パワーMOSFET6個体で、故障の1〜2段階前に健全期ノイズの**20〜300倍**の逸脱。残るのは**EPSへの転移** | 実部品・実故障・同一個体の連続追跡 | 済 |
| ~~**B**~~ | ~~個体基準の有効期間~~ → **測定済**([docs/167](167_precursor_results_v2.md))。**不安定さの正体は経年ではなく温度**。温度を個体ごとに1次で除けば健全期の基準は **0.09〜0.75%** に収まる | 6デバイスの連続追跡 | 済 |

**AとBは2026-08-23に埋まった([docs/167](167_precursor_results_v2.md))。** ただし埋まったのは**fault前駆**であり、**SOTIF(機能不足)ではない**([docs/169](169_sotif_link_check.md))。

| 残る未証明 | 内容 |
|---|---|
| **A''** | **EPSコネクタのfretting劣化は、機能影響が出る前に単調な発生率の上昇として観測できるか**([docs/168](168_transfer_reduces_to_spec.md)) |
| **S** | **パラメータのずれが「機能不足」に翻訳できるか**([docs/169](169_sotif_link_check.md))。ここが埋まらないとSOTIFの根拠にならない |

転移(A')の大部分は **gain / offset の違いであり、製品規格の決めごとに還元される**([docs/168](168_transfer_reduces_to_spec.md))。
同一型番6個体ですら温度係数が40%ばらつく中で6/6成立したため、手法はgainのばらつきに対して既に頑健である。
還元されないのは「標的故障族(fretting=断続的)が単調な観測量を生むか」の1点で、
その場合の単調量は水準ではなく**発生率**になる——設計は既に recurrence を含んでおり、アーキテクチャは変わらない。

### AとBを埋めうる経路(2026-08-23 発見、[docs/159](159_public_dataset_reinventory.md) の棚卸し手順で)

**NASA PCoE: MOSFET Thermal Overstress Aging**(DS015、パブリックドメイン)

- パワーMOSFET **6個体を健全から故障まで連続測定した run-to-failure データ**
- **ON抵抗の上昇が「故障の前駆指標(precursor)」として使われている** — 閾値未満の電気的兆候が故障に先行することの、実部品・実故障での測定そのもの
- EPSインバータ電力段と**同じ部品クラス**。しかも劣化機構(熱ストレスによるdie-attach劣化)は、SPD008の標的故障族(電源・熱context)と同型
- 6個体あるため、**個体ごとの基準が故障までにどれだけドリフトするか**(B)も同じデータで測れる

**できないこと**: これはディスクリート部品の熱ストレス試験台であり、車載EPSではない。
言えるのは「**部品内部の電気量に、故障に先行する情報が乗る**」という機構レベルまでで、
EPSへの転移は別の問いとして残る。それでも [docs/150](150_advisory_precedence_verification.md) の24.1倍(検査員の目視観察)より、
主張したい対象に**一段近い**。

### 「EOL検査に必要な量が記録されているか」は問いではない

一度この項目を未証明として挙げたが、**誤りだった**([AGENTS.md](../AGENTS.md) 2条・5条・7条違反)。外から組み立てる。

- **EOL検査は出荷可否を決める工程である。** EPSを通電してアシストを出し、電流・トルク・応答を測らずに合否は出せない。
  「測っているか」は構造上問う必要がない
- 実際の論点は**粒度と保存期間**であり、それはprogram依存の設計事項である
- そして**それは調べる対象ではなく、要求する対象である**。第1層はRFQ差別化 + 診断コンテンツNREであり、
  **EOL指紋工程の仕様は売り物の中身**である。既存工程に何が記録されているかを前提条件にしない
- 桁感: EOL指紋は既存測定値の要約を数十バイト書き込むだけであり、タクトタイムを増やさない。
  追加ラインも新規センサも要らない

したがってCは未証明項目ではなく、**設計項目**である。以後この話題を未解決として扱わない。

## Kill済み(蒸し返さない)

- 故障予測・RUL・交換時期予告 — [docs/143](143_recall_detection_results_v2.md) で事前登録基準に未達、確定
- SbW汎用安全支援の外販 — [docs/160](160_asset_scope_expansion.md) でKill維持を確認(観測資産の範囲拡張は別物として整理)
- Coverage Benchmark / SOVD基盤支援 / エンドユーザ通知

## 資産範囲(2026-08-22 拡張)

EPSアシストモータ + ECU / SbW road wheel actuator / SbW feedback actuator は**すべて三相PMSM**で、
内部電子観測が届く。ギアAssy中核は一部のみ、**外側タイロッドエンドは届かない**([docs/160](160_asset_scope_expansion.md))。

## この研究が嘘をつけない構造

**「公開情報のみ」は面倒回避ではなく、検証可能性の装置である**([AGENTS.md](../AGENTS.md) 1条)。
内部情報を許せば「確認できないが内部ではこうなっている」で任意の主張を通せてしまい、
第三者だけでなく本人も監査できなくなる。**検証できない主張は、この研究では存在しないのと同じ**である。

上表のすべての数字は、次の3つで外部から再導出できる。

| 装置 | 中身 |
|---|---|
| 出典 | [SOURCES.md](../SOURCES.md) — 全ソースのURL・ライセンス・取得日・派生ファイル対応 |
| 再現 | [scripts/](../scripts/) — 生データは再配布せず、取得と計算のコードを置く |
| 事前登録 | [docs/140](140_recall_detection_protocol.md), [142](142_recall_detection_protocol_v2.md), [161](161_pmsm_model_validation_protocol.md) — 見る前に基準を固定し、不成立をそのまま記録する |

この構造があるから、下の「訂正したもの」を正直に積める。訂正が積めることが、装置が働いている証拠である。

## 誤りとして訂正したもの(記録)

1. [docs/151](151_high_rate_model_crosscheck.md) の「すべて消化した」→ 未消化3件が残っていた([docs/154](154_open_items_after_exhaustion_claim.md))
2. [docs/151](151_high_rate_model_crosscheck.md) のCorsa答え合わせ → モード水準で誤帰属([docs/157](157_mode_split_and_corsa_correction.md))
3. [docs/155](155_window_recurrence_verification.md)/[docs/158](158_sotif_eooc_monitor_demo.md) の較正設計 → 母集団基準は誤り。個体基準が正しい([docs/163](163_per_unit_baselining.md))
4. [docs/158](158_sotif_eooc_monitor_demo.md) を「Demo達成」と報告 → Demoは結論まで回すこと([AGENTS.md](../AGENTS.md) 4条)
5. 「実故障データは公開されていない」→ 操舵系としてはない。モータ層にはある([docs/159](159_public_dataset_reinventory.md))
6. 「EOL検査に必要な量が記録されているか」を未証明項目として再掲 → **内部情報を代替案なしに要求していた**。EOL検査は出荷可否を決める工程であり測定は構造上必須。論点は粒度と保存であり、それは調べる対象ではなく**RFQで要求する設計項目**である(2026-08-23 ユーザ指摘)
