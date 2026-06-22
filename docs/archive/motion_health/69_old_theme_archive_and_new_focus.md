# 旧テーマArchiveと新しい検証焦点

## 結論

旧テーマはArchiveにする。

ここでいう旧テーマは、乗用車向けEPS単体について、公開情報だけを使い、故障予測、劣化兆候通知、追加ログ、公開市場pain分類、Coverage Benchmark、汎用SbW説明支援、SOVD基盤支援を外販商材にできるかを探した一連の探索である。
この方向は、現行条件では閉じる。

新しく見るなら、問いを変える。

> 電動パワーステアリング単体の寿命を当てるのではなく、自動運転車両、配送車、商用車、シャトルなどの車両群で、操舵系を含む重要部品について、次の運行に出してよいか、次回点検まで持つか、先に入庫させるべきかを判断できるか。

この新テーマは、EPS単体の故障予測ではない。
目的は、安全機能を予測で代替することではなく、車両群を止めないために、運行可否、点検優先度、診断時間短縮、交換準備、実使用条件からの品質改善へつなげることである。

## 何をArchiveするか

Archiveするもの:

- 乗用車EPS単体の残寿命予測
- 個人ユーザー向けのEPS劣化兆候通知
- 追加ログやevent memoryそのものを売る案
- 公開recall / ODI / TSB monitor単体
- 公開市場pain scenario library単体
- 内部資料なしのCoverage Benchmark
- SOVD server、SOVD基盤、ODX/UDS変換ツール支援
- 汎用SbW safety / cyber / redundancy evidence pack
- steering ECU cyber / SBOM / CVE management汎用支援

Archiveしないもの:

- Kill知識ベース
- 内部資料を使える場合の再開条件
- 製造品質 / EOL検査 / 評価時間短縮の別テーマ
- 自動運転・商用車両群向けの操舵系運行可否 / 点検優先度判断

## なぜ旧テーマを閉じるか

旧テーマは、市場需要そのものが無かったから閉じるのではない。
閉じる理由は、EPSサプライヤが公開情報だけで外販商材にできる差分が見えなかったためである。

分かったこと:

- EPSは安全重要部品だが、通常の乗用車では寿命内に壊れないよう設計される
- 異常時は、予測ではなくDTC、警告、fail-safe、診断仕様、安全設計で扱う
- EPS単体の故障予測には、fleet data、service data、保証ラベル、交換結果、故障ラベルが必要になる
- それらの多くはOEM、fleet運営者、サービス領域にある
- 公開情報だけでは、対象EPSの既存DTC、freeze frame、extended data、HILS、safety caseとの差分を確認できない

したがって、旧テーマを続けると、同じKill理由に戻る可能性が高い。

## 新しい問い

新テーマの自然言語の問いは次である。

> 自動運転車両や商用車両群で、操舵系の状態を見て、次の運行に出してよい車、先に点検すべき車、交換準備すべき部品、診断に時間がかかりそうな車を早めに分けられるか。

以後この整理を、必要な場合だけ `操舵系の運行可否 / 点検優先度判断` と呼ぶ。
ただし、最初から商品名にしない。

## 市場需要

新テーマの需要は、安全性よりも、稼働停止コストと整備判断にある。

想定される利用場面:

- 自動運転シャトルを翌日の運行に出せるか判断する
- 配送車や商用車のうち、操舵系を先に点検すべき車両を選ぶ
- 警告やDTCが出た車両について、整備士が最初に読む情報を絞る
- SbWや高可用操舵で、冗長系の一部低下を運行判断へつなげる
- 実使用条件で操舵系に厳しい使われ方を見つけ、次の製品改善へ戻す

公開情報上も、Nexteerはsteering、chassis components、tiresを含むhealth monitoringを、fleet downtime低減、maintenance scheduling、診断時間短縮と結びつけて説明している。
Boschもfleet vehicleのhealth status、maintenance planning、early warningをcloud and predictive diagnosticsとして説明している。

## 未解決の痛み

まだ確認すべき痛みは、以下である。

1. 操舵系理由の運行停止や入庫判断が、自動運転・商用車両群で本当に痛いか
2. DTCや通常診断だけでは、運行可否や点検優先度を決めるには遅い、または粗いか
3. EPS / SbWサプライヤが、運行データ、DTC、DID、整備履歴、交換結果にアクセスできるか
4. 買い手はOEMなのか、fleet運営者なのか、サプライヤのサービス部門なのか
5. 「交換時期を当てる」より、「次回点検まで運行可 / 先に入庫」の判断の方が買われるか

## 仮説

