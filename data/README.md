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
  - EPS内部信号から作れるhealth / degradation indicator候補を、必要信号、劣化・故障ヒント、正規化難易度つきで整理したTSV。

## Interpretation

この収集は、個別企業の公開情報を網羅するものではなく、`docs/` にある選択肢に対して、事業モデルの型と移植可能な知識を整理した初期リサーチである。
特に重視した観点は以下。

- EPS / ECU単体の故障予測として売らない
- 「ログ追加」ではなく、EPS自体の付加価値としてhealth indicatorを持たせる
- 故障予測そのものではなく、予測に使える材料と劣化兆候を整備する
- サプライヤが責任を持てる範囲に収める
- 将来OEM側のVHM / connected diagnostics / 市場品質データと接続しやすい形にする
