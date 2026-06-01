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
