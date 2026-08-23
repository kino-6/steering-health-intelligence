# Memory.md — セッション復帰用インデックス

新しいセッション(人間・AIどちらでも)でこのRepoに戻ってきたとき、ここだけ読めば議論の現在地に復帰できるようにするための台帳。詳細は各ドキュメントへのリンク先が正。

## このRepoは何か

**個人の事業仮説研究**(所属組織の業務ではない)。目的は「(操舵系の)故障予測の需要調査、および必要ならデータ収集、Demo構築」(Plan.md)。**公開情報のみを使う**——内部情報・内部資料は使わない・入手経路も作らない。最上位ルールは [AGENTS.md](AGENTS.md) の「Personal Public-Only Research Rule」(0〜7条)。結論の書き方は「判断を先に、根拠を箇条書きで、日本語優先」。

## 現在地(2026-07-15 時点)

**公開データで能動的に実行できる検証はほぼ消化した。以後は原則として観測台帳(受動)のみ**(docs/151)。

2026-08-22に横断棚卸し([docs/154](docs/154_open_items_after_exhaustion_claim.md))を実施し、**未消化3件を発見して全て消化した**([docs/155](docs/155_window_recurrence_verification.md) 窓長・再発、[docs/156](docs/156_train_era_miss_structure.md) 見逃し構造、[docs/157](docs/157_mode_split_and_corsa_correction.md) モード照合)。**うち docs/157 は docs/151 の Corsa 答え合わせを誤帰属と訂正した。**

確立した証拠連鎖(技術主張の最終形、docs/150):

1. **現象は実在** — 電動パワステの断続的アシスト喪失は Ford(米)・GM(米)・Vauxhall Corsa(英)の3独立市場で確認された故障ファミリー(docs/127, 129, 151)
2. **仕組みは作れる** — 合成劣化注入で検出限界を定量: 90%検出は 応答遅れ0.4s / ゲイン15% / バイアス0.05 m/s²、誤検知6.7%(docs/144)。手法は車種を跨いで移るが閾値は移らない(docs/147)
3. **外からは見えない** — 苦情・リコール等の外部データではEPS内部の前駆信号は観測できない=部品内部観測の独占性(docs/143, 145)
4. **偏在は車種×年式に集中** — 英国車検2,800万件で上位10モデルが操舵不合格の50%。群シグナル上位は公開不具合記録と対応(答え合わせ3例成立)。ただし欠陥(Corsa)と用途摩耗(バン)の2型があり、切り分けにはモードが要る(docs/148, 149, 151)
5. **閾値未満の兆候には故障に先行する実情報が乗る** — 1,700万個体の連結で、兆候のみ→翌年操舵不合格が最大**24.1倍**(車齢4-7年)。しかも兆候層は最も予測力があり最も放置されている(docs/150)——**本研究の最強の実証**

ビジネス判断(docs/146): SOTIF運用フェーズ監視への部品側参加は**時限の窓**。競合の実弾(Nexteer MotionIQ/Health 量産投入)が支払い意思の最も硬い証拠。誤り条件つきで判断済み。

## 読み順(復帰時はこの順)

| 順 | ドキュメント | 内容 |
|---|---|---|
| 1 | [docs/131](docs/131_steering_predictive_diagnostics_checkpoint_summary.md) | 中間まとめ + ID対訳表(SPD/BM等の記号の意味) |
| 2 | [docs/145](docs/145_final_conclusions_and_interpretations.md) | 技術・ビジネス成立性の結論 |
| 3 | [docs/146](docs/146_business_framework_and_roadmap.md) | ビジネスの枠組み・段取り(時限の窓) |
| 4 | [docs/150](docs/150_advisory_precedence_verification.md) | 最強の実証(兆候→故障 24倍) |
| 5 | [docs/151](docs/151_high_rate_model_crosscheck.md) | 答え合わせ3例目 + **観測台帳(次に見るもの)** |
| 補 | [README.md](README.md) / [Plan.md](Plan.md) / [docs/INDEX.md](docs/INDEX.md) | 結論と根拠の入口 / フェーズ全表 / 全ドキュメント索引 |

## 直近の更新(2026-08-23)

- **本丸だった「兆候→故障の橋」は熱・接合部の族で実証**([docs/167](docs/167_precursor_results_v2.md))。故障の1〜2段階前、ノイズの20〜300倍。個体基準+動作点正規化で成立([docs/163](docs/163_per_unit_baselining.md))
- **ただし SOTIF ではなく 26262 側**([docs/169](docs/169_sotif_link_check.md))。SOTIFの接点は「兆候〜故障確定の窓」で、熱余裕13〜50%喪失として翻訳した([docs/170](docs/170_thermal_headroom_translation.md))
- **熱経路はEPSの公開記録に支持されない**([docs/171](docs/171_eps_wearout_mechanism_scan.md))。市場で優勢なのは接点・接続系(2.81倍)、熱系は平均以下(0.54倍)
- **接点系(A'')は公開情報では答えられないため問いを閉じた**([docs/175](docs/175_close_contact_question.md))。公開劣化データ110件の総覧に接点は0件。**fretting系に実用的な先行時間はない**
- **作業の作法6項目を [AGENTS.md](AGENTS.md) に追加**(データセット採用前に論文の機構節を読む、棚卸しは3軸、事前登録、完了宣言前の全文検査、数える単位を疑う、故障族ごとに主張を分ける)