EPSサプライヤは、EPS単体の寿命予測ではなく、自動運転・商用車両群向けに、操舵系を含む重要部品の運行可否、点検優先度、診断時間短縮、交換準備を支援できるかもしれない。

この仮説では、EPSは単独商品ではなく、SbW、ブレーキ、足回り、タイヤ、電源、通信などと一緒に見る。
また、出力も「何km後に壊れる」ではなく、「次の運行に出してよい」「次回点検まで様子見」「先に入庫」「交換部品を準備」「診断でこのDIDを読む」である。

## 解決策

最初に作るものは、予測モデルではない。
まず作るのは検証質問表である。

対応TSV:

- [data/archive/motion_health/motion_health_new_focus_questions.tsv](../../../data/archive/motion_health/motion_health_new_focus_questions.tsv)

この表では、以下を確認する。

- どの利用者の業務判断か
- どの公開情報またはRepo内根拠があるか
- 何が分かれば続けるか
- 何が分かればKillするか
- 旧テーマへ戻らないための注意点

## 買い手 / 利用者

初期候補は、個人ユーザーではない。

候補:

- 自動運転シャトル / ロボタクシー運営者
- 配送車 / 商用車fleet運営者
- 商用車OEMのfleet service部門
- EPS / SbWサプライヤの品質・サービス・診断部門
- dealer / remote diagnostics部門

最初に確認すべき買い手は、fleet運営者ではなく、OEMまたはサプライヤ内のfleet service / diagnostics / customer technical interfaceでよい。
理由は、EPSサプライヤが直接fleet運用データに触れられるとは限らないためである。

## Why supplier can play

EPS / SbWサプライヤが持てる可能性のある手札:

- 操舵系のDTC、DID、freeze frame、extended data
- motor current、assist state、limit state、thermal state、voltage、communication state
- software / calibration ID
- HILS / bench / durabilityで見た異常時状態
- SbW冗長系、degraded state、fail-operational stateの知識
- OEMやfleetへ説明できる診断・整備判断の自然言語化

ただし、運行データ、整備履歴、交換結果、故障ラベルはOEM/fleet/service側にある可能性が高い。
ここにアクセスできないなら、この新テーマも旧テーマと同じ理由で止まる。

## EPSサプライヤとしての言い方

言ってよいこと:

> EPS単体の寿命を断定するのではなく、操舵系を含む車両状態から、運行可否、点検優先度、診断で読むべき情報を出せるかを検証する。

まだ言ってはいけないこと:

> EPS交換時期をリアルタイムで正確に予測できる、故障を防げる、保証費を削減できる、安全機能を予測で代替できる、とは言わない。

次に見る最小項目:

> 自動運転・商用車両群で、操舵系理由の運行停止、予定外入庫、診断時間、部品待ち、再発確認がどれくらい痛いか。

## Kill条件

以下なら新テーマも止める。

- 操舵系理由の運行停止や入庫判断がfleetで大きな痛みではない
- DTCや通常診断だけで運行可否・点検優先度が十分判断できる
- EPS / SbWサプライヤが運行データ、整備履歴、交換結果にアクセスできない
- 買い手がOEM/fleet/service側に固定され、サプライヤが主語になれない
- 出力が「交換時期予測」だけになり、整備判断へ転記できない
- 故障予測、保証費削減、root cause断定に戻る

## CoVe

| 検証質問 | 現時点の回答 | Confidence | 反映 |
|---|---|---|---|
| 旧テーマをArchiveしてよいか | よい。閉じる理由はdocs/68とdata/repo_closure_inventory.tsvに整理済み | High | 旧テーマはArchive |
| EPSは新テーマに入るか | 入る。ただしEPS単体ではなく、操舵系やchassis healthの一部として入る | Medium | 新テーマはEPS単体寿命予測にしない |
| 需要の芯は安全か | 安全だけではない。稼働停止、入庫判断、診断時間、整備計画が芯 | Medium | 出力を運行可否/点検優先度へ変更 |
| サプライヤが主語になれるか | 未確認。運行データと整備履歴へのアクセスが最大の壁 | Unknown | 最初の検証質問にする |
| 旧テーマへ戻る危険はあるか | ある。交換時期予測や保証費削減と言い始めると戻る | High | 禁止主張を明記 |

## 次アクション

次は、[data/archive/motion_health/motion_health_new_focus_questions.tsv](../../../data/archive/motion_health/motion_health_new_focus_questions.tsv) の上から順に、公開情報とRepo内根拠で確認する。
最初に見るのは技術実現性ではなく、操舵系理由の運行停止・入庫判断が本当に買い手の痛みかである。
