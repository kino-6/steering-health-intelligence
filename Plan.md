# Plan: Steering Predictive Diagnostics 次アクション

作成日: 2026-07-06 / 区切り更新: 2026-07-07
前提ブランチ: `research/bosch-motion-domain-ai`

## このリポジトリの目的地(2026-07-07 ユーザ確認)

> **故障予測の需要調査、および必要ならデータ収集、Demo構築。**

注意: 「個車のRUL/交換時期をEPSサプライヤが売る」形は既往検証でKill済み(禁止主張・データ所在・既存プレイヤー)。目的地はこのKillと矛盾しない。需要調査の対象は「誰が・何のために・どの粒度で予測を欲しがるか」の全体であり、群レベルの予測、入庫優先度、DTC未満の状態説明など、制約を生き残る形をすべて含む。SPD本線(docs/119〜132)はこの需要調査の第1ラウンド(生き残り形態=状態説明の特定とDemo v1)だった。

**ビジネスモデル定義(2026-07-07、[docs/138](docs/138_business_model_definition.md)): 3層構造。第1層(唯一の収益線)= 状態説明機能を組み込んだEPS製品仕様をOEMにRFQ差別化+診断コンテンツNREとして売る。第2層= 市場シグナル監視は内部投資(第1層の信用の裏付け)。第3層= assessmentはprogram付帯NREのみ。事業のKill条件はBM-KQ1〜4(RFQ要求の実在、採点影響の有無、NRE余地、社内利用)。**

**前提の恒久確認(2026-07-07、AGENTS.md「Personal Public-Only Research Rule」に記載): この活動は現段階では仕事ではなく個人研究であり、内部情報は使わない・使う予定もない。BM-KQ1〜3や質問シート回答などの内部依存項目は「境界の記録」であり、次アクションとして扱わない・以後尋ねない。成果物の宛先は技術者。Demoの方針は「公開logから人間には読み取れない兆候を機械的に読み取り、SOTIFへ部品側として参加できる形を見せる」。**

## 現行フェーズ: 故障予測の需要マップ

