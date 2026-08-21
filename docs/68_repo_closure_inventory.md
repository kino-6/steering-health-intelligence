# Repoを閉じるかどうかの棚卸し

> Trust recovery correction:
> この文書は、旧テーマ、motion health、RDI切り出しまでの棚卸しとしては有用だが、Kaggle / Public Proxyによる予測的付加価値探索の最新判断としては使わない。
> 後続レビューで、EPS内部状態、DTC、freeze frame、交換結果が見えないことをKaggle/Public Proxy系の主Kill理由にしてはいけないと補正した。
> 最新判断は [docs/96_predictive_value_internal_fact_correction.md](96_predictive_value_internal_fact_correction.md)、信用回復監査は [docs/97_trust_recovery_rule_check_audit.md](97_trust_recovery_rule_check_audit.md) を参照する。
> 修正後は、`PVC001`、`ULC008`、`ULC004`、`PVC004` を公開proxy価値の検証候補として残す。

## 結論

現行条件のままなら、このRepoの主探索はArchiveにして閉じてよい。

ここで閉じる対象は、EPSサプライヤ向けに、公開情報だけを使って、新しい外販商材を見つける探索である。
市場変化は複数見つかったが、どれも購買需要、既存業務との差分、EPSサプライヤの部品境界での独自価値まで届かなかった。
特に、内部資料を使わない方針では、既存DTC、freeze frame、extended data、HILS、safety case、診断仕様、RFQ回答との差分を確認できない。

ただし、Repoを「失敗」として捨てるのではなく、次の3つに分けて閉じるのがよい。

1. EPS製品価値の外販探索はArchiveにして閉じる
2. Kill知識ベースとして保存する
3. 前提変更または新テーマがある場合だけ、別テーマとして再開する

旧テーマとして、現時点で外販商品として売りに行くものはない。
追加で検証した自動運転・商用車両群向けの操舵系運行可否/点検優先度判断も、外販テーマとしてはArchiveする。
残るのは、内部資料を使える場合の再開条件、特定案件の短期整理支援、または製造品質/EOL検査の別テーマである。

旧テーマArchive後の新しい入口は [docs/archive/motion_health/69_old_theme_archive_and_new_focus.md](archive/motion_health/69_old_theme_archive_and_new_focus.md) に置いた。
その後、MHQ001〜005を検証し、最終判断は [docs/archive/motion_health/75_motion_health_mhq001_final_decision.md](archive/motion_health/75_motion_health_mhq001_final_decision.md) に置いた。
さらにMHQ002/004/006/007/008/009/010も [docs/archive/motion_health/76_other_mhq_20min_deep_dive.md](archive/motion_health/76_other_mhq_20min_deep_dive.md) で確認した。
MHQ004/007/008については、[docs/archive/motion_health/77_mhq004_007_008_deeper_review.md](archive/motion_health/77_mhq004_007_008_deeper_review.md) で追加深掘りし、外販ではなく再開条件として残す判断にした。
結論は、fleet downtime需要はあるが、data accessと既存remote diagnosticsとの差分を公開情報だけでは証明できないため、EPS/SbWサプライヤ単独の外販テーマとしてはStop / Archiveである。

ただし、次の作業仮説として [docs/archive/oem_remote_diagnostics/78_oem_remote_diagnostics_eps_explanation_layer_hypothesis.md](archive/oem_remote_diagnostics/78_oem_remote_diagnostics_eps_explanation_layer_hypothesis.md) を切り出した。
これはfleet監視サービスではなく、OEM remote diagnostics networkに組み込まれる操舵系状態説明レイヤーである。
過去のmotion health調査は [docs/archive/motion_health/79_motion_health_archive_index.md](archive/motion_health/79_motion_health_archive_index.md) にArchiveし、新仮説の背景知識としてだけ使う。

## 何を判断しているか

判断しているのは、これ以上このRepoで公開情報ベースのEPS製品価値探索を続けるべきかである。

