# OEM remote diagnostics / RDI archive

## 状況

このArchiveは、OEM遠隔診断に組み込む操舵系状態説明レイヤーの探索を閉じるための置き場である。

市場需要はある。
OEM remote diagnostics、fleet service、service engineeringでは、DTC後のseverity判断、action plan、service routing、診断時間短縮の需要がある。

ただし、内部資料を使わない現行ルールでは、EPS/SbWサプライヤが公開情報だけで外販テーマにできる差分は残らなかった。
差分の核になるEPS/SbW固有DID、freeze frame、assist / limit state、thermal indicators、software / calibration ID、service note転記先、service outcome feedbackが、公開情報だけでは埋まらないためである。

## 最終判断

RDIは、公開情報だけでProceedできる外販テーマとしては **Stop / Archive** とする。

残す知見は次の通り。

- DTC説明、severity、action plan、service routingだけなら既存remote diagnosticsが強い。
- 差分が出るなら、追加DID読み順、注意文、禁止主張、service note転記である。
- service outcome feedbackが戻らないと、説明ロジックの改善loopにならない。
- EPS/SbWサプライヤは、走行安全、運行可否、交換時期、root causeを断定しない。
- 再開できるのは、特定OEM programでEPS/SbW固有data fieldとservice outcomeが使える場合だけである。

## 主要ファイル

- [78 hypothesis](78_oem_remote_diagnostics_eps_explanation_layer_hypothesis.md)
- [80 validation plan](80_oem_remote_diagnostics_validation_plan.md)
- [81 RDI001-006 research](81_rdi001_006_research_report.md)
- [82 RDI006 sample](82_rdi006_thermal_limit_4_column_sample.md)
- [83 program gap PDCA](83_rdi006_program_gap_pdca.md)

## Kaggleへ移る理由

RDIは内部program依存の壁に当たった。
一方で、Kaggleは内部資料を使わずに、企業が外に出した問題設定から業務意図を読むことができる。

そのため、次の探索はRDIではなく、Kaggle problem-setting lensを使い、製造品質、EOL検査、評価時間短縮の隠れた需要を読む方向へ移す。