| # | 作業 | 内容 | 出力 | 状態 |
|---|---|---|---|---|
| A | 需要マップ | 故障予測を欲しがる主体(OEM保証/品質、fleet、整備、保険、vehicle health基盤、サプライヤ内部)ごとに、欲しい予測の形・粒度・必要データ・既存プレイヤー・EPSサプライヤの入り口を1表に整理 | [docs/133](docs/133_failure_prediction_demand_map.md) + [data TSV](data/failure_prediction_demand_map.tsv) | 完了。個車レベルの席(RUL/予兆/入庫優先度)はfleet側(Uptake/Questar/Stratio)もOEM側(Viaduct等)も埋まっている。空席は(1)部品内部のDTC未満信号=第1ラウンド検証済み、(2)群レベルの故障傾向(公開データ)=未検証でフェーズB/Cの本命 |
| B | データ当たり付け | 空席(2)に対し、公開データ(NHTSA苦情DB、リコール/ODI、英国DVSA MOT車検統計、既存proxy資産)で「車齢×操舵系不具合率」曲線が誠実に引けるかを判定 | [docs/134](docs/134_group_level_data_feasibility.md) + [data TSV](data/group_level_data_feasibility.tsv) | 完了。**引ける=フェーズC Go**。主データ=NHTSA苦情API(実働確認済み、STEERING/発生日/年式あり)、答え合わせ=既知リコール(15V-340対象cohortが浮くか)、拡張=DVSA MOT(分母付き率曲線)。分母なし・報告バイアス等の限界も明記 |
| C | Demo構築 v2 | 群レベル操舵系リスク曲線Demo: Fusion MY2010-2014のcohort曲線+リコール答え合わせ+報告バイアスの可視化 | [docs/135](docs/135_steering_cohort_curve_demo_verdict.md) + [scripts/steering_cohort_curve.py](scripts/steering_cohort_curve.py) + [generated HTML](generated/steering_cohort_curve.html) + [data TSV](data/steering_cohort_curve_summary.tsv) | **完了。答え合わせ成功**: リコール対象cohort(MY2011-2012)の操舵系比率51.2%/57.7%が比較cohort(21.5%/24.2%)の2倍以上に浮き、盲検集計が公式リコール事実を再現。空席(2)は公開データで埋められると実証 |
| D | 時点区切りバックテスト | その時点で知り得た届出だけで、リコール公表前に浮きが検知できたか(早期検知として使えるか)を、事前固定した検知ルール(30件以上+旧世代基準2倍+30%下限)で判定 | [docs/136](docs/136_steering_cohort_backtest_verdict.md) + [scripts/steering_cohort_backtest.py](scripts/steering_cohort_backtest.py) + [generated HTML](generated/steering_cohort_backtest.html) + [data TSV](data/steering_cohort_backtest.tsv) | **完了。MY2012はリコール25ヶ月前(ODI調査より約1年前)、MY2011は7ヶ月前に発火。非リコールcohortは発火せず(偽陽性ゼロ)。MY2010は届出遅延により検知不能=苦情ベース検知の適用限界として記録。空席(1)と(2)の相補性が確定** |
| E | 残候補一括消化 | ①横展開(Silverado) ②故障モード分類 ③DVSA見極め ④転記見本 | [docs/137](docs/137_residual_candidates_sweep.md) + [data TSV×2](data/steering_mode_split.tsv) + [scripts/steering_mode_split.py](scripts/steering_mode_split.py) + generated HTML | **完了。①負の結果: 事前固定ルールはSilveradoの両リコールcohortをMISS(絶対閾値は車種を跨いで汎化しない。相対シグナルは8〜13倍で存在) ②Fusionの浮きの60〜62%はアシスト喪失モード=リコール対象モードそのもの。モードベース監視がルール改訂候補(要第3車種で事前固定検証) ③DVSAは年10GB級と確定、EPS固有分類の存在を確認、再開価値高で保留 ④品質改善向け月次監視レポートのモック作成** |
| F | Log兆候抽出デモ(技術者向け) | 上位ルールのDemo方針の実装: 公開走行log(commaSteeringControl、MIT)から人間には読めない統計兆候を機械抽出し、payload+SOTIF語彙へ変換する仕組みをend-to-endで見せる | [docs/139](docs/139_log_sign_extraction_demo.md) + [scripts/steering_log_sign_extraction.py](scripts/steering_log_sign_extraction.py) + [generated HTML](generated/steering_log_sign_extraction.html) + [data TSV](data/steering_log_sign_extraction.tsv) | **完了(v2)。妥当性ゲート+クラス分け導入、上位検出の正体検分、8章構成の技術者向けレポートに再構成** |
| G | 実証モデルA: リコール検知 | 苦情DB全件+リコール台帳全件で、事前登録プロトコルによる時系列分割評価(v1→v2改訂、テストアクセス2回で打ち切り) | [docs/140](docs/140_recall_detection_protocol.md) / [docs/141](docs/141_recall_detection_results.md) / [docs/142](docs/142_recall_detection_protocol_v2.md) / [docs/143](docs/143_recall_detection_results_v2.md) + scripts×2 + [結果ログ](data/recall_detection_results.tsv) | **確定判定: 基準(prec≥0.5∧rec≥0.3)にv2でも僅差未達(0.48/0.26)→「実用シグナル不成立」で確定し、テスト3回目は封印(将来2025年以降のリコールeraを次の検証データに指定)。確定した知見: 信号は実在(PR-AUC 0.355=無情報3.2倍、ROC 0.796、手作りルール比で桁違い)、リード×精度のトレードオフ定量化、適用範囲=乗用車系のみ、EPS系予兆は苦情から最も見えにくい(=部品内部観測の希少性の裏付け)。第2層の位置づけは「注意配分の道具」に確定** |
| L | 兆候→翌年故障の先行性(個体連結) | 中央の橋の実データ検証: 車検2年分を車両IDで連結し、不合格未満の記録(advisory/minor)が翌年の操舵系不合格を先行予測するかを全数で検定 | [docs/150](docs/150_advisory_precedence_verification.md) + [scripts/mot_advisory_longitudinal.py](scripts/mot_advisory_longitudinal.py) + [data TSV](data/mot_advisory_longitudinal.tsv) | **完了・成立(本研究最強の結果)。約1,700万個体で、兆候のみの個体は翌年の操舵系不合格率が最大24倍(車齢4-7年: 0.43%→10.3%)。しかも若い車では「兆候のみ」群が「不合格→修理」群より高率=不合格未満の層は最も予測力があり最も放置されている。目視観察とECU内部信号の区別、生存バイアス等の限界を明記** |
| K | 偏り・EV新規参入・日本データ | 不合格の車種偏在、EV/新興メーカーの上振れ有無、日本の同年代データの検証 | [docs/149](docs/149_concentration_ev_and_japan.md) + [scripts/dvsa_mot_concentration.py](scripts/dvsa_mot_concentration.py) + [data TSV](data/dvsa_mot_concentration_2025.tsv) | **完了。①偏りは強烈: 15,626モデル中10モデルで不合格の50%(Corsa単独16.6%)、年齢補正後もメーカー間18倍 ②EV/新興(Tesla/MG)は中位で異常なし。EVは車齢5年以降むしろ低率(事故率は別の問いと明記) ③日本は英米級の公開マイクロデータなし。ホットライン集計(FY2024: かじ取り99件/3.1%)を取得。苦情母数が小さく日本では苦情ベース群監視は成立しにくい=部品内部観測の相対価値が高い地域差を記録** |
| J | 分母つき群曲線(英国車検2025) | 米国苦情曲線(分母なし)の独立再検証。9.2GBをストリーム2パス処理 | [docs/148](docs/148_dvsa_mot_denominator_verification.md) + [scripts/dvsa_mot_steering_rates.py](scripts/dvsa_mot_steering_rates.py) + [data TSV](data/dvsa_mot_steering_2025.tsv) + [generated HTML](generated/dvsa_mot_steering_2025.html) | **完了・成立。2,800万件の全数検査で、操舵系不合格率は車齢3年0.11%→20年で約40倍と単調増加。EPS固有項目も同形(絶対値は極小=コード化の癖を明記)。読み方の注意(車検義務3年目から、生存バイアス、メーカー優劣に使わない)を同梱** |
| I | 多車種展開+実在変種比較 | 波形感度の4車種再現と、実在する部品/ソフト版数グループの分離可否 | [docs/147](docs/147_multiplatform_and_variant_verification.md) + scripts + data TSV×4 | **完了。質的パターンは4車種で再現(閾値は車種固有=手法は移るが閾値は移らない)。実在変種の分離は使い方の交絡に埋もれ「捕まらなかった」と報告——個体内の縦断監視が本命という設計結論に3経路目で到達** |
| H | 実証モデルB: 波形合成劣化感度 | 公開走行logへの既知量の劣化注入で、log兆候パイプラインの検出限界を定量化 | [docs/144](docs/144_synthetic_sensitivity_results.md) + [scripts/steering_synthetic_sensitivity.py](scripts/steering_synthetic_sensitivity.py) + [generated HTML](generated/steering_synthetic_sensitivity.html) + [data TSV](data/steering_synthetic_sensitivity.tsv) | **完了。操作点z≥4(健全時誤検出6.7%実測)で、90%検出限界: 応答遅れ0.4s / ゲイン変化15% / 定常バイアス≤0.05m/s² / 非対称は0.3でも86%。検出不能領域(遅れ0.1s、ゲイン2%)も対等に報告。合成条件である限界を明記。モデルAの「苦情からEPS系予兆は見えない」と合わせ、部品内部観測の必要十分性が両側から定量で揃った** |

