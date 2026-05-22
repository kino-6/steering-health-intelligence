# Steering Health Intelligence Notes

EPS / ステアリング制御系ECUにおける、故障予測・診断データ・OEM向け市場品質支援の事業仮説メモ。

本リポジトリは、以下の問いを整理するための作業メモである。

- ECU故障予測は Vehicle Health Management 市場で課金価値を持つか
- EPS / ステアリング制御系は、フリート向け・OEM向けのどちらに価値があるか
- ECUサプライヤ側から提案可能な範囲はどこまでか
- 「ログをもっと出す」以上の企画にするにはどう見せるべきか
- 最終的に Project Charter として何を提案すべきか

## Current Conclusion

現時点の結論は、**「ECU故障予測」そのものを売るのは弱い**というもの。

より現実的には、以下の方向性が有望。

> EPS / ステアリングECUにおいて、DTCだけでは不足する内部状態・一時異常・使用条件を診断エビデンスとして残し、OEM / Tier1間の市場不具合解析・原因候補分類・品質説明を支援する。

つまり、現時点では以下のように整理する。

| 観点 | 結論 |
|---|---|
| エンドユーザ向け故障警告 | 弱い |
| フリート向けEPS単体予兆 | 頻度が低く弱い |
| OEM向け市場リスク監視 | 価値はあるがOEM依存が強い |
| ECUサプライヤ発の提案 | 診断エビデンス提供が現実的 |
| AIモデル | 直接の故障予測ではなく原因候補分類・解析支援が現実的 |
| 最初の企画名候補 | Steering Diagnostic Evidence Package |

## Directory Structure

```text
docs/
  00_context.md
  01_business_model_options.md
  02_option_comparison.md
  03_supplier_scope.md
  04_project_charter_diagnostic_evidence.md
  05_risks_and_open_questions.md
  06_next_actions.md
```

## Suggested Repository Name

候補:

- `steering-health-intelligence`
- `steering-diagnostic-evidence`
- `eps-diagnostic-intelligence`
- `steering-risk-notes`

現時点では、事業企画メモとして始めるなら `steering-diagnostic-evidence` が一番ブレにくい。
