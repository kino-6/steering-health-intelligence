# Trust Recovery Rule Check Audit

## 結論

今回の信用回復Actionとして、過去の主要な `Stop`、`Kill`、`Archive`、`No-Go` 系の報告を、追加した上位ルールで再監査した。

結果は、全部を破棄する必要はない。
ただし、Kaggle / Public Proxy 系の一部報告は、旧ロジックに引っ張られていたため、最新判断として使ってはいけない。

最も重要な修正はこれである。

> EPS内部状態、DTC、freeze frame、交換結果が見えないことを、Kaggle / Public Proxy 系の主Kill理由にしてはいけない。

このルールに照らすと、前回の「Kaggleにあったネタは全滅」という判断は誤りだった。
最新判断は [docs/96_predictive_value_internal_fact_correction.md](96_predictive_value_internal_fact_correction.md) であり、`PVC001`、`ULC008`、`ULC004`、`PVC004` は公開proxy価値の検証候補として残す。

一方で、motion health、RDI、Steer-by-wire、SOVDの過去結論は、すぐ破棄する必要はない。
それらの多くは「内部事実がないから全部Kill」ではなく、買い手、既存業務、責任境界、OEM/platform依存を理由にしている。
ただし、新しい `Mandatory Rule Check` より前に作られたため、次に引用する場合はRule Checkを添える。

監査表は [data/trust_recovery_rule_check_audit.tsv](../data/trust_recovery_rule_check_audit.tsv) に置く。

## 何を判断しているか

判断しているのは、過去報告を今後の意思決定に使ってよいかである。

今回の目的は、過去の結論を擁護することではない。
どの報告が上位ルールに耐えていて、どの報告が補正済みで、どの報告を再引用する前に再確認すべきかを分けることである。

## 適用した上位ルール