## 現在地(SPD本線=第1ラウンドの区切り)

2サンプル(電源監視、通信入力妥当性)とも公開情報のみで価値仮説をConfirmedし「限定Proceed」。残項目はすべて実行段階の内部資料条件。**全体まとめとID対訳表は [docs/131](docs/131_steering_predictive_diagnostics_checkpoint_summary.md) を最初に読むこと。**

## 何を判断しようとしているか

自然言語で言うと、次の1点である。

> EPS内部重要モジュール(まず電源監視、次に通信入力妥当性)がruntimeで観測した「DTC未満の普段と違う状態」は、既存のDTC / reset log / freeze frame / extended data / 汎用テレマティクス / ADAS / IDSでは残らない差分を持ち、原因断定なしに部署成果物またはvehicle healthへの部品側状態説明に転記できるか。

Yesなら SPD008 は次の本線として続き、Noなら Hold / Stop に落とす。
この判断に必要な作業だけを、下のNextActionに置く。

## NextAction 一覧

| # | 作業 | 目的 | 出力 | 状態 |
|---|---|---|---|---|
| 1 | 電源監視の実残存フィールド照合質問シート作成 | [docs/122](docs/122_steering_predictive_diagnostics_power_monitor_payload_sample.md) の判定ゲート(5項目中2項目以上のsoft context差分 + 2部署以上の使い道)を解くための唯一のインプットを作る | [docs/123](docs/123_steering_predictive_diagnostics_power_monitor_program_question_sheet.md) + [data TSV](data/steering_predictive_diagnostics_power_monitor_program_question_sheet.tsv) | 完了 |
| 2 | 通信入力妥当性の独立ケース化 | 第二検証候補([docs/120](docs/120_steering_predictive_diagnostics_spd008_predictive_value_check.md))を、電源監視と同じ型(単一ターゲットケース → 最小payload → 判定ゲート)で独立に判定できる状態にする | [docs/124](docs/124_steering_predictive_diagnostics_comm_input_validity_case.md) + [data TSV](data/steering_predictive_diagnostics_comm_input_validity_case.tsv) | 完了 |
| 3 | 未検証デルタのファクトチェックと判定 | 「SPD008の既存monitor比優位性は未検証」([docs/117](docs/117_steering_predictive_diagnostics_spd008_vs_spd002_decision.md))と「汎用テレマティクス / 路面分類 / ADAS / IDSとのデルタは未検証」([docs/98](docs/98_business_model_mainline_after_correction.md) Kill条件)を、公開情報で検証し判定を書く | [docs/125](docs/125_steering_predictive_diagnostics_unverified_delta_check.md) + [data TSV](data/steering_predictive_diagnostics_unverified_delta_check.tsv) | 完了 |
| 4 | SPD002デモ枝の扱いを明文化 | [docs/114](docs/114_steering_predictive_diagnostics_spd_final_conclusions.md) でProceed指定のまま停滞しているSPD002 reference demoを、1〜3が決着するまで意図的に凍結と記録し、暗黙の放置にしない | docs/125 内の1節 | 完了 |
| 5 | ブランチのremote公開 | 23コミット未pushでlocalのみ。消失リスク回避 | `git push -u origin research/bosch-motion-domain-ai` | 未実施(ユーザ判断待ち) |
| 6 | SOTIFへの乗り方の判定 | 「SOTIFに乗っかれるプロダクト」の見込みを3分解(プロセス支援 / 論証証拠 / 運用フェーズ監視インプット)で判定し、入口条件KQ1を固定する | [docs/126](docs/126_steering_predictive_diagnostics_sotif_contribution_prospect.md) + [data TSV](data/steering_predictive_diagnostics_sotif_contribution_prospect.tsv) | 完了 |
| 7 | ターゲットケースの公開実在確認 | 「permanent DTCが残らない断続的なassist低下」が公開苦情 / TSB / リコール調査に実在するかを、既存pain family整理を「故障コードが残らない」条件で絞り直して確認する。実在しなければ市場需要側から弱まる | [docs/127](docs/127_steering_predictive_diagnostics_target_case_public_evidence.md) + [data TSV](data/steering_predictive_diagnostics_target_case_public_evidence.tsv) | 完了。実在Confirmed(Ford 15V-340の「DTCなし」是正経路、GM 17V-414の1秒喪失・復帰、GM TSB 17-NA-158の外部signal起因警告ほか)。以後のSPD本線は内部資料条件待ち |