判断対象は以下である。

- EPS故障予測や劣化兆候通知
- ECU追加ログやevent memory
- 公開市場painのscenario library
- RCA / 8D向けcase pack
- EPS診断・評価coverage benchmark
- steering ECU cyber / SBOM / CVE evidence
- steer-by-wire向け説明資料整理
- SOVD / 次世代診断コンテンツ整理
- public recall / ODI / TSB monitor
- Kaggle/Bosch型の製造品質・評価時間短縮
- 自動運転・商用車両群向けの操舵系運行可否 / 点検優先度判断

判断対象外は以下である。

- 内部資料を使える特定programの実務支援
- OEM/fleet/service dataを使う別テーマ
- EPSではなく製造品質分析サービスとしての別テーマ
- 調査会社として公開情報モニタを売る別テーマ

## 市場需要

市場需要そのものは複数ある。

- EPSではloss of assist、警告灯、低速高操舵、intermittent assist loss、software/failsafeなどの困りごとが公開市場に出る
- steer-by-wireでは、異常時状態、冗長性、運転者警告、診断、software update、認証説明の重要性が増える
- SOVD / ISO 17978系では、診断が近接整備、リモート、車内、software update、logging、fault informationへ広がる
- 製造品質や評価時間短縮は、Bosch型やMercedes-Benz型のKaggle課題から需要シグナルがある

しかし、このRepoが必要としていたのは、市場変化ではなく、EPSサプライヤが外部サービスとして買う理由である。
そこまでは公開情報だけでは届かなかった。

## 未解決の痛み

公開情報だけで確認できた痛みは、主に市場側または標準・規制側の痛みである。
EPSサプライヤ側の未解決業務として確定できたものは少ない。

公開情報から見えた痛み:

- 市場ではEPSのdriver-visible painが繰り返し起きる
- SbWでは異常時説明が複数部署にまたがる
- 次世代診断では、classic ECUの診断コンテンツもAPI化・リモート化の波に入る
- 製造・EOL・評価では、不良候補や試験時間の絞り込み需要がありそう

公開情報だけでは見えなかった痛み:

- 対象EPSの既存DTCやfreeze frameで何が足りないか
- 既存HILS、bench、release reviewとの差分
- 既存safety caseやCSMS/TARA/SBOM運用との差分
- OEM RFQや顧客技術説明で実際に詰まっている質問
- 診断設計担当が既にやっている作業との差分
- 予算を持つ買い手

## 仮説ごとの棚卸し

詳細TSVは [data/repo_closure_inventory.tsv](../data/repo_closure_inventory.tsv) に置いた。
ここでは意思決定に必要な粒度だけまとめる。

