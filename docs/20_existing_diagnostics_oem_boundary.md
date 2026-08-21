# 20. Reality Check: Existing Diagnostics and OEM Boundary

## Purpose

直近の議論で、`EPS / ECU embedded evidence` はかなり危うい表現だと分かった。

理由は単純で、ECU内に診断証跡を残す仕組みは既に長く使われているからである。

このメモでは、既存診断との差分、OEM領分、サプライヤ側で持てる手札、外部市場調査で見えたこと・見えなかったことを整理する。

## Current Conclusion

> 内蔵証跡そのものは既存。価値があるとすれば、既存診断データをEPSサプライヤの返却品解析、NTF、顧客品質報告、原因調査に使える形へ棚卸し・再設計・提案すること。

ただし、これもOEM領分に半分入る。
サプライヤ単独のプロダクトとして売るには弱い。

より現実的な入口は、次のような設計支援または内部解析支援である。

> EPS Warranty / NTF Case Backlog Analysis

または:

> EPS Diagnostic Evidence Design Review for Customer Quality

## Existing Diagnostics Already Cover A Lot

次は既存診断の範囲にある。

- DTC
- freeze frame / snapshot data
- extended data
- event memory
- occurrence counter
- aging counter
- operation cycle / ignition cycle
- voltage / temperature / mileageなどの環境情報
- NvM保存
- UDS ReadDTCInformation
- AUTOSAR DEM

したがって、`ECU内に証跡を残す` と言っているだけなら新規性はない。
それは既存診断仕様の言い換えである。

## OEM Boundary

多くの重要領域はOEM主導である。

| 領域 | 主導者 | サプライヤ単独でできるか |
|---|---|---|
| DTC体系、DID、ODX、診断仕様 | OEM主導、Tier1共同 | 難しい |
| サービスツールで何を読むか | OEM主導 | 難しい |
| 保証DB、修理履歴、苦情、走行条件との紐付け | OEM | ほぼ不可 |
| 市場品質解析ワークフロー | OEM / Tier1品質部門 | 単独では不可 |
| EPS ECU内部monitor設計、freeze frame候補、extended data候補 | EPS / ECUサプライヤ | 可能 |
| 返却品解析時に読むサプライヤ内部ツール | EPS / ECUサプライヤ | 可能 |
| OEMに提案する診断証跡パッケージ | EPS / ECUサプライヤ | 可能 |
| 顧客品質報告に使う事実整理テンプレート | EPS / ECUサプライヤ | 可能 |

## What Not To Say

避けるべき言い方:

> EPSの市場不具合解析データ基盤を提供します。

理由:

- OEMの保証DB、サービス履歴、市場品質ワークフローが必要
- サプライヤ単独ではデータ権限がない
- 既存DEM/UDS診断との差分が曖昧

避けるべき言い方:

> EPSの8D回答を自動化します。

理由:

- 8Dは顧客指定フォーマットや責任分界が絡む
- 根本原因の断定は責任問題になる
- 証拠が弱いと逆に不利になる
- NTFでは `断定不可` が正しい場合もある

## Better Framing

より通りが良い言い方:

> EPSサプライヤの過去NTF / 返却品 / 再現不能案件を棚卸しし、現行DTC / freeze frame / extended dataで足りなかった証跡を分類し、NVM制約内で追加すべき最小証跡セットと顧客品質報告向けの事実整理を作る。

さらに短く言うなら:

> EPS返却品・NTF案件の診断証跡棚卸しと改善提案。

## Supplier-Side Hand

OEMに無手で聞きに行くのは弱い。
先にサプライヤ側で持つべき手札は次。

| 手札 | 価値 |
|---|---|
| 過去の市場不具合・返却品・NTFケース分類 | サプライヤで困っている論点を定義できる |
| 現行DTC / freeze frame / extended dataの棚卸し | 既存診断の限界をサプライヤ視点で示せる |
| 解析不能だったケースの原因リスト | どの証拠が足りないかを具体化できる |
| EPS failure mode x 必要証跡マップ | OEMに何を入れたいか提案できる |
| NVM制約内の最小証跡セット案 | 実装可能性を持った提案になる |
| DTCだけ vs 追加証跡ありの顧客品質報告サンプル | 効果を見せられる |
| コスト / リスク / 誤判定 / 責任境界の整理 | OEMが嫌がる論点を先回りできる |

