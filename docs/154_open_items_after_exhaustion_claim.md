# 154. 「すべて消化した」の棚卸し(未消化項目の確定)

## 判断

**[docs/151](151_high_rate_model_crosscheck.md) の「公開データで能動的に実行できる検証はすべて消化した」は誤りだった。未消化が3件残っていた。**

> **追記(2026-08-22)**: 3件すべて実施済み。結果は [docs/155](155_window_recurrence_verification.md)(窓長・再発)、[docs/156](156_train_era_miss_structure.md)(見逃し構造)、[docs/157](157_mode_split_and_corsa_correction.md)(モード照合)。**うち1件は既存結論の訂正を伴った**——docs/157 は docs/151 の Corsa 答え合わせを誤帰属と判定した。「残作業を放置すると、誤った結論も一緒に残る」ことの実例である。

うち2件は、リポジトリ自身が残作業として明示的に登録したまま実施されなかったものである。全文検査(未実施 / 未照合 / 未検証 / 残作業 / 未着手 / 保留 の全出現)で確定した。

| # | 未消化項目 | どこで登録されたか | 実施可否 | 停止ルールへの抵触 |
|---|---|---|---|---|
| 1 | ~~**学習era内の見逃し構造分析**~~ → **実施済([docs/156](156_train_era_miss_structure.md))** | [docs/147:31](147_multiplatform_and_variant_verification.md)、[docs/148:36](148_dvsa_mot_denominator_verification.md)が「残る唯一の机上作業(未)」と明記 | **可能**。データ在り、学習era(2013-2018)のみ使用 | **抵触しない**([docs/143](143_recall_detection_results_v2.md)の停止ルールはテストeraへの3回目アクセス禁止。本件はテストeraに触れない) |
| 2 | ~~**Fiat 500X / Jeep Renegade の照合**~~ → **実施済([docs/157](157_mode_split_and_corsa_correction.md))** | [docs/151:12](151_high_rate_model_crosscheck.md)が「今回照合していない(推測で埋めない)」と明記 | **可能**。公開の不具合記録との突き合わせ | 抵触しない |
| 3 | ~~**窓長・再発カウントによる感度向上の定量**~~ → **実施済([docs/155](155_window_recurrence_verification.md))** | [docs/144:29](144_synthetic_sensitivity_results.md)が「窓を長くする/再発を数えると感度は上がる方向(未検証)」と記載 | **可能**。既存キャッシュ(comma.ai)とスクリプトで完結 | 抵触しない |

**閉じてよい項目**(誤って未消化に見えるが実施済み):

- [docs/143:43](143_recall_detection_results_v2.md)「モデルB(波形側の合成劣化感度)— 未着手のまま残存」→ [docs/144](144_synthetic_sensitivity_results.md) で実施済み
- [docs/143:44](143_recall_detection_results_v2.md)「DVSA MOT(分母付き)による相互検証 — 保留のまま」→ [docs/148](148_dvsa_mot_denominator_verification.md) で実施済み
- [docs/141:56](141_recall_detection_results.md)「EPS系campaign限定のサブセット評価(未実施)」→ [docs/143](143_recall_detection_results_v2.md) で実施済み(PR-AUC 0.180)

## なぜ取りこぼしたか

構造的な理由が1つある。

**残作業の登録場所と、完了宣言の場所が別のドキュメントだった。** [docs/147](147_multiplatform_and_variant_verification.md) と [docs/148](148_dvsa_mot_denominator_verification.md) が残作業を各自の末尾に書き、[docs/151](151_high_rate_model_crosscheck.md) は自分の軸(軸2)の完了をもって全体の完了を宣言した。**横断の棚卸しを一度も通していない。**

したがって是正は「今回の3件を消す」だけでは足りない。**完了宣言の前に全文検査を通す**という手順が要る。本ドキュメントがその1回目である。

## 各項目の中身と事前登録案

実施する場合は、このリポジトリの作法([docs/140](140_recall_detection_protocol.md), [docs/142](142_recall_detection_protocol_v2.md))に従い、**実行前に何を見るかを固定してからコミットする**。以下は事前登録の案であり、まだ実行していない。