| 枝 | 現行判断 | 閉じる理由 | 残すなら |
|---|---|---|---|
| EPS故障予測 / 劣化兆候通知 | Kill | OEM/fleet/service data、故障ラベル、外部要因が必要 | OEM/fleet/service dataを使える別テーマ |
| ECU追加ログ / event memory | Kill | DTC、freeze frame、extended data、DEM/UDS、NvMと被る | 不足fieldと転記先帳票が確認できた場合 |
| Public market scenario library | Kill as product | 公開事例整理だけでは事例紹介になる | 設計質問、診断質問、禁止主張の入力 |
| RCA / 8D case pack | Kill as main | 案件依存、OEM依存、内部資料依存が強い | 炎上案件や滞留案件の短期支援 |
| Coverage Benchmark | No-Go / Stop | 既存HILS/DTC/freeze frame/reviewとの差分を内部資料なしで示せない | 内部資料を使える場合だけ再開 |
| Coverage Benchmark SaaS / HIL tool | Kill | 既存HIL/SIL/diagnostic toolingが強い | 既存ツールに入らない横断gapが確認できた場合 |
| Cyber / SBOM / CVE evidence | Kill寄り | 既存CSMS/TARA/SBOM/CVE/ISO21434/R155/R156業務が厚い | steering ECU固有のOEM回答翻訳 |
| SbW説明資料整理 | No-Go | 市場変化はあるが安全・認証・診断・ソフト更新・顧客説明の既存業務に飲まれる | 特定案件で既存資料をOEM向け1枚へつなぐ支援 |
| SOVD / 次世代診断 | No-Go as product | SOVD基盤、API、authoring、API検証、trainingは既存ツール領域 | EPS診断コンテンツの公開範囲・権限整理だけ |
| Public recall / ODI / TSB monitor | Kill as product | 市場シグナル整理だけでは有料価値が弱い | 他成果物の入力 |
| Kaggle/Bosch出荷前品質 | Branch only | 製造品質・EOL検査・評価運用でありEPS製品価値ではない | 製造品質分析サービスとして別テーマ化 |
| 自動運転・商用車両群向け操舵系運行可否 / 点検優先度判断 | Stop / Archive as external offer | data accessがOEM/fleet/platform契約依存で、既存remote diagnosticsもDTC severity、action plan、API連携、診断時間短縮を既に扱う | 特定OEM programでEPS/SbW固有data fieldとservice outcome、既存診断との差分を確認できる場合 |

## 解決策

このRepoの次の解決策は、新しい商品を追加で探すことではない。
閉じるなら、次の形にする。

1. READMEとAGENTSの現在地を、閉じた判断に寄せる
2. Kill知識ベースを最初に読む資料として固定する
3. 再開条件を3つだけ残す
4. Kaggle/Bosch線を別テーマへ切り出すか、枝として保留する
5. generated demoや古いBest5が最新仮説に見えないよう、historical扱いを明記する

## 買い手 / 利用者

この棚卸しの利用者は、外部顧客ではない。
利用者は、このRepoを次に読む本人、次のLLM、またはEPSサプライヤ向け新規テーマを再検討する人である。

利用者が得る判断は、次の3つである。

- 現行条件で続けるべきか
- どの仮説を再提案してはいけないか
- 前提が変わった場合、どこから再開するか

## Why supplier can play

EPSサプライヤが現行条件で持てる手札は、非常に狭い。

持てる可能性があるもの:

- 部品境界内のDTC、DID、freeze frame、extended data、software/calibration ID、security access
- HILS、bench、release review、安全・診断・サイバー成果物
- OEM説明やRFQ回答へ転記できる確認済み事実

ただし、これらは公開情報では確認できない。
また、多くは既存の診断設計、安全設計、品質保証、CSMS、評価業務の中に持ち主がいる。
したがって、現行方針のままでは、EPSサプライヤが外部から買う新規価値としては弱い。

## EPS supplier conclusion

EPSサプライヤとして売ること:

> 現行条件では売らない。公開情報だけでは、既存診断、既存評価、既存安全、既存品質、既存サイバー業務との差分を示せないためである。

EPSサプライヤとして実施できること:

> 内部資料を使える場合だけ、対象EPSのHILS試験名、関連DTC、freeze frame / extended data、既存レビュー会議体を見て、既存業務との差分を確認する。

EPSサプライヤとして言ってはいけないこと:

> 故障予測、劣化兆候通知、保証費削減、root cause断定、OEM保証DBなしの市場判断、SOVD基盤提供、汎用SbW安全支援を主張しない。

初期対象外:

> OEM保証DB、fleet analytics、サービスツール、車両クラウド、SOVD server、ODX/UDS変換ツール、HIL/SILツール、CSMS/TARA/SBOM代替は初期対象外に置く。

次に見せる部署:

> 閉じる判断としては、事業開発またはテーマ探索の責任者に見せる。再開する場合だけ、diagnostic engineering、functional safety、software/calibration、customer technical interfaceに見せる。

## Demo