## What Market Research Showed

外部市場調査で見えたこと:

| 分かったこと | 粒度 |
|---|---|
| NTF / 返却品解析 / warranty analyticsは市場痛みとして存在する | 業務レベル |
| DTC、診断データ、返却品、修理履歴、ナラティブを組み合わせたい需要がある | データカテゴリレベル |
| supplier quality / 原因調査 / 顧客品質報告に証拠が必要 | ワークフローレベル |
| OEMデータや保証DBはサプライヤ単独では触りにくい | 権限レベル |

## What Market Research Did Not Show

外部市場調査では見えていないこと:

| 見えていないこと | なぜ難しいか |
|---|---|
| EPS返却品で実際に多いNTFパターン | 各社の品質・保証内部データ |
| DTCだけで解析不能だった実例 | 非公開の不具合解析情報 |
| freeze frame / extended dataに何が入っていて、何が足りないか | OEM / サプライヤ / 車種ごとの診断仕様 |
| 電源・熱・センサ・制御努力・使用条件・一過性異常のどれが効くか | 実案件とECU仕様を突き合わせないと分からない |
| 20-50件のケース分類 | 社内返却品・市場不具合台帳が必要 |

したがって、`電源・熱・センサ・制御努力・使用条件・一過性異常` という分類は、現時点では市場調査で確認された答えではない。
内部案件レビューを始めるための仮分類である。

## Correct Next Research

外部市場調査で次にできること:

1. 公開リコール / 不具合事例からEPS系の故障モードを分類する
2. warranty analytics / supplier qualityツールの出力形式を比較する
3. 顧客品質報告や原因調査支援の一般的な証拠構造を調べる

ただし、これでも `どのfreeze frameが不足していたか` までは見えない。

内部一次調査でないと無理なこと:

1. サプライヤEPSの返却品・市場不具合・NTF分類
2. 現行DTC / freeze frame / extended dataの不足分析
3. NVM制約内で何を残すべきか
4. 証跡が解析リードタイムや説明力を改善するか
5. 顧客品質報告で通る表現か

## Proposed Internal Review

最初の実施単位:

> 過去20-50件のEPS返却品・市場不具合・NTF・再現不能案件を棚卸しする。

見る項目:

1. どんな症状だったか
2. DTCはあったか
3. freeze frame / extended dataは読めたか
4. 返却品単体で再現したか
5. 解析が止まった理由は何か
6. 何が分かれば解析が進んだか
7. それはECU内部で保存可能だったか
8. OEMデータが必要だったか
9. 次の診断仕様に入れる価値があるか

この結果が出るまで、`EPS Event Context Memory` や `EPS Warranty Evidence Option` は仮説に留める。

## Revised Business Judgment

現時点の実現性:

| 案 | 実現性 | 判断 |
|---|---:|---|
| OEM横断の市場品質データサービス | 低 | OEMデータ・保証DB・サービス運用が必要 |
| EPSサプライヤ単独の故障予測サービス | 低 | データも責任も足りない |
| EPS診断証跡の設計レビュー | 中 | サプライヤ内部の設計・品質ノウハウで始められる |
| 返却品解析用のサプライヤ内部reader / report generator | 中 | 読み出し権限と現場導入があれば可能 |
| OEM RFQ / design review向けの診断証跡提案パッケージ | 中 | OEM承認は必要だが、提案材料としては成立する |
| 過去NTF / 返却品ケースのbacklog analysis | 中-高 | 内部データがあれば最も現実的な第一歩 |

## Sources

- AUTOSAR Diagnostic Event Manager: https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_DiagnosticEventManager.pdf
- UDS ReadDTCInformation overview: https://uds.readthedocs.io/en/stable/pages/knowledge_base/service.html
- AIAG Automotive Warranty Management Key Terms: https://aiag.org/docs/default-source/quality/aiag-cqi-14-warranty-key-terms.pdf
- AIAG Global Automotive Warranty Report: https://www.aiag.org/docs/default-source/Quality-/global_auto_wrnty_rpt.pdf
- AWM Warranty Data Analysis: https://www.awm-warranty-management.com/services/warranty-data-analysis/
