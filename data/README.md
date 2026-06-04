# Data Notes

このディレクトリは、Repo内の事業仮説に対して参照できるビジネスモデル探索メモを置く。

## Files

- `business_model_research.tsv`
  - Repo内の6案に対応する隣接ビジネスモデルを100件整理したTSV。
  - 各行に、顧客、課題、収益モデル、抽出知識、本Repoへの有効アイテム、関連度を記載。
- `useful_items_for_steering_diagnostic_evidence.md`
  - 100件から、本Repoに移植しやすい知見を統合したメモ。後半に `EPS Health Intelligence Package` への軸修正も記載。
- `ota_connected_health_market_signals.tsv`
  - OTA / connected vehicle / remote diagnostics / SOVD / EPS safety trendから、EPS connected health方向の需要シグナルを整理したTSV。
- `target_feasibility_matrix.tsv`
  - EPS Health Intelligence方向について、ターゲット別の実現性、魅力度、データアクセス、初期ピッチを整理したTSV。
- `eps_health_indicator_candidates.tsv`
  - EPS内部信号から作れるhealth / degradation indicator候補を、必要信号、劣化・故障ヒント、正規化難易度、OEMデータ依存度つきで整理したTSV。
- `business_model_feasibility_100.tsv`
  - EPS Health Intelligence周辺のビジネスモデル成立性を100案で整理したTSV。
- `business_model_feasibility_sources.md`
  - 100案の発想元にした市場・技術ソースのメモ。
- `best5_business_model_candidates.md`
  - 100案から選んだBest5と推奨初手。
- `demo_eps_health_summary_examples.tsv`
  - Best5のうちPoCに使いやすいhealth summary出力例。
- `customer_pain_market_signals.tsv`
  - 市場調査で見えたWarranty / NTF / supplier quality / 顧客品質報告 / remote diagnosticsの買い手痛みを整理したTSV。
- `eps_event_context_market_research.tsv`
  - EPSサプライヤ視点で、`EPS Event Context Memory` が接続できる市場痛みをWarranty / NTF / returned parts / 顧客品質報告 / 原因調査中心に整理したTSV。
- `eps_ntf_case_review_template.tsv`
  - 外部市場調査では見えない、EPS返却品・市場不具合・NTF・再現不能案件の内部一次調査用テンプレート。
- `eps_ntf_case_classification_value_map.tsv`
  - 20-50件のケース分類が完了した場合に、誰が何を嬉しいのか、どんな意思決定が可能になるのかを整理した価値マップ。
- `public_proxy_data_sources.tsv`
  - 内部NTF/返却品ケースにアクセスできない前提で、NHTSA、Kaggle、公開CAN/steering datasetから補える情報と補えない情報を整理したTSV。
- `eps_public_market_pain_cases.tsv`
  - NHTSA / recall / investigation / public reportから、driver-visibleなEPS痛みを抽出した公開ケース分類TSV。
- `public_steering_dataset_inventory.tsv`
  - 公開steering / CAN / OBD / Kaggle datasetの信号、用途、できないこと、優先度を整理したTSV。
- `steering_context_risk_phase1_summary.tsv`
  - `Steering Context Risk Explorer` Phase 1の静的集計結果。公開EPS pain caseのsource、proxy feature、driver-visible pain、boundaryを整理。
- `low_speed_high_steering_proxy_summary.tsv`
  - commaSteeringControl `CHRYSLER_PACIFICA_2018` の走査条件、件数、候補window件数の要約。
- `low_speed_high_steering_proxy_windows.tsv`
  - 低速・高操舵要求proxyとして抽出した上位12件の代表window。
- `low_speed_high_steering_proxy_timeseries.tsv`
  - 上位5件の代表windowについて、`vEgo`、`steerFiltered`、`steeringAngleDeg`、`latAccelDesired` などの時系列を切り出したTSV。
- `eps_scenario_to_evidence_pack.tsv`
  - 公開市場文脈と公開走行windowを、EPSサプライヤ向けの評価シナリオ、内部信号、既存診断との差分、次検証、kill criterionへ変換したTSV。