## 直近の更新(2026-08-22)

- **公開データセット棚卸しを更新**([docs/159](docs/159_public_dataset_reinventory.md))。前回は車両レベルしか探しておらず、**部品レベル(PMSM/インバータ)の実故障ラベル付きデータ2件を見落としていた**。
  **DS011(KAIST、CC BY 4.0、1.0/1.5/3.0 kW、severity連続値8段階、電流100kHz)が最重要**——EPSと同型・同出力帯のモータで、劣化が段階的に振られた実データ。
  棚卸しは以後「用途軸(steering/EPS)」と「部品軸(PMSM/inverter/winding)」の2軸で行う
- **理想回路モデルはユーザ承認済み**(内部情報を使わないため)。DS011と突き合わせれば循環問題の一部を断てる

## 最上位ルールの理由(2026-08-23 ユーザ明示)

**「公開情報のみ」は面倒回避のためではなく、調査に嘘をつけなくするための装置である。**
内部情報を許せば「確認できない」を理由に検証不能な主張を通せてしまい、自分自身も監査できなくなって研究が破綻する。
**検証できない主張は、この研究では存在しないのと同じ。** 出典・再現スクリプト・事前登録は、すべてこの目的の装置。

## 用語の定義(取り違え注意)

- **「Demo」= 一定の結果が出るまでプロジェクトを回すこと**(2026-08-22 ユーザ訂正)。画面・レポート・数字の陳列ではない。
  UIを作って「Demoができた」と報告するのは誤り。求められているのは結論(成立/不成立とその根拠)への到達。
  実際に [docs/158](docs/158_sotif_eooc_monitor_demo.md) でこの取り違えが起きた

## Kill済み・禁止事項(蒸し返さない)

- **故障予測(RUL・交換時期予告)は Kill済み** — 実証モデルv2は事前登録基準に対し不成立確定(precision 0.48 / recall 0.26 < bar 0.5/0.3、docs/143)。以後の主張は「群統計の記述」「不足の検出」まで
- **禁止する主張**: 故障予測・余寿命・交換時期/原因断定/安全保証/保証費削減効果/EPS無罪論/OEM・モデルの設計優劣断定
- **公開による反応測定は禁止**(AGENTS.md 6条)。公開・発信はユーザの明示指示がある場合のみ
- **内部情報を次アクション・再開条件にしない**。内部依存の論点は「ここで問いを閉じる」で終える(docs/123, 138 は境界の記録)

## 観測台帳(受動、docs/151 が正)

Nexteer MotionIQ の採用/撤退|2025年以降の操舵系リコール蓄積(識別モデルの汚染なし再試験)|新興EVメーカーが車齢3年超になった頃の英国再集計|NALTEC(日本OBD検査)データ開放|ISO 21448 運用フェーズ・UNECE 監視要求の実装。未照合のまま残したもの: Fiat 500X / Jeep Renegade(推測で埋めない)。

## データ源と再現(キャッシュは gitignored、消えても再取得可)

| ローカル | 出所・ライセンス | 使うスクリプト |
|---|---|---|
| `.dvsa_mot/` | 英国 DVSA MOT結果+不合格項目(OGL v3.0)、年約4.8+4.4GB zip | `dvsa_mot_steering_rates.py`, `dvsa_mot_concentration.py`, `mot_advisory_longitudinal.py` |
| `.nhtsa_flat/` | NHTSA FLAT_CMPL.zip / FLAT_RCL_POST_2010.zip(米、公有) | `build_cohort_monthly.py`, `recall_detection_model.py`, `steering_cohort_*.py` |
| `.public_log_cache/` | comma.ai commaSteeringControl(MIT、120プラットフォーム) | `steering_log_sign_extraction.py`, `steering_synthetic_sensitivity.py`, `steering_fw_group_comparison.py` |
| `.jp_mlit/` | 国交省 不具合情報(集計PDFのみ。個票なし) | (docs/149 の記録のみ) |

数表は `data/*.tsv`、レポートHTMLは `generated/` にコミット済み。

## ブランチ運用

- `research/bosch-motion-domain-ai`: 作業ブランチ(コミット→push→mainへfast-forward mergeを都度実施)
- `main`: 集約先
- `public-snapshot`: **公開用**。履歴なしの単一スナップショット方式——mainのツリーをそのまま新コミットとして積む(`git commit-tree main^{tree} -p public-snapshot`)。公開前チェック: 追跡ファイルに PII・認証情報・ローカルパス・キャッシュディレクトリが無いこと(2026-08-21 再監査、クリーン。記録は [docs/152](docs/152_publication_readiness_reaudit.md))

## 復帰時の定型手順

1. この Memory.md → docs/151 の観測台帳を読む
2. 観測台帳のどれかが動いたか(ニュース・データ更新)を確認する
3. 動いていなければ能動作業はない。動いていれば該当スクリプトを再実行し、docs/152以降として判断→根拠形式で記録する