今回のRule Checkで使った上位ルールは、[AGENTS.md](../AGENTS.md) の次の節である。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Kaggle / Public Proxy Predictive Value Rule`
5. `Mandatory Rule Check Before Stop / Kill / Archive`

特に重要なのは、`Mandatory Rule Check Before Stop / Kill / Archive` である。
今後、`Stop`、`Kill`、`Archive`、`No-Go`、`全滅`、`閉じる` と書く前に、上位ルールに照らしたRule Checkが本文にない場合、その結論はdraft扱いにする。

## 監査結果

### 最新判断として使う

| 対象 | 判断 | 理由 |
|---|---|---|
| [docs/96_predictive_value_internal_fact_correction.md](96_predictive_value_internal_fact_correction.md) | 最新判断として使う | Kaggle/Public Proxy系で内部事実不足を主Kill理由にしないよう補正している |
| [data/predictive_value_corrected_status.tsv](../data/predictive_value_corrected_status.tsv) | 最新ステータスとして使う | `PVC001`、`ULC008`、`ULC004`、`PVC004` を検証候補として戻している |
| [AGENTS.md](../AGENTS.md) | 上位ルールとして使う | Mandatory Rule Checkを追加済み |

### 補正前として扱う

| 対象 | 判断 | 理由 |
|---|---|---|
| [docs/95_predictive_value_continue_final_decision.md](95_predictive_value_continue_final_decision.md) | 最新判断として使わない | Kaggle/Public Proxy系を閉じる判断が強すぎた |
| [docs/93_predictive_value_id_status_inventory.md](93_predictive_value_id_status_inventory.md) | 最新判断として使わない | `Continue` を消す方向に寄りすぎ、内部事実不足を主Kill理由にしすぎた |
| [docs/68_repo_closure_inventory.md](68_repo_closure_inventory.md) | Kaggle/Public Proxy最新判断には使わない | 旧テーマ棚卸しとしては使えるが、docs/96の補正を反映していない |
| [docs/61_llm_kill_knowledge_base.md](61_llm_kill_knowledge_base.md) | Kaggle/Public Proxyについては補正付きで使う | Kaggle例外が製造品質/EOL/評価時間に寄っており、使用条件classの先読み候補を反映していない |

### Rule Check付きで再引用する

| 対象 | 暫定判断 | 理由 |
|---|---|---|
| [docs/archive/motion_health/75_motion_health_mhq001_final_decision.md](archive/motion_health/75_motion_health_mhq001_final_decision.md) | 暫定維持 | fleet remote diagnostics系では、データアクセスと既存remote diagnosticsとの差分が価値の中心なので、内部/契約データ不足は妥当なGate。ただしRule Check未記載 |
| [docs/archive/oem_remote_diagnostics/83_rdi006_program_gap_pdca.md](archive/oem_remote_diagnostics/83_rdi006_program_gap_pdca.md) | 暫定維持 | RDI系は仮説自体がprogram data / service workflow依存なので、DTC/freeze frame/service outcome不足は妥当なGate。ただしRule Check未記載 |
| [docs/60_sbw_explanation_support_no_go_reasoning.md](60_sbw_explanation_support_no_go_reasoning.md) | 暫定維持 | No-Go理由は既存安全・認証・診断・顧客説明業務との重複が中心。ただしRule Check未記載 |
| [docs/67_next_generation_diagnostic_content_value_check.md](67_next_generation_diagnostic_content_value_check.md) | 暫定維持 | No-Go理由はSOVD基盤/ツール領域との差分不足と買い手pain未確認が中心。ただしRule Check未記載 |

## 修正した使い方

### Kaggle / Public Proxy

補正前:

> EPS内部状態やDTC、freeze frame、交換結果が見えないため、Kaggle/Public Proxy系は全滅。

補正後:

> EPS内部状態やDTC、freeze frame、交換結果が見えないことは、故障予測や原因断定を禁止する境界である。しかし、それだけで公開proxy価値をKillしてはいけない。使用条件class、路面・操舵context、通信異常contextがEPSサプライヤの業務成果物へ転記できるかを見る。

残す候補:

1. `PVC001`: 使用負荷classの先読み
2. `ULC008`: 駐車場、低速、大舵角、凹凸
3. `ULC004`: 荒れた路面と操舵
4. `PVC004`: 通信異常contextの説明境界

### Motion Health / RDI

この系統は、Kaggle/Public Proxyと同じ扱いにしない。

motion healthやRDIは、そもそもremote diagnostics、OEM program、service workflow、service outcomeへ組み込む仮説である。
したがって、データアクセスやservice outcomeが見えないことは、主Kill理由として妥当な場合がある。

ただし、次に引用する時は必ず次を明示する。

1. その仮説は公開proxy価値の話ではなく、OEM/fleet/service workflowへ組み込む話である
2. なぜデータアクセスやservice outcomeが価値の中心なのか
3. 既存remote diagnosticsとの差分がどこに残るのか
4. EPSサプライヤとして何を言ってはいけないか

### SbW / SOVD

SbWやSOVDのNo-Go判断は、主に既存業務との重複が理由である。
これは今回のKaggle/Public Proxy誤りとは別の論点である。

ただし、これらも新しいRule Checkより前の文書である。
次に引用する場合は、単に「No-Go」と書かず、以下を添える。

1. 市場需要は何か
2. 誰の既存業務と重なるのか
3. EPSサプライヤの部品境界で残る可能性は何か
4. それでも外販商品にしない理由は何か

## CoVe

| 検証質問 | 回答 | Confidence | 反映 |
|---|---|---:|---|
| 過去報告は全部信用不能か | No。Kaggle/Public Proxy系の全滅判断が主な破綻点。ほかは暫定維持できるがRule Check未記載。 | Medium | 全破棄ではなく分類監査にした |
| Kaggle/Public Proxyは全滅か | No。`PVC001`、`ULC008`、`ULC004`、`PVC004` は検証候補として残す。 | High | docs/96を最新判断にした |
| 内部事実不足を常にKill理由にしてはいけないのか | No。Kaggle/Public Proxyでは主Kill理由にしない。RDIやmotion healthのように仮説自体がdata/workflow依存ならGateになる。 | High | 系統別に判断を分けた |
| docs/68はそのまま使えるか | 部分的。旧テーマ棚卸しには使えるが、Kaggle/Public Proxy最新判断としては使わない。 | High | correction bannerを追加する |
| docs/61はそのまま使えるか | 部分的。Kill知識ベースとして使うが、Kaggle例外ルールはdocs/96で補正する。 | High | correction blockを追加する |

## 次の検収ルール

今後、過去報告または新規報告を意思決定に使う場合、次の扱いにする。

1. Rule Checkがない `Stop / Kill / Archive / No-Go / 全滅` 結論はdraft扱い
2. Kaggle/Public Proxy系では、内部事実不足を主Kill理由にした結論は無効
3. 旧テーマ、motion health、RDI、SbW、SOVDは、それぞれの上位ルールと仮説特性に照らして個別に判断する
4. 最新判断として使う文書は、READMEとAGENTSに入口を置く
5. 補正前文書には、必ず補正先への導線を置く

## EPSサプライヤとしての言い方

言ってよいこと:

> 過去報告のうち、Kaggle/Public Proxy系には上位ルール違反があったため補正した。最新判断では、公開proxyから使用条件classや通信異常contextを先読みまたは分類する候補は残る。ただし、故障予測、交換時期、安全保証、保証費削減、root cause断定は言わない。

まだ言ってはいけないこと:

> 過去報告は全部正しい。

> Kaggleにあったネタは全滅。

> EPS内部事実が見えないから公開proxy価値はない。

> Rule CheckなしのStop/Kill/Archive結論を最終判断として使える。