- `s2e001_diagnostic_evidence_gap_check.tsv`
  - `S2E001 low_speed_high_effort` に絞り、必要証跡、既存診断の想定カバー範囲、不足時の追加候補、内部確認項目を整理したTSV。
- `s2e001_diagnostic_evidence_review_template.tsv`
  - 内部DTC仕様、freeze frame、extended data、返却品reader可否、NVM制約を入力して、S2E001をProceed / Kill / Hold判定するテンプレート。
- `business_model_rebranch_after_s2e001_hold.tsv`
  - S2E001 Hold後に、内部データ不要で売れるもの、内部データがあれば売れるもの、OEM依存で後回しのものへビジネスモデルを再分岐したTSV。
- `bmr001_market_pain_scenario_cards.tsv`
  - `BMR001 EPS Market Pain Scenario Library` の初期3枚scenario card。公開市場case、代表proxy window、売り先、評価シナリオ、設計レビュー質問、診断証跡質問、RFQ文言、Kill条件を整理。
- `bmr002_rfq_design_review_pack.tsv`
  - BMR001のscenario cardを、RFQ/設計レビュー1ページに変換するための構成部品。Market Pain Coverage Statement、Scenario Readiness Matrix、Supplier-Owned Boundary、Diagnostic Explainability Checklist、Validation Scenario Hook、Customer Quality Fact Summary Skeletonを整理。

## Interpretation

この収集は、個別企業の公開情報を網羅するものではなく、`docs/` にある選択肢に対して、事業モデルの型と移植可能な知識を整理した初期リサーチである。
特に重視した観点は以下。

- EPS / ECU単体の故障予測として売らない
- 「ログ追加」や既存診断証跡の言い換えではなく、返却品・NTF・再現不能案件の不足証跡を特定する
- 故障予測そのものではなく、顧客品質報告や原因調査に使える確認済み事実・未確認事項を整理する
- サプライヤが責任を持てる範囲に収める
- ECUメーカー起点で成立するCoreと、OEMデータ接続で広がるOptional extensionを分ける
- 将来OEM側のVHM / connected diagnostics / 市場品質データと接続しやすい形にする
- まずはDTCだけでは説明できない市場不具合・返却品・NTF案件に対する、ECU内の小さな状況証拠として価値を検証する
- ただしDTC、freeze frame、extended data、event memory自体は既存診断であり、新規性はサプライヤ内部の案件棚卸しから不足証跡を特定することに置く
- ケース分類の価値は、分類表そのものではなく、診断仕様改善、顧客品質報告、追加データ要求、事業継続判断を可能にすることに置く
- 内部一次情報がない場合、公開データでできるのは市場痛み分類とsteering context proxy demoまでであり、EPS内部故障予測や返却品解析価値は証明できない
- commaSteeringControlのproxy demoは、低速・高操舵要求の正常走行windowを作るものであり、assist loss、劣化兆候、DTC不足を直接示すものではない
- `eps_scenario_to_evidence_pack.tsv` の価値は、追加証跡を断定することではなく、既存DTC / freeze frame / extended dataで十分かをシナリオ別に潰すことにある
- `s2e001_diagnostic_evidence_gap_check.tsv` では、車速/操舵角/電圧/温度/カウンタのように既存で残りやすいものを追加価値として扱わず、assist demand-to-output、limit/derating、pre-event scalar summaryだけを条件付き候補に残す
- `s2e001_diagnostic_evidence_review_template.tsv` は、追加候補を提案するためではなく、内部診断仕様を入れた結果としてProceed / Kill / Holdを判定するためのレビュー表である。内部仕様を確認できない場合、S2E001はHoldとして扱う
- `business_model_rebranch_after_s2e001_hold.tsv` では、ECU内追加証跡商品を現時点では追わず、公開市場文脈を使ったscenario library、RFQ/design review pack、diagnostic evidence workshopへ軸を戻す
- `bmr001_market_pain_scenario_cards.tsv` では、故障予測や既存診断不足を主張せず、公開市場ペインを評価、設計レビュー、RFQ、顧客品質説明で使うscenario cardへ変換する
- `bmr002_rfq_design_review_pack.tsv` では、scenario card単体では価値が弱い前提を置き、RFQ回答、設計レビュー、DRBFM、評価計画へ転記できる1ページに変換できるかを検証する