このRepoには、デモやproxy artifactがかなり残っている。
ただし、どれも商品価値の証明ではなく、Stop判断の材料として扱う。

- 公開市場pain分類: 市場入力にはなるが単体商品ではない
- FAM08 coverage sample: 内部DTC/HILS資料なしでは差分判定できない
- SbW 1ケースsample: 既存safety caseの要約に見えるならStop
- 次世代診断25件表: 既存DTC/DID表やODX authoringの整形に見えるならStop
- Kaggle/Bosch proxy demo: 製造品質・EOL検査の別テーマであり、EPS製品価値ではない

## What not to claim

- このRepoで外販商材が見つかった
- 公開情報だけでEPS診断不足を証明できた
- SbWやSOVDなら買い手がいる
- Kaggle/Bosch線がEPS製品価値になる
- Public recall / ODI / TSB monitorが単体商品になる
- 内部資料なしでCoverage Benchmarkを売れる
- Killした仮説を名前だけ変えて復活できる

## Kill criteria

このRepoを閉じる条件は、すでにほぼ満たしている。

- 公開情報だけでは、既存DTC/freeze frame/extended dataとの差分を示せない
- 公開情報だけでは、既存HILS/bench/release reviewとの差分を示せない
- 公開情報だけでは、既存safety case、CSMS、TARA、SBOM、SOVD toolingとの差分を示せない
- 買い手の業務成果物へ直接転記できる強い外販offerが残っていない
- 残る案が、特定案件支援、内部資料前提、または別テーマに縮んでいる

閉じない条件は、次のいずれかだけである。

- 内部資料を少し使える
- OEM/fleet/service dataを使う前提に変える
- 製造品質/EOL検査/評価時間短縮を別テーマとして切り出す
- 自動運転・商用車両群向けに、操舵系の運行可否/点検優先度判断を新テーマとして切り出す場合は、docs/75の再開条件を満たす
- 外販ではなく、サプライヤ内LLM知識ベースやレビュー補助として目的を変える

## CoVe

| 検証質問 | 回答 | Confidence | 判断への反映 |
|---|---|---|---|
| 本当に全枝を見たか | 主要枝はREADME、Kill知識ベース、docs/35-67、data/llm_kill_knowledge_base.tsvにまとまっている | High | 閉じる判断の棚卸しとして十分 |
| 市場需要まで否定していないか | 否定していない。市場需要はあるが、購買需要とEPSサプライヤ差分が見えない | High | 「市場がない」ではなく「現行条件では売れない」と書く |
| まだProceed候補はないか | 外販Proceed候補はない。残るのは内部資料前提、特定案件支援、別テーマ | High | 主探索は閉じる |
| Kaggle/Bosch線は残すべきか | 残すなら別テーマ。EPS製品価値ではなく製造品質・EOL検査 | Medium | Repo主仮説から外す |
| SOVD/次世代診断は閉じすぎか | content mapだけは特定programで残るが、外販商品ではない | Medium | No-Go as product / content map only |
| 閉じることで失うものは何か | 公開情報ベースの追加探索機会。ただし同じKillに戻る可能性が高い | Medium | 追加探索より知識ベース保存を優先 |

## 推奨判断

推奨は、**主探索をClose** である。

より正確には、次の状態にする。

> EPSサプライヤ向けに、公開情報だけで外販できるEPS製品価値を探す探索はArchiveしてClose。追加で見た自動運転・商用車両群向けの操舵系運行可否/点検優先度判断も、外販テーマとしてはStop / Archive。RepoはKill知識ベースとして保存。再開は、内部資料を使える場合、OEM/fleet/service前提に変える場合、製造品質/EOL検査の別テーマに切る場合、またはdocs/75の再開条件を満たす特定OEM programがある場合だけ。

次にやるなら、READMEの冒頭に「このRepoは現行条件ではClose判断済み」と明記し、generated demoや古いBest5が最新提案に見えないようにする。
