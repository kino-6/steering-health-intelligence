# Data Notes

このディレクトリは、Repo内の事業仮説に対して参照できるビジネスモデル探索メモを置く。

## Files

- `business_model_research.tsv`
  - Repo内の6案に対応する隣接ビジネスモデルを100件整理したTSV。
  - 各行に、顧客、課題、収益モデル、抽出知識、本Repoへの有効アイテム、関連度を記載。
- `useful_items_for_steering_diagnostic_evidence.md`
  - 100件から、本Repoの本命案である `Steering Diagnostic Evidence Package` に移植しやすい知見を統合したメモ。

## Interpretation

この収集は、個別企業の公開情報を網羅するものではなく、`docs/` にある6つの選択肢に対して、事業モデルの型と移植可能な知識を整理した初期リサーチである。
特に重視した観点は以下。

- EPS / ECU単体の故障予測として売らない
- OEM / Tier1の市場不具合解析を早める
- DTCだけでは不足する診断エビデンスを商品化する
- サプライヤが責任を持てる範囲に収める
- 将来OEM側データと接続しやすい形にする