## 内部資料の扱い(2026-07-06追記)

現行方針は「公開情報は使う、内部資料は使わない」である。
これに伴い、次の2つは次アクションから外し、**内部資料を使える条件になった場合だけの実施条件**として保存する(Coverage Benchmark / SbWと同じ扱い)。

- #1 質問シートのprogram固有欄の回答取得(docs/123に実施条件として明記)
- docs/126のKQ1(RFQ / 安全要件の中身確認)とKQ2

現行方針で進められる次アクションは #7 である。

| # | 作業 | 目的 | 出力 | 状態 |
|---|---|---|---|---|
| 8 | SOTIF公開シグナル観測 | KQ1(SOTIF要求の部品側展開)の公算を公開情報で観測する | [docs/128](docs/128_steering_predictive_diagnostics_sotif_public_signal_watch.md) + TSV追記(SOTIF013〜016) | 完了。SOTIF-EooC(規格上の部品参加形式)とBosch定量SOTIF特許・by-wire量産を確認。KQ1公算は補強、最終確認は内部資料条件のまま |
| 9 | 判定ゲートの公開ケース照合 | 質問シートの照合対象を「自社program」から「公開リコール是正実務」へ組み替え、内部資料なしで判定ゲートを閉じられるか試す | [docs/129](docs/129_steering_predictive_diagnostics_public_case_crosscheck.md) + [data TSV](data/steering_predictive_diagnostics_public_case_crosscheck.tsv) | 完了。Ford 15S18・GM 17276の一次文書精読により5項目中4項目の差分を公開レベルでConfirmed。SPD008は「公開レベルConfirmed付き限定Proceed」へ。内部資料条件は検証ではなく実行のみに縮小 |
| 10 | comm input validityの公開ケース照合 | #9と同じ手法を第二候補に適用する | [docs/130](docs/130_steering_predictive_diagnostics_comm_validity_public_crosscheck.md) + [data TSV](data/steering_predictive_diagnostics_comm_validity_public_crosscheck.tsv) | 完了。GM TSB 17-NA-158原文で「無効な依存signal→操舵警告→直らないgear交換の連鎖」をOEM公式記録として確認し、Hold→公開レベルConfirmed付き限定Proceedへ。副産物としてFord SSM 49530(2021年)で現行世代のpower context誤帰属も確認 |
| 11 | 区切りまとめとID対訳 | IDなしの自然言語で全体を言い直し、最終判定・実行条件・ID対訳表を1本に集約する | [docs/131](docs/131_steering_predictive_diagnostics_checkpoint_summary.md) | 完了。公開情報での仮説検証はここで区切り。以後は実行段階(内部資料条件)のみ |
| 12 | 具体化 案A: payload replay demo | 公開3ケース(GM 17-NA-158、Ford SSM 49530、Ford 15S18)を最小payloadで再演し、境界ガード(禁止主張の機械的拒否)込みで動く形にする | [docs/132](docs/132_steering_predictive_diagnostics_payload_replay_demo.md) + [scripts/spd008_payload_replay.py](scripts/spd008_payload_replay.py) + [generated HTML](generated/spd008_payload_replay.html) + [data TSV](data/spd008_payload_replay_cases.tsv) | 完了。3ケースともpayloadはガード通過、安直な言い方(原因断定・交換判断・無罪)は3件とも機械的に拒否されることを実行で確認 |
| 13 | 具体化 案B: 固定スコープassessmentの商品仕様化 | docs/122-123とデモを、スコープ/成果物/工数/やらないことの1枚仕様に変換する | docs/133(未作成) | 未着手 |

## 実行順と依存関係

1. #1 質問シート(電源監視) — docs/122の明示的な次タスク。最優先
2. #2 通信入力妥当性ケース — #1と独立。同じ型を再利用
3. #3 デルタ検証 — #1/#2の照合観点を既存技術事実(UDS / AUTOSAR DEM / テレマティクス電圧監視 / IdsM)と突き合わせる。ネットワークでのファクトチェックを含む
4. #4 は#3のドキュメント内で処理
5. #5 は任意タイミング

## 判定の出口

- 質問シート(#1)が対象programで回答され、判定ゲートの条件を満たす → 電源監視はProceed(固定スコープassessmentとして)
- 既存monitor / 既存mechanismで5項目が十分に残ると分かる → Hold / Stop に落とす(Rule Check必須)
- #3で汎用テレマティクス / IDSとの差分が説明できない → docs/98のKill条件に接続する

## 禁止主張(全作業共通)

EPS RUL、交換時期、故障発生時期、安全保証、root cause断定、保証費削減、EPS無罪、電源原因断定、外部ECU原因断定。