### 項目1: 学習era内の見逃し構造分析

問い: 学習era(2013-2018)で、モデルが**捕らえた陽性cohortと見逃した陽性cohortを構造的に分けるものは何か**。

- 使うもの: `scripts/recall_detection_model.py` の学習era部分のみ。凍結運用点(threshold=0.3105、train recall=0.48)を変更しない
- **テストera(2019-2024)には一切触れない**。これが停止ルールを守る条件
- 見る軸(実行前に固定): 見逃しcohortの ①苦情件数 ②操舵系比率 ③車齢 ④campaign種別(ELECTRIC/ASSIST か否か) ⑤リコール届出からの苦情の立ち上がり時期
- 期待される結論の形: [docs/145:31](145_final_conclusions_and_interpretations.md) が定性的に述べた「見逃しの中にはユーザが苦情を書く前にサプライヤ内で見つかったリコールが含まれる」を、**定量で裏づけるか否定するか**
- これは Kill 済みモデルの復活ではない。[docs/143](143_recall_detection_results_v2.md) の不成立判定は動かさない。見るのは「なぜ原理的に見えないのか」であり、性能改善ではない

### 項目2: Fiat 500X / Jeep Renegade の照合

問い: 英国車検で高率だった 500X / Renegade(8.8%前後、同一プラットフォーム対)は、[docs/151](151_high_rate_model_crosscheck.md) の①欠陥ファミリー型と②用途摩耗型のどちらか。

- 3例目までの答え合わせ(Ford / GM / Corsa)と同じ手順で、公開の不具合記録・リコール・整備情報と突き合わせる
- 意味: 4例目が成立すれば群監視の答え合わせが補強される。**どちらの型でもない/判別できない場合はそう記録する**——それも群監視の限界の記録として価値がある

### 項目3: 窓長・再発カウントによる感度向上の定量

問い: 60秒窓・単発判定で得た検出限界(遅れ0.4s / ゲイン15%)は、**窓を延ばす・再発を数えると実際どこまで下がるか**。

- 使うもの: 既存キャッシュ(`.public_log_cache/`)と `scripts/steering_synthetic_sensitivity.py`
- **[docs/153](153_sotif_eooc_assumption_sheet.md) のEooC仮定シートに直接効く**。現在 [EOOC009](../data/sotif_eooc_assumption_sheet.tsv) は「窓を延ばす・再発を数えると感度は上がる方向(未検証)」と書いてある。OEMへ差し出す仮定シートに未検証の見込みを書くのは弱い。数値化すれば EOOC006 の宣言粒度がそのまま強くなる
- 注意: [docs/144](144_synthetic_sensitivity_results.md) の「バイアスは最小試験量でも100%検出=路面カントでも発火する」という結論があるため、感度を上げる方向の検証は**誤検出率とセットでしか報告できない**

## 優先順位の判断

**項目3 > 項目1 > 項目2** を推奨する。

- 項目3は、いま作った [docs/153](153_sotif_eooc_assumption_sheet.md) の欠けている数値をそのまま埋める。成果物に直結する
- 項目1は、リポジトリ自身が「残る唯一の机上作業」と呼んだもの。誠実性の観点で閉じる価値があるが、Kill済みモデルの周辺であり事業判断は動かさない
- 項目2は、答え合わせの4例目。既存結論(3例成立)を補強するだけで、判断を変える見込みは小さい

## Rule Check

適用したルール: `Natural Language First` / `Mandatory Rule Check Before Stop / Kill / Archive`

- 「すべて消化した」という過大な宣言を、実データ(全文検査)で訂正した。宣言を守るために事実を曲げていない
- 3件はいずれも公開情報の範囲で完結し、内部資料を必要としない。内部依存の項目(KQ1、[docs/123](123_steering_predictive_diagnostics_power_monitor_program_question_sheet.md)の質問シート)は本棚卸しの対象外であり、次アクションにも置かない
- 項目1は Kill 済み仮説の再提案ではないことを明記した。性能改善ではなく限界の構造解明である
- 事前登録案の段階で止め、実行していない。実行する場合は本ドキュメントをコミットしてから行う
