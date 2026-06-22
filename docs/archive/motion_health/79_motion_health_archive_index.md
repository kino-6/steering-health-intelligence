# Motion Health調査Archive Index

## 目的

このArchiveは、motion health / fleet運行可否 / 点検優先度の調査結果を捨てずに保存するための索引である。

結論は、EPS/SbWサプライヤ単独のfleet監視サービスや故障予測サービスとしてはStop / Archiveである。
ただし、新しい仮説である「OEM遠隔診断に組み込む操舵系状態説明レイヤー」の背景知識としては使える。

Archiveを読むときの注意:

- ここにある資料は、外販fleet監視サービスのProceed証拠ではない
- fleet downtime需要やremote diagnostics需要は示すが、EPS/SbWサプライヤ単独の買い手を示すものではない
- 使える知見は、既存remote diagnosticsとの差分、必要data field、service outcome依存、禁止主張である

## Archive Summary

| Area | 残す知見 | 新仮説への使い方 | 主な資料 |
|---|---|---|---|
| MHQ001 | fleet downtime需要はあるが、steering-only購買pain、data access、既存診断との差分が弱い | 単独fleet監視ではなくOEM network内contentに切る理由 | docs/72, docs/73, docs/75 |
| MHQ003 / MHQ005 | data accessはOEM/fleet/platform依存、既存remote diagnosticsは強い | network参加と既存diagnostics差分を検証質問にする | docs/74, data/archive/motion_health/motion_health_mhq003_005_evidence.tsv |
| MHQ004 | 価値ある出力は交換時期ではなく、運行可否、入庫優先度、診断読み順、部品準備 | 説明レイヤーの出力rubricとして使う | docs/77, data/archive/motion_health/motion_health_mhq004_007_008_deeper.tsv |
| MHQ007 | EPS単独ではなくmotion/chassis bundleで見る方が市場に合う | OEM network内でsupplier-owned steering contributionを分ける | docs/77 |
| MHQ008 | 実使用条件から品質・開発へ戻す価値はある | field-to-engineering feedback条件として使う | docs/77 |
| Kill sample | DTCだけ、既存remote diagnostics、supplier domain triageの差分は内部data前提 | 新仮説の1ケースsampleの土台にする | data/archive/motion_health/motion_health_mhq001_final_kill_check_sample.tsv |

## Reading Order

1. [docs/archive/oem_remote_diagnostics/78_oem_remote_diagnostics_eps_explanation_layer_hypothesis.md](docs/archive/oem_remote_diagnostics/78_oem_remote_diagnostics_eps_explanation_layer_hypothesis.md): 新しい作業仮説。まずこれを読む。
1. [docs/archive/motion_health/75_motion_health_mhq001_final_decision.md](docs/archive/motion_health/75_motion_health_mhq001_final_decision.md): 旧motion health外販テーマを閉じた理由。
1. [docs/archive/motion_health/74_mhq003_005_deep_dive_for_mhq001.md](docs/archive/motion_health/74_mhq003_005_deep_dive_for_mhq001.md): data accessと既存remote diagnostics差分の壁。
1. [docs/archive/motion_health/77_mhq004_007_008_deeper_review.md](docs/archive/motion_health/77_mhq004_007_008_deeper_review.md): 残すべき知見。output rubric、bundle boundary、field-to-engineering feedback。
1. [data/archive/motion_health/motion_health_archive_links.tsv](../../../data/archive/motion_health/motion_health_archive_links.tsv): source linkと使い方の一覧。

## Archived Documents

| Document | Status | Use |
|---|---|---|
| docs/archive/motion_health/69_old_theme_archive_and_new_focus.md | Historical | 旧テーマからmotion healthへ切った入口 |
| docs/archive/motion_health/70_motion_health_mhq001_005_research_report.md | Historical evidence | MHQ001-005の初期source整理 |
| docs/archive/motion_health/71_mhq001_005_timeboxed_item_deep_dive.md | Historical evidence | MHQ001-005のitem別初期結論 |
| docs/archive/motion_health/72_mhq001_20min_deep_dive.md | Historical evidence | MHQ001の最初の深掘り |
| docs/archive/motion_health/73_mhq001_second_20min_deep_dive.md | Historical evidence | MHQ001をProceedからHoldへ下げた判断 |
| docs/archive/motion_health/74_mhq003_005_deep_dive_for_mhq001.md | Active archive input | data access / remote diagnostics差分の壁 |
| docs/archive/motion_health/75_motion_health_mhq001_final_decision.md | Active archive input | motion health外販Stopの最終判断 |
| docs/archive/motion_health/76_other_mhq_20min_deep_dive.md | Active archive input | 他MHQによるStop補強 |
| docs/archive/motion_health/77_mhq004_007_008_deeper_review.md | Active archive input | 新仮説に再利用する3知見 |

## Reusable Knowledge

新仮説で使ってよい知見:

- End userやfleet側には、downtime、診断時間、部品準備、入庫優先度の痛みがある
- 既存remote diagnosticsはDTC、severity、action plan、API連携をかなり扱う
- EPS/SbWサプライヤの価値は、fleet monitoring全体ではなく、component-specific explanationにある可能性がある
- 説明には、EPS内部data field、OEM network参加、service outcome feedbackが必要である
- safety guarantee、root cause断定、交換時期予測、既存remote diagnostics置換は言ってはいけない

新仮説で使ってはいけない主張:

- 公開情報だけでEPS/SbWサプライヤがfleet向け外販商品を作れる
- steering-only購買painが強い
- DTCを優先度付けするだけで差分がある
- EPS内部データがOEM networkに上がると確認済み
- service outcome feedbackが取れると確認済み

## Sources

詳細sourceは [data/archive/motion_health/motion_health_archive_links.tsv](../../../data/archive/motion_health/motion_health_archive_links.tsv) に置く。
