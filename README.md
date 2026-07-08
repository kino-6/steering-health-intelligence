# Steering Health Intelligence Notes

EPS / ステアリングECUを起点に、ECU内部信号からhealth / stress / control-effort indicatorを作る事業仮説メモ。

## 現在の状態

旧テーマはArchive扱いにする。

ここでいう旧テーマは、乗用車向けEPS単体について、公開情報だけを使い、故障予測、劣化兆候通知、追加ログ、公開市場pain分類、Coverage Benchmark、汎用SbW説明支援、SOVD基盤支援を外販商材にできるかを探した一連の探索である。
現行条件では、この方向は閉じる。

追加で見た自動運転・商用車両群向けの操舵系運行可否 / 点検優先度判断も、EPS/SbWサプライヤ単独の外販テーマとしてはArchiveする。
最終判断は [docs/archive/motion_health/75_motion_health_mhq001_final_decision.md](docs/archive/motion_health/75_motion_health_mhq001_final_decision.md) に置く。

結論は、市場需要はあるが、EPS/SbWサプライヤが公開情報だけで外販商品にできる差分は確認できない、である。
必要データはOEM/fleet/platform契約に依存し、既存remote diagnosticsもDTC severity、action plan、API連携、診断時間短縮をすでに扱っている。

ただし、新しい作業仮説として、OEM remote diagnostics networkに組み込む操舵系状態説明レイヤーは切り出す。
これはfleet監視サービスではなく、EPS/SbW内部データからDTCだけでは分からない状態説明、追加DID読み順、禁止主張、field-to-engineering feedbackを作る部品側コンテンツである。
入口は [docs/archive/oem_remote_diagnostics/78_oem_remote_diagnostics_eps_explanation_layer_hypothesis.md](docs/archive/oem_remote_diagnostics/78_oem_remote_diagnostics_eps_explanation_layer_hypothesis.md) に置く。
過去のmotion health調査は [docs/archive/motion_health/79_motion_health_archive_index.md](docs/archive/motion_health/79_motion_health_archive_index.md) へArchiveする。

Kaggle / 公開proxyによる予測的付加価値探索については、後続レビューで補正済みである。
「EPS内部状態、DTC、freeze frame、交換結果が見えないから全滅」という判断は撤回する。
最新判断は [docs/96_predictive_value_internal_fact_correction.md](docs/96_predictive_value_internal_fact_correction.md)、信用回復監査は [docs/97_trust_recovery_rule_check_audit.md](docs/97_trust_recovery_rule_check_audit.md) に置く。
修正後は、`PVC001`、`ULC008`、`ULC004`、`PVC004` を公開proxy価値の検証候補として残す。
補正後のビジネスモデル本線は [docs/98_business_model_mainline_after_correction.md](docs/98_business_model_mainline_after_correction.md) に置く。

## 上位ルール

最初に前提を固定する(詳細は `AGENTS.md` の `Personal Public-Only Research Rule`):

- この活動は**現段階では仕事(所属組織の業務)ではない**。個人の事業仮説研究である
- **内部情報・内部資料は使わない。使う予定もない。** 内部依存の判断は「境界の記録」として文書に残すだけで、次アクションにしない
- 成果物の宛先は**技術者**。Demoは「公開logから人間には読み取れない兆候を機械的に読み取り、SOTIFへ部品側として参加できる形」を見せる

このRepoでは、以後の調査・仮説・デモ・ドキュメント更新を必ず以下の順で提示する。

> 市場需要 -> 未解決の痛み -> 仮説 -> 解決策 -> 買い手/利用者 -> 初期提供物 -> 検証方法 -> Kill条件

悪い提示:

> EPSにこういう公開事例がある。

良い提示:

> 市場ではloss of assist、低速高操舵、警告灯+DTC、intermittent assist loss、stop-start、software/failsafeなどのEPS共通pain familyが繰り返し問題化している。EPSサプライヤは、各scenarioに対して既存DTC/freeze frame/extended data、reader、HILS/bench評価がどこまで説明・再現できるかをCoverage Benchmarkとして提示できる。

### 自然言語優先

レポートや結論では、造語、商品名、略称、phase名を先に出さない。
必ず先に、自然言語で以下を説明する。

- 何を判断しているのか
- 誰のどの業務の話なのか
- 何が分かれば進み、何が分かれば止めるのか
- 既存業務、既存診断、既存評価と何が違う可能性があるのか

悪い提示:

> P1 paid assessmentとしてCoverage BenchmarkはNo-Go。P0 ScreeningだけProceed。

良い提示:

> 現時点では、有償サービスとして売りに行く段階ではない。内部資料を使わない前提では、対象EPSのHILS試験名、関連DTC、freeze frame / extended data項目、既存レビュー会議体を見られず、既存レビューとの差分を示せないためである。これらの4項目は、内部資料を使える条件になった場合だけの再開条件として扱う。

`Coverage Benchmark`、`P0`、`P1`、`Evidence Pack`、`Readiness`、`screening` のような言葉は使ってよい。
ただし、自然言語で意味を説明した後にだけ使う。

過去の探索メモはhistoricalとして扱う。
`EPS故障予測`、`劣化兆候通知`、`Health-ready EPS`、`ECU追加ログ`、`Market Pain Scenario Library単体`、`RFQ / Design Review Pack単体` は、最新結論ではない。
`RCA / 8D Evidence Case Pack` は単独主商品から下げる。
`EPS Diagnostic / Robustness Coverage Benchmark` も、内部資料を使わない現行方針ではNo-Goとして止める。

旧テーマの最終局面では、公開されている規制、標準、業界動向から、EPSサプライヤ側に実務負荷が増えている領域を探していた。
その時点の探索対象は以下の3つだったが、深掘り後は汎用外販商品としてはどれも弱い。

1. Steer-by-wire safety / cybersecurity / redundancy
2. SOVD / next-generation diagnostics content design for EPS
3. Public recall / ODI / TSB monitor as input only

その時点で残していたのは、Steer-by-wireの汎用安全支援でも、SOVD基盤支援でもない。
既存の安全・サイバー・診断・software update成果物を、OEM説明、RFQ回答、診断コンテンツ設計に転記しやすくするcomponent-boundary整理だけである。

## EPSサプライヤ視点

このRepoの結論は、必ずEPSサプライヤの立場に帰着させる。

市場、OEM、エンドユーザ、サービス、connected platform、規制、公開データをメタ視点で見るのはよい。
ただし、最終判断は以下で締める。

- EPSサプライヤとして何を売るか
- EPSサプライヤとして何を実施できるか
- EPSサプライヤとして何を言ってはいけないか
- OEM領域、サービス領域、fleet platform領域として初期対象外に置くものは何か
- 次にEPSサプライヤ内のどの部署に見せるか

当初はEPS故障予測やVehicle Health Managementを検討していたが、現在は以下の順で仮説が進化している。

```text
EPS故障予測
  -> EPS単体の個車RULは頻度・責任・データ面で弱い

EPS Health Intelligence Package
  -> EPSをhealth-aware subsystemとして差別化する

Development Evaluation First
  -> まず開発・耐久評価でECU信号ベースの指標価値を検証する

Common ECU Hardware Health Layer
  -> EPS固有メカ指標から、より横展開しやすいECU共通hardware healthへ広げる

Existing Diagnostics / OEM Boundary Check
  -> DTC、freeze frame、extended data、DEM/UDSは既存。価値があるなら、サプライヤ内部のNTF/返却品ケース棚卸しから不足証跡を特定する方向へ修正する

Public Proxy Data Reset
  -> 内部NTF/返却品ケースにアクセスできない前提に修正。公開市場情報、NHTSA、Kaggle、公開CAN datasetで補える範囲に限定する

Market Demand To Warranty / RCA Evidence
  -> 公開事例やscenario card単体ではなく、NTF、返却品解析、保証claim、SCAR/8D、顧客品質説明で使えるproduct-side evidence readinessへ軸を修正する

EPS Common Pain Productization
  -> RCA/8D単体はドメイン固有でスケールしにくい。公開市場で繰り返すEPS共通pain familyを、既存診断・reader・HILS/bench評価のcoverage benchmarkへ変換する
```

## 旧テーマの最終判断

旧テーマについては、以下を最終判断として扱う。

> Coverage Benchmarkは、内部資料なしでは止める。広いcyber/SBOM商品も既存業務・既存ツールと被るためKill寄りに下げる。Steer-by-wireの汎用説明支援も有償サービスとしてはNo-Go。SOVD / 次世代診断は基盤ではなく、EPS診断コンテンツの公開範囲・権限・禁止主張が製品仕様やRFQ回答に残るかだけをKill-firstで見る。

さらに旧テーマのメタ結論として、現行条件では外販ビジネスとしてProceedできる強い手札はほぼ残っていない。
次にこのRepoを読むLLMは、まずKill知識ベースを前提にすること。
過去にKillした仮説を、名前だけ変えて再提案しない。

Kaggle/Bosch線は、需要調査の枝としては有用だった。
ただし、これは製造品質、EOL検査、工程改善の話であり、EPS製品そのものの付加価値ではない。
したがって、Repoの主仮説にはしない。
本題に戻る場合は、EPS製品仕様、診断仕様、制御仕様、評価仕様、OEM説明に残る価値だけを主探索にする。

`ECU内に証跡を残す` こと自体は既存診断の範囲にあるため、新規性として扱わない。
`TARA/SBOM/CVE管理をやる` ことも既存CSMS/ISO21434/R155/R156対応と被るため、新規性として扱わない。
価値が残るとすれば、EPSサプライヤがcomponent boundaryで説明責任を持てる範囲を、OEM説明、設計レビュー、RFQ回答、診断コンテンツ設計に転記できる形にすることである。
Steer-by-wireでは、この範囲が従来EPSより広がる可能性がある。
ただし、公開情報を追加収集した結果、SbWの安全・認証・診断論点はNHTSA、VCA、R79、ASAM SOVDで既にかなり扱われている。
したがって、公開情報だけで有償offerへ進める判断はしない。
深掘り後の結論は、Steer-by-wire向けの汎用説明資料整理支援も有償サービスとしてはNo-Goである。
市場変化はあるが、異常時説明、安全設計、認証、診断、ソフト更新、顧客説明は既存業務の中に既に持ち主がいるためである。
次に見るなら、EPSサプライヤが持つDTC、DID、freeze frame、extended data、software/calibration ID、routine、security accessを、近接整備、リモート診断、車内診断、製造、開発の利用場面ごとに、公開/制限/禁止へ整理できるかを見る。
それが既存診断仕様やODX authoringの言い換えで終わるなら、SOVD / 次世代診断方向もStopする。

重要な境界:

- OEMの市場fleetデータ、保証DB、苦情DB、車両クラウドを初期前提にしない
- OTAやremote diagnosticsは主商品ではなく、読み出しチャネルの一つ
- 個車RULやエンドユーザ故障通知は初期主張にしない
- まずはEPSサプライヤが責任を持てるcomponent-levelの説明範囲に収める
- OEMデータ接続やfleet analyticsはOptional extensionに置く
- OEMに無手で聞きに行くのではなく、EPSサプライヤ側で持てる診断仕様、software/calibration ID、security access、fail-safe / degraded state、HILS/bench評価、公開市場scenarioから仮説を作ってから検証する
- `8D回答` という曖昧な言い方は避け、RCA/8Dや顧客品質報告は副次artifactとして扱う

## 現在の焦点

| 観点 | 現在の見立て |
|---|---|
| 最新判断 | 旧テーマ、単独fleet監視型motion health、RDI / OEM remote diagnostics説明レイヤーは外販商品としてArchive。Kaggle / 公開proxyによる予測的付加価値探索は、前回の全滅判断を補正し、PVC001 / ULC008 / ULC004 / PVC004を検証候補として残す |
| EPS向け軸 | 個車のEPS残寿命や交換時期を当てるとは言わない。OEMが想定する車両用途や使われ方を、操舵要求、路面・振動exposure、使用負荷class、通信異常contextなどのEPS側確認観点へ翻訳できるかを見る |
| 最終検証軸 | EPS内部状態、DTC、freeze frame、交換結果が見えないことを主Kill理由にしない。評価するのは、OEM用途想定をEPSサプライヤの製品企画、診断企画、品質改善、評価企画、顧客技術説明へ翻訳できるか |
| 近い商品名 | まだ作らない。自然言語では「OEM用途想定をEPS側の確認観点へ翻訳する検証候補」。外販商品ではなく検証候補である |
| RCA/8Dの扱い | 主商品ではない。特定programの短期支援で、確認済み事実の転記先になる場合だけ |
| Primary target | EPSサプライヤの商品企画、製品企画、診断企画、品質改善、評価企画。製造品質、EOL検査、評価時間短縮は別枝または補助材料として扱う |
| 初期データ前提 | 内部資料は使わない。Kaggleの公開課題を、データセットそのものではなく、外に出された問題設定と公開proxyとして読む |
| OEM / fleetデータ | 使わない。OEM保証DB、fleet data、service outcomeを必要とする方向へ戻さない |
| AI / 予測 | 予測のような付加価値を探索する。ただし個車RUL、交換時期、安全保証、保証費削減、root cause断定は主張しない。Kaggle精度競争ではなく、予測対象がEPSサプライヤの価値へ転記できるかを見る |
| 避ける主張 | EPS交換時期の正確予測、安全機能の代替、保証費削減断定、root cause断定、サプライヤ単独fleet監視 |
| Kaggle/Bosch線 | 公開データそのものではなく、外に出された問題設定から隠れた需要を読む観点として使う。Bosch型の製造品質 / EOL検査、Mercedes型の評価時間短縮は現テーマ外。KGL003/005/006/007/008は、OEM用途想定をEPS側確認観点へ翻訳するための公開proxy入力として残す |
| Bosch公開シグナル | BoschのAct-by-Wire、Vehicle Motion Management、Motion integration platform、AI/SDV公開情報は、EPS故障予測の根拠ではない。ただし、by-wire / motion-domain時代に、上位制御から操舵側へ来る要求を、EPSサプライヤの受け入れ境界、制限境界、診断境界、禁止主張へ翻訳する必要が増える可能性を示す |
| Bosch予測診断シグナル | 2026年のBosch / Uptake発表とBosch Predictive Diagnosticsでは、fleet / connected vehicle / cloud diagnostics文脈でAI-driven predictive maintenance、vehicle health、component-specific load and diagnostic featuresが明確に出ている。このブランチでは、steering predictive diagnostics / predictive maintenance / vehicle healthを正面から扱う |
| 次アクション | `ULC008` を最有力、`ULC004` を二番手、`PVC004` を境界候補として、OEM用途想定をどの業務成果物へ翻訳できるかを確認する。加えて、Bosch公開シグナルを受けて、上位motion controllerから来る操舵要求の受け入れ境界と、steering predictive diagnostics / predictive maintenance / vehicle healthの対象を確認する。4枚の最小パックは `docs/100`、質問票は `docs/101`、Bosch motion枝は `docs/102`、Bosch予測診断枝は `docs/103`、操舵系predictive state候補は `docs/104`、Bosch予測ビジネス分析は `docs/105`、screening計画は `docs/106`、Phase 1/2結果は `docs/107`、Proceed深掘りは `docs/108`、Phase 3 data boundaryは `docs/109`、Phase 4 supplier workflow fitは `docs/110`、Phase 5 screening decisionは `docs/111`、継続候補の並列深掘りは `docs/112`、見込み候補の深掘りは `docs/113`、SPD別の一定結論は `docs/114`、SPD008/SPD002のartifactと比較判断は `docs/115`〜`docs/117`、SPD008 first samplesは `docs/118`、観点補正は `docs/119`、predictive value checkは `docs/120`、power monitor 1ケースは `docs/121`、payload sampleは `docs/122`、program別照合質問シートは `docs/123`、communication input validityの独立ケースは `docs/124`、未検証デルタのファクトチェックは `docs/125`、SOTIFへの乗り方の判定は `docs/126` に切り出した。SOTIFはプロセス支援商品としてはNo-Go、SOTIF運用フェーズのフィールド監視への部品側インプット(SPD008 payloadの宛先追加)としてだけ条件付き検証候補に残す。入口条件はKQ1(SOTIF由来のfault未満監視要求が部品側RFQへ実際に降りてきているか)であり、確認できるまで工数を割かない。故障予測はKill維持。最終判断は、SPD008を次の本線候補、SPD002をreference demoに置く(SPD002は `docs/125` で意図的凍結を明文化)。デルタ検証の結果、価値主張は「既存monitorでは残らない」ではなく「既存標準(AUTOSAR Dem)は残す設定余地を持つが、機能影響との同時性や閾値未満eventの再発は残らない設計が多く、EPSサプライヤがcomponent boundaryで設計できる」に言い直した。`docs/123` の質問シートのprogram固有欄の回答取得は、内部資料(対象programの診断仕様)への接触が必要なため、次アクションに置かず、内部資料を使える条件になった場合だけの実施条件として保存する(Coverage Benchmark / SbWと同じ扱い)。ターゲットケース(permanent DTCが残らない断続的なassist低下)の公開実在確認は `docs/127` で完了し、Confirmedとした(Ford 15V-340是正手順の「DTCなし」経路、GM 17V-414の約1秒の一時喪失・突然復帰、GM TSB 17-NA-158の外部signal起因操舵警告、Tesla EA24001の過電圧起因ほか)。さらに `docs/129` で、判定ゲートの照合対象を「自社program」から「公開リコール是正実務」へ組み替え、Ford 15S18とGM 17276のディーラー向け一次文書を精読した結果、5項目中4項目の差分(DTC未満event、snapshot利用、同時性、再発がいずれも是正実務に存在せず、判断はDTC有無の1bitのみ)を公開レベルでConfirmedした。これによりSPD008 power monitorは「公開レベルConfirmed付き限定Proceed」となり、内部資料条件は仮説検証ではなく実行のみ(現行世代の自社設定確認=`docs/123` 質問シート、2部署以上の使い道確認、SOTIF KQ1)に縮小した。`docs/130` では同じ手法を第二候補のcommunication input validityに適用し、GM TSB 17-NA-158の原文(無効な冷却水温signal→操舵警告→「U0401:71でgearを交換するな」という公式警告と誤交換の記録)により、Hold→「公開レベルConfirmed付き限定Proceed(第二候補)」へ引き上げた。このTSBの内容はSPD008 payloadと同一のfield構成であり、SPD008は「OEMが誤交換の後に人手で書くservice文書を、部品側がruntimeで機械的に出せるようにする」提案だと言い直せる。副産物として、Ford SSM 49530(2021年F-150、始動時電圧8V未満→内部故障系code U3000:96保存→PSCM交換不要とOEMが説明)により、現行世代でもpower contextの誤帰属が続いていることを確認した。EPS RUL/交換時期予測やBosch型fleet platformとしてはProceedしない。内部事実の不足だけでKillしない |

## 推奨読書順

まず読むなら、この順番が分かりやすい。

1. [docs/61_llm_kill_knowledge_base.md](docs/61_llm_kill_knowledge_base.md): 次のLLMが最初に読む前提知識。Kill済み仮説、再提案禁止、再開条件、前提変更時にだけ復活する候補を整理。
1. [data/llm_kill_knowledge_base.tsv](data/llm_kill_knowledge_base.tsv): Kill済み仮説ごとの現行判断、Kill理由、再主張禁止、再開条件、LLM向けルール。
1. [docs/97_trust_recovery_rule_check_audit.md](docs/97_trust_recovery_rule_check_audit.md): 信用回復監査。過去のStop/Kill/Archive報告を上位ルールで再監査し、最新判断として使う文書、補正前として扱う文書、Rule Check付きで再引用する文書を分類。
1. [data/trust_recovery_rule_check_audit.tsv](data/trust_recovery_rule_check_audit.tsv): 信用回復監査のTSV。各文書のcurrent use status、Rule Check status、main issue、corrected use、action takenを整理。
1. [docs/98_business_model_mainline_after_correction.md](docs/98_business_model_mainline_after_correction.md): 補正後のビジネスモデル本線。故障予測ではなく、OEM用途想定をEPSサプライヤの製品企画・診断企画・品質改善・評価企画・顧客技術説明へ翻訳できるかを見る固定スコープassessmentとして整理。
1. [data/business_model_mainline_after_correction.tsv](data/business_model_mainline_after_correction.tsv): 補正後ビジネスモデル本線の市場需要、痛み、仮説、解決策、買い手、初期offer、Proceed/Kill条件、禁止主張、次アクションを整理。
1. [docs/100_oem_usage_translation_minimum_pack.md](docs/100_oem_usage_translation_minimum_pack.md): OEM用途想定をEPS側の確認観点、提案観点、説明境界へ翻訳する4枚の最小パック。製品企画、診断企画、品質改善/評価企画、診断企画/サイバー担当の順で社内レビューする。
1. [data/oem_usage_translation_minimum_pack.tsv](data/oem_usage_translation_minimum_pack.tsv): 4枚の最小パックのartifact別TSV。decision question、OEM入力、public proxy role、EPS supplier output、Proceed/Kill signal、禁止主張、最初のレビュー質問を整理。
1. [docs/101_oem_usage_translation_review_questions.md](docs/101_oem_usage_translation_review_questions.md): 4枚の最小パックを社内で確認する質問票。最初は製品企画と診断企画に絞り、既存RFQ回答、既存診断、既存評価との差分が出るかを見る。
1. [data/oem_usage_translation_review_questions.tsv](data/oem_usage_translation_review_questions.tsv): 質問票のTSV。question、聞く理由、期待成果物、Proceed signal、Kill signal、禁止主張、Yes/No時の次アクションを整理。
1. [docs/102_bosch_motion_domain_ai_signal_review.md](docs/102_bosch_motion_domain_ai_signal_review.md): Bosch公開情報を、EPS故障予測ではなく、by-wire / motion-domain時代の操舵側説明責任が増えるシグナルとして整理したレビュー。
1. [data/bosch_motion_domain_ai_signal_review.tsv](data/bosch_motion_domain_ai_signal_review.tsv): Bosch公開情報のソース別TSV。public signal、公開されていること、EPSサプライヤへの含意、禁止主張、次の検証質問を整理。
1. [docs/103_bosch_predictive_diagnostics_meaning_review.md](docs/103_bosch_predictive_diagnostics_meaning_review.md): Boschが言う予測を、fleet predictive maintenance、Predictive Diagnostics、Cloud and predictive diagnostics、AI cockpitに分解し、steering predictive diagnostics / predictive maintenance / vehicle healthとして扱う条件を整理したレビュー。
1. [data/bosch_predictive_diagnostics_meaning_review.tsv](data/bosch_predictive_diagnostics_meaning_review.tsv): Bosch予測診断シグナルのソース別TSV。prediction type、予測対象、入力feature、出力action、EPSサプライヤ含意、禁止主張、次の質問を整理。
1. [docs/104_steering_predictive_state_candidate_scan.md](docs/104_steering_predictive_state_candidate_scan.md): Boschの予測語をこのブランチでは正面から扱い、公開サービス情報やNHTSA資料から、steering predictive state候補を整理した調査。
1. [data/steering_predictive_state_candidates.tsv](data/steering_predictive_state_candidates.tsv): steering predictive state候補のTSV。熱保護、低/高電圧、過温度、外部signal異常、複合電気症状、DTC coverage、DTC履歴について、材料、予測価値、用途、禁止主張、次checkを整理。
1. [docs/105_bosch_predictive_business_analysis.md](docs/105_bosch_predictive_business_analysis.md): Boschの予測ビジネスを、接続、クラウド診断、predictive diagnostics、predictive maintenance、vehicle health、整備計画、保証・品質判断までの業務パッケージとして再整理した分析。
1. [data/bosch_predictive_business_analysis.tsv](data/bosch_predictive_business_analysis.tsv): Bosch予測ビジネスの層別TSV。fleet maintenance、cloud diagnostics、predictive diagnostics、data-driven intelligence、Uptake、battery、brake、powertrain、connectivityをEPSサプライヤ含意へ変換。
1. [docs/106_steering_predictive_diagnostics_screening_plan.md](docs/106_steering_predictive_diagnostics_screening_plan.md): 次アクション実施計画。Bosch公式ソースURLを固定し、操舵系predictive diagnostics候補をstate、必要データ、整備action、vehicle health output、禁止主張へ切る手順を整理。
1. [docs/107_steering_predictive_diagnostics_state_screening.md](docs/107_steering_predictive_diagnostics_state_screening.md): Phase 1/2の実行結果。Bosch型予測ビジネス要求を操舵系screening要求へ変換し、SPS001-SPS007をmaintenance action、vehicle health output、diagnostic triage、quality/warranty investigationへ並べ替えた。
1. [data/steering_predictive_diagnostics_screening_requirements.tsv](data/steering_predictive_diagnostics_screening_requirements.tsv): Bosch予測ビジネスのBBA001-BBA010を、操舵系screening requirementへ変換したTSV。
1. [data/steering_predictive_diagnostics_state_screening.tsv](data/steering_predictive_diagnostics_state_screening.tsv): 操舵系predictive state候補のscreening TSV。Proceed / Hold / dependency、Bosch output fit、禁止主張、次checkを整理。
1. [docs/108_steering_predictive_diagnostics_proceed_deep_dive.md](docs/108_steering_predictive_diagnostics_proceed_deep_dive.md): Proceed候補の深掘り。SPD002、SPD004、SPD003、SPD001、SPD007の順で、EPSサプライヤが定義できること、OEM/fleet/platform依存、vehicle health output、maintenance action、Hold/Kill riskを整理。
1. [data/steering_predictive_diagnostics_proceed_deep_dive.tsv](data/steering_predictive_diagnostics_proceed_deep_dive.tsv): Proceed深掘りTSV。各stateのwhy proceed、必要依存、提案output、次artifactを整理。
1. [docs/109_steering_predictive_diagnostics_data_boundary.md](docs/109_steering_predictive_diagnostics_data_boundary.md): Phase 3結果。Proceed候補5件について、必要DTC、freeze frame / extended data、limit state、温度・電源・通信context、repair feedback loop、EPSサプライヤが言えること/言えないことを整理。
1. [data/steering_predictive_diagnostics_data_boundary.tsv](data/steering_predictive_diagnostics_data_boundary.tsv): Phase 3 data boundary TSV。各stateの必要データ、OEM/fleet/platform依存、RUL/交換時期を言わない境界、次checkを整理。
1. [docs/110_steering_predictive_diagnostics_supplier_workflow_fit.md](docs/110_steering_predictive_diagnostics_supplier_workflow_fit.md): Phase 4結果。Phase 3のdata boundaryを、診断企画、品質改善、顧客技術説明、service / aftermarket連携、製品企画、評価企画の成果物へ転記できるかを確認。
1. [data/steering_predictive_diagnostics_supplier_workflow_fit.tsv](data/steering_predictive_diagnostics_supplier_workflow_fit.tsv): Phase 4 supplier workflow fit TSV。部署別の成果物、価値、重複リスク、Proceed signal、Hold/Stop signal、禁止主張、次stepを整理。
1. [docs/111_steering_predictive_diagnostics_screening_decision.md](docs/111_steering_predictive_diagnostics_screening_decision.md): Phase 5最終判断。操舵系predictive diagnosticsは、固定スコープの内部/顧客技術向けassessmentとしてProceed。EPS RUL/交換時期予測、Bosch型fleet platform、安全保証、root cause / warranty cost reductionはProceedしない。
1. [data/steering_predictive_diagnostics_screening_decision.tsv](data/steering_predictive_diagnostics_screening_decision.tsv): Phase 5 decision TSV。Market demand、未解決の痛み、仮説、解決策、買い手、EPSサプライヤの手札、Demo、Kill criteriaを整理。
1. [docs/112_steering_predictive_diagnostics_parallel_continuation_deep_dive.md](docs/112_steering_predictive_diagnostics_parallel_continuation_deep_dive.md): 継続候補の並列深掘り。SPD002/003/004/001/007に加え、内部重要モジュールruntime deviation案をSPD008として扱い、E2E製品全体ではなく内部モジュール単位に限定して検証する方針を整理。
1. [data/steering_predictive_diagnostics_parallel_continuation.tsv](data/steering_predictive_diagnostics_parallel_continuation.tsv): 並列深掘りTSV。各候補の自然言語の問い、継続理由、module scope、E2Eにしない理由、成果物、Proceed signal、Hold/Stop signal、禁止主張を整理。
1. [docs/113_steering_predictive_diagnostics_promising_candidate_deep_dive.md](docs/113_steering_predictive_diagnostics_promising_candidate_deep_dive.md): 見込み候補の深掘り。SPD008を伸びしろ、SPD002を実証しやすさ、SPD003を実務価値、SPD004をvehicle health接続として整理し、SPD001/007も状況と判断理由を明示。
1. [data/steering_predictive_diagnostics_promising_candidate_deep_dive.tsv](data/steering_predictive_diagnostics_promising_candidate_deep_dive.tsv): 見込み候補深掘りTSV。各候補のstatus、判断、見込み理由、不足理由、成果物、初回テスト、Proceed/Hold/Stop境界、禁止主張を整理。
1. [docs/114_steering_predictive_diagnostics_spd_final_conclusions.md](docs/114_steering_predictive_diagnostics_spd_final_conclusions.md): SPD別の一定結論。SPD008を本命候補、SPD002を実証demo、SPD003を近い実務支援、SPD004を戦略オプション、SPD001を低優先、SPD007を条件付き再開として整理。
1. [data/steering_predictive_diagnostics_spd_final_conclusions.tsv](data/steering_predictive_diagnostics_spd_final_conclusions.tsv): SPD別最終結論TSV。final decision、market demand、unresolved pain、hypothesis、artifact、buyer/user、Proceed/Hold/Stop境界、禁止主張、次アクションを整理。
1. [docs/115_steering_predictive_diagnostics_spd008_runtime_deviation_map.md](docs/115_steering_predictive_diagnostics_spd008_runtime_deviation_map.md): SPD008のinternal module runtime deviation map。5つの内部重要モジュールについて、既存monitorとの差分、deviation候補、追加ログtrigger、転記先を整理。
1. [data/steering_predictive_diagnostics_spd008_runtime_deviation_map.tsv](data/steering_predictive_diagnostics_spd008_runtime_deviation_map.tsv): SPD008 map TSV。module別にinput/output、comparison basis、existing monitor、deviation candidate、diagnostic/quality/customer use、Proceed/Hold条件を整理。
1. [docs/116_steering_predictive_diagnostics_spd002_one_case_reading_order.md](docs/116_steering_predictive_diagnostics_spd002_one_case_reading_order.md): SPD002のone-case diagnostic reading order。低/高電圧または過温度によるreduced assistを、DTC、電圧、温度、assist mode、key cycle、repair feedback requirementの順に読むsample。
1. [data/steering_predictive_diagnostics_spd002_one_case_reading_order.tsv](data/steering_predictive_diagnostics_spd002_one_case_reading_order.tsv): SPD002 reading order TSV。step別のquestion、data to read、why this order、interpretation、service/customer output、feedback requirement、禁止主張を整理。
1. [docs/117_steering_predictive_diagnostics_spd008_vs_spd002_decision.md](docs/117_steering_predictive_diagnostics_spd008_vs_spd002_decision.md): SPD008とSPD002の比較判断。SPD008を次の本線候補、SPD002をreference demoに置く判断を整理。SPD008は診断資料作成ではなく、内部重要モジュールのruntime状態説明がpredictive diagnostics / vehicle healthの部品側contributionになるかを見る。
1. [data/steering_predictive_diagnostics_spd008_vs_spd002_decision.tsv](data/steering_predictive_diagnostics_spd008_vs_spd002_decision.tsv): SPD008 vs SPD002比較TSV。伸びしろ、実証しやすさ、既存業務との差分、依存、Proceed/Hold/Stop、禁止主張を整理。
1. [docs/118_steering_predictive_diagnostics_spd008_first_samples.md](docs/118_steering_predictive_diagnostics_spd008_first_samples.md): SPD008 first samples。power monitorとcommunication input validityについて、DTC未満のsoft contextを内部重要モジュールのruntime状態説明として扱えるか、既存monitorとの差分やvehicle healthへの部品側contributionがあるかを整理。
1. [data/steering_predictive_diagnostics_spd008_first_samples.tsv](data/steering_predictive_diagnostics_spd008_first_samples.tsv): SPD008 first samples TSV。sample別にevent pattern、soft deviation、existing monitor boundary、additional log trigger、runtime state explanation、vehicle health contribution、Proceed/Hold条件、禁止主張を整理。
1. [docs/119_steering_predictive_diagnostics_viewpoint_correction.md](docs/119_steering_predictive_diagnostics_viewpoint_correction.md): SPD008観点補正。診断企画向け1枚schemaを目的にせず、runtime状態説明とpredictive diagnostics / vehicle healthへの部品側contributionを先に確認するルールとNext Actionを整理。
1. [docs/120_steering_predictive_diagnostics_spd008_predictive_value_check.md](docs/120_steering_predictive_diagnostics_spd008_predictive_value_check.md): SPD008 predictive value check。power monitorを第一検証候補、communication input validityを第二検証候補に置き、既存monitorとの差分、runtime状態説明、vehicle healthへの部品側contribution、買い手業務、禁止主張を整理。
1. [data/steering_predictive_diagnostics_spd008_predictive_value_check.tsv](data/steering_predictive_diagnostics_spd008_predictive_value_check.tsv): SPD008 predictive value check TSV。sample別にjudgment、runtime state、existing monitor difference、vehicle health contribution、business output、Proceed/Hold/Stop、禁止主張、次アクションを整理。
1. [docs/121_steering_predictive_diagnostics_power_monitor_case.md](docs/121_steering_predictive_diagnostics_power_monitor_case.md): Power monitor 1ケース。短い電圧dip / near-reset contextとassist limitationの近接について、既存monitorで残る項目、残らない可能性、vehicle health向け状態説明、限定Proceed / Hold / Stop条件を整理。
1. [data/steering_predictive_diagnostics_power_monitor_case.tsv](data/steering_predictive_diagnostics_power_monitor_case.tsv): Power monitor case TSV。under-voltage DTC、reset log、power supply fault、freeze frame / extended data、assist mode / limit state、key cycle recurrenceごとに、既存monitorとの差分と次確認項目を整理。
1. [docs/122_steering_predictive_diagnostics_power_monitor_payload_sample.md](docs/122_steering_predictive_diagnostics_power_monitor_payload_sample.md): Power monitor payload sample。既存monitorで十分かを先に判定し、不足がある場合だけvehicle health向け最小payloadへ進むための確認項目、payload候補、Decision Gateを整理。
1. [data/steering_predictive_diagnostics_power_monitor_payload_sample.tsv](data/steering_predictive_diagnostics_power_monitor_payload_sample.tsv): Power monitor payload sample TSV。check item、payload field、decision gateごとに、既存monitorで十分な条件、gap、payload use、Proceed/Hold/Stop、禁止主張を整理。
1. [docs/123_steering_predictive_diagnostics_power_monitor_program_question_sheet.md](docs/123_steering_predictive_diagnostics_power_monitor_program_question_sheet.md): Power monitor program別照合質問シート。AUTOSAR標準で残せる設定余地を前提に、対象programが実際に残しているかを聞く形へ補正。判定ロジックと公開情報で埋められる一般論を整理。
1. [data/steering_predictive_diagnostics_power_monitor_program_question_sheet.tsv](data/steering_predictive_diagnostics_power_monitor_program_question_sheet.tsv): 照合質問シートTSV。check item × 質問軸ごとに、質問、聞く理由、回答元、十分条件、差分条件、payload field、禁止主張を整理。program固有欄は空欄で渡す。
1. [docs/124_steering_predictive_diagnostics_comm_input_validity_case.md](docs/124_steering_predictive_diagnostics_comm_input_validity_case.md): Communication input validityの独立ケース。hard communication DTC未満の揺らぎとfallback近接について、既存monitor(IdsM含む)との差分、最小payload、条件付きHold(Proceed寄り)の判定を整理。
1. [data/steering_predictive_diagnostics_comm_input_validity_case.tsv](data/steering_predictive_diagnostics_comm_input_validity_case.tsv): Communication input validity case TSV。timeout DTC、bus-off、invalid value、E2E保護、fallback state、IdsM、recurrenceごとに差分条件と判定を整理。
1. [docs/125_steering_predictive_diagnostics_unverified_delta_check.md](docs/125_steering_predictive_diagnostics_unverified_delta_check.md): 未検証デルタのファクトチェック。既存monitor比、汎用テレマティクス比、IDS比の差分主張を公開情報で検証し、価値主張の言い直しとSPD002の意図的凍結を記録。
1. [data/steering_predictive_diagnostics_unverified_delta_check.tsv](data/steering_predictive_diagnostics_unverified_delta_check.tsv): デルタ検証TSV。delta claim、公開事実、検証結果、残る差分、言い直し後の表現、Kill条件への接続を整理。
1. [docs/126_steering_predictive_diagnostics_sotif_contribution_prospect.md](docs/126_steering_predictive_diagnostics_sotif_contribution_prospect.md): SOTIFへの乗り方の判定。プロセス支援はNo-Go、論証証拠は既存業務、運用フェーズのフィールド監視への部品側インプットだけ条件付き検証候補。KQ1〜KQ5の入口条件と故障予測Kill維持を整理。
1. [data/steering_predictive_diagnostics_sotif_contribution_prospect.tsv](data/steering_predictive_diagnostics_sotif_contribution_prospect.tsv): SOTIF prospect TSV。3つのoption判定、KQ1〜KQ5、EPS視点triggering condition候補、故障予測Kill維持を整理。
1. [docs/127_steering_predictive_diagnostics_target_case_public_evidence.md](docs/127_steering_predictive_diagnostics_target_case_public_evidence.md): ターゲットケースの公開実在確認。Ford 15V-340のDTC有無2経路是正、GM 17V-414の一時喪失・突然復帰、GM TSB 17-NA-158の外部signal起因警告、Tesla過電圧調査などから「DTCが残らない断続的assist低下」の実在をConfirmed。痛みの実在確認であり商品価値の証明ではない、という限界も明記。
1. [data/steering_predictive_diagnostics_target_case_public_evidence.tsv](data/steering_predictive_diagnostics_target_case_public_evidence.tsv): 公開証拠TSV。リコール是正・ODI調査・TSB・整備情報ごとに、公開事実、SPDとの関係、支持内容、限界、confidenceを整理。
1. [docs/128_steering_predictive_diagnostics_sotif_public_signal_watch.md](docs/128_steering_predictive_diagnostics_sotif_public_signal_watch.md): SOTIF公開シグナル観測。ISO 21448のSOTIF-EooC(部品サプライヤの公式参加形式)、Bosch定量SOTIF特許、by-wire量産・L3展開を確認し、KQ1の公算を補強。SOTIF枝は実施条件待ちのまま、KQ1の質問形をEooC仮定ベースへ具体化。
1. [docs/129_steering_predictive_diagnostics_public_case_crosscheck.md](docs/129_steering_predictive_diagnostics_public_case_crosscheck.md): 判定ゲートの公開ケース照合。Ford 15S18とGM 17276の一次文書精読により、是正実務の判断材料がDTC有無の1bitのみで、DTC未満event・snapshot・同時性・再発が存在しないことを確認。SPD008価値仮説を公開情報のみでConfirmedし、内部資料条件を実行のみに縮小。
1. [data/steering_predictive_diagnostics_public_case_crosscheck.tsv](data/steering_predictive_diagnostics_public_case_crosscheck.tsv): 公開ケース照合TSV。5照合項目+誤診コスト実在+判定を、公開文書の記述、差分確認、SPDへの含意、限界とともに整理。
1. [docs/130_steering_predictive_diagnostics_comm_validity_public_crosscheck.md](docs/130_steering_predictive_diagnostics_comm_validity_public_crosscheck.md): comm input validityの公開ケース照合。GM TSB 17-NA-158原文で依存signal起因の誤交換連鎖を確認し、Hold→公開レベルConfirmed付き限定Proceedへ。TSB=SPD008 payloadの人手版という言い直しと、Ford SSM 49530による2021年世代の誤帰属継続確認を含む。
1. [data/steering_predictive_diagnostics_comm_validity_public_crosscheck.tsv](data/steering_predictive_diagnostics_comm_validity_public_crosscheck.tsv): comm validity公開照合TSV。保持・切り分け・説明・近接・再発・依存定義の主導権・現行世代誤帰属・判定を整理。
1. [docs/131_steering_predictive_diagnostics_checkpoint_summary.md](docs/131_steering_predictive_diagnostics_checkpoint_summary.md): **区切りまとめ(まずこれを読む)**。IDを使わない自然言語での仮説と結論、ID対訳表、検証ストーリー、最終判定表、残る実行条件(すべて内部資料条件)を1本に集約。
1. [docs/132_steering_predictive_diagnostics_payload_replay_demo.md](docs/132_steering_predictive_diagnostics_payload_replay_demo.md): 具体化デモ。公開3ケースを最小payloadで再演し、実務の判断材料(DTC 1bit / 誤帰属code)と「その場で出せた状態説明」を対比。禁止主張を機械的に拒否する境界ガードの動作確認込み。実行は `python3 scripts/spd008_payload_replay.py`、出力は [generated/spd008_payload_replay.html](generated/spd008_payload_replay.html)。
1. [docs/133_failure_prediction_demand_map.md](docs/133_failure_prediction_demand_map.md): 故障予測の需要マップ。買い手6セグメント別に、欲しい予測の形・粒度・必要データ・既存プレイヤー・EPSサプライヤの入り口を整理。個車レベルの席は埋まっており、空席は(1)部品内部のDTC未満信号(検証済み)と(2)群レベルの故障傾向(公開データで未検証、次フェーズの本命)の2つ。
1. [data/failure_prediction_demand_map.tsv](data/failure_prediction_demand_map.tsv): 需要マップTSV。セグメント×(予測の形、粒度、データ所有、既存プレイヤー、入り口、公開Demo可否、判定)。
1. [docs/134_group_level_data_feasibility.md](docs/134_group_level_data_feasibility.md): 群レベル曲線のデータ当たり付け。NHTSA苦情API(実働確認済み)を主データ、既知リコールを答え合わせ、DVSA MOT(分母付き)を拡張とし、フェーズC Goを判定。分母なし・報告バイアスの限界を明記。
1. [data/group_level_data_feasibility.tsv](data/group_level_data_feasibility.tsv): データ当たり付けTSV。源別に実在確認、粒度、分母有無、曲線への使い方、限界、ライセンス、判定を整理。
1. [docs/135_steering_cohort_curve_demo_verdict.md](docs/135_steering_cohort_curve_demo_verdict.md): **群レベルcohort曲線Demoの判定(答え合わせ成功)**。Ford Fusion 5年式・13,862件の公開苦情の盲検集計で、リコール対象cohort(MY2011-2012)の操舵系比率51.2%/57.7%が比較cohort(21.5%/24.2%)の2倍以上に浮き、公式リコール事実を再現。実行は `python3 scripts/steering_cohort_curve.py`、出力は [generated/steering_cohort_curve.html](generated/steering_cohort_curve.html)。報告バイアスの可視化と限界(分母なし、事後検証である点)も明記。
1. [data/steering_cohort_curve_summary.tsv](data/steering_cohort_curve_summary.tsv): cohort別サマリTSV。全苦情、操舵系件数、比率、車齢24/48/72/120ヶ月時点の累積。
1. [docs/136_steering_cohort_backtest_verdict.md](docs/136_steering_cohort_backtest_verdict.md): **時点区切りバックテストの判定(事前検知成功)**。事前固定した検知ルールで、MY2012はリコール公表25ヶ月前(ODI調査開始より約1年前)、MY2011は7ヶ月前に発火。非リコールcohortは発火せず偽陽性ゼロ。MY2010は届出遅延で検知不能=苦情ベース検知の限界として記録し、部品内部観測(SPD008)との相補性を確定。実行は `python3 scripts/steering_cohort_backtest.py`。
1. [data/steering_cohort_backtest.tsv](data/steering_cohort_backtest.tsv): バックテストTSV。cutoff別のcohort比率・発火判定と、初回発火時点・リード月数。
1. [docs/137_residual_candidates_sweep.md](docs/137_residual_candidates_sweep.md): 残候補4件の一括消化。**①Silverado横展開は負の結果(事前固定ルールが両リコールcohortをMISS=絶対閾値は車種を跨いで汎化しない)** ②故障モード分類は成功(Fusionの浮きの60〜62%がアシスト喪失モード)、モードベース監視をルール改訂候補に ③DVSA MOTは年10GB級・EPS固有分類の存在確認・保留 ④品質改善向け月次監視レポートのモック。
1. [data/steering_cohort_backtest_silverado.tsv](data/steering_cohort_backtest_silverado.tsv): Silverado横展開のバックテストTSV。
1. [data/steering_mode_split.tsv](data/steering_mode_split.tsv): 故障モード分類TSV。車種×cohort別にアシスト喪失/騒音・振動/流れ・ふらつき/コラム・ロック/その他の件数とモード比率。
1. [docs/138_business_model_definition.md](docs/138_business_model_definition.md): **ビジネスモデル定義**。3層構造(第1層=状態説明機能つきEPS製品仕様をOEMへRFQ差別化+診断コンテンツNREとして売る唯一の収益線、第2層=市場シグナル監視は内部投資、第3層=assessmentはprogram付帯NREのみ)。金の流れ、競争優位、既往Killとの整合、事業のKill条件(BM-KQ1〜4)を定義。技術検証が「問題への手当て」で終わらないための土台。
1. [docs/139_log_sign_extraction_demo.md](docs/139_log_sign_extraction_demo.md): **技術者向けLog兆候抽出デモ**。公開走行log(commaSteeringControl、MIT)938セグメントから、操舵応答の残差6特徴をrobust z-scoreで機械抽出(学習モデルなし・決定的・再現可能)。raw波形の目視では分からない兆候を検出し、payload形式の状態説明とSOTIF語彙(triggering condition候補、EooC仮定検証)へ機械変換。故障検出ではない境界を明記。実行は `python3 scripts/steering_log_sign_extraction.py`、出力は [generated/steering_log_sign_extraction.html](generated/steering_log_sign_extraction.html)。
1. [data/steering_log_sign_extraction.tsv](data/steering_log_sign_extraction.tsv): セグメント別特徴量TSV。6特徴の実値とz-score、max_abs_z、主特徴、有効サンプル、平均車速。
1. [docs/68_repo_closure_inventory.md](docs/68_repo_closure_inventory.md): Repoを閉じるかどうかの人間向け棚卸し。探索枝ごとの現行判断、残す価値、再開条件、Close推奨を整理。
1. [data/repo_closure_inventory.tsv](data/repo_closure_inventory.tsv): 探索枝ごとのmarket signal、tested artifact、latest decision、why not proceed、residual value、reopen condition、source docsを整理したTSV。
1. [docs/archive/oem_remote_diagnostics/78_oem_remote_diagnostics_eps_explanation_layer_hypothesis.md](docs/archive/oem_remote_diagnostics/78_oem_remote_diagnostics_eps_explanation_layer_hypothesis.md): 新しい作業仮説。OEM remote diagnostics networkに組み込むEPS/SbW内部データ由来の操舵系状態説明レイヤー。
1. [data/archive/oem_remote_diagnostics/oem_remote_diagnostics_eps_explanation_layer_questions.tsv](data/archive/oem_remote_diagnostics/oem_remote_diagnostics_eps_explanation_layer_questions.tsv): 新仮説の検証質問。data field、既存remote diagnosticsとの差分、service outcome、責任境界、成果物転記を確認する。
1. [docs/archive/oem_remote_diagnostics/80_oem_remote_diagnostics_validation_plan.md](docs/archive/oem_remote_diagnostics/80_oem_remote_diagnostics_validation_plan.md): 新仮説の検証計画。Network参加可能性、必要data field、既存remote diagnosticsとの差分、service outcome、責任境界、1ケースsampleへ分解。
1. [data/archive/oem_remote_diagnostics/oem_remote_diagnostics_validation_items.tsv](data/archive/oem_remote_diagnostics/oem_remote_diagnostics_validation_items.tsv): RDI001〜RDI006の調査item。Network参加経路を最初のKill gateとして整理。
1. [docs/archive/oem_remote_diagnostics/81_rdi001_006_research_report.md](docs/archive/oem_remote_diagnostics/81_rdi001_006_research_report.md): RDI001〜RDI006を公開情報で調査した結果。Network参加経路はあるがopenではなく、公開APIだけではEPS/SbW固有data fieldとservice outcome feedbackが弱い。
1. [data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi_research_findings.tsv](data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi_research_findings.tsv): RDI001〜RDI006のitem別結論、根拠、反証、Proceed条件、Kill条件を整理したTSV。
1. [docs/archive/oem_remote_diagnostics/82_rdi006_thermal_limit_4_column_sample.md](docs/archive/oem_remote_diagnostics/82_rdi006_thermal_limit_4_column_sample.md): thermal limit / assist limitationの1ケースsample。DTCだけ、既存remote diagnostics、EPS/SbW内部説明、OEM service noteを比較し、差分が出る条件を整理。
1. [data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_thermal_limit_sample.tsv](data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_thermal_limit_sample.tsv): RDI006 sampleのstep別4列比較。event snapshot、cool-down、repeated event、software/calibration、service outcome feedbackを整理。
1. [data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_program_gap_template.tsv](data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_program_gap_template.tsv): 実programまたは想定programで穴埋めする確認表。読めるdata field、既存action plan、追加説明、service note転記先、outcome feedback、責任境界を確認する。
1. [docs/archive/oem_remote_diagnostics/83_rdi006_program_gap_pdca.md](docs/archive/oem_remote_diagnostics/83_rdi006_program_gap_pdca.md): RDI006 program gapをPDCAで穴埋めしたレポート。当時はConditional Continue / not offerに縮小したが、内部資料なしルールではArchive判断の根拠として扱う。
1. [data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_program_gap_filled.tsv](data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_program_gap_filled.tsv): 穴埋め完了版。10項目ごとにfilled status、必要artifact、owner、Proceed/Kill signal、EPS supplier decisionを整理。
1. [data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_pdca_log.tsv](data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_pdca_log.tsv): PDCA 4周分のPlan / Do / Check / Actと判断変化。
1. [docs/archive/motion_health/79_motion_health_archive_index.md](docs/archive/motion_health/79_motion_health_archive_index.md): motion health / fleet運行可否調査をArchive化した索引。新仮説で使える知見と使ってはいけない主張を整理。
1. [data/archive/motion_health/motion_health_archive_links.tsv](data/archive/motion_health/motion_health_archive_links.tsv): Archive化したsource link、使い方、限界を整理したTSV。
1. [docs/archive/motion_health/69_old_theme_archive_and_new_focus.md](docs/archive/motion_health/69_old_theme_archive_and_new_focus.md): 旧テーマをArchiveし、新テーマを「自動運転・商用車両群向けの操舵系運行可否/点検優先度判断」に絞るための入口。
1. [data/archive/motion_health/motion_health_new_focus_questions.tsv](data/archive/motion_health/motion_health_new_focus_questions.tsv): 新テーマで最初に確認する10個の検証質問。買い手、痛み、データアクセス、判断出力、Kill条件を整理。
1. [docs/archive/motion_health/70_motion_health_mhq001_005_research_report.md](docs/archive/motion_health/70_motion_health_mhq001_005_research_report.md): 新テーマの検証質問1〜5を公開情報で確認したレポート。fleet一般の需要は強いが、操舵系固有の痛みとサプライヤのデータアクセスは追加検証が必要。
1. [data/archive/motion_health/motion_health_mhq001_005_evidence.tsv](data/archive/motion_health/motion_health_mhq001_005_evidence.tsv): MHQ001〜005向けのsource、evidence signal、support、limit、confidence、URLを整理したTSV。
1. [docs/archive/motion_health/72_mhq001_20min_deep_dive.md](docs/archive/motion_health/72_mhq001_20min_deep_dive.md): MHQ001を20分枠で深掘りしたメモ。fleet downtimeとAV maintenanceは強いが、steering単独では弱く、chassis / motion healthとしても `Hold / Continue Investigation` に留める判断。
1. [docs/archive/motion_health/73_mhq001_second_20min_deep_dive.md](docs/archive/motion_health/73_mhq001_second_20min_deep_dive.md): MHQ001を再深掘りし、`Proceed` を `Hold / Continue Investigation` に下げた修正版。steering-onlyの購買painは未確認で、chassis / motion healthとしてのみ継続。
1. [docs/archive/motion_health/74_mhq003_005_deep_dive_for_mhq001.md](docs/archive/motion_health/74_mhq003_005_deep_dive_for_mhq001.md): MHQ003のdata accessとMHQ005の既存remote diagnostics差分を深掘りし、MHQ001を `Hold / Stop-leaning` に下げた判断。次の1ケースsampleで差分が出なければStop。
1. [docs/archive/motion_health/75_motion_health_mhq001_final_decision.md](docs/archive/motion_health/75_motion_health_mhq001_final_decision.md): MHQ001の最終判断。fleet downtime需要はあるが、data accessと既存remote diagnosticsとの差分が公開情報だけでは証明できないため、外販テーマとしてはStop / Archive。
1. [docs/archive/motion_health/76_other_mhq_20min_deep_dive.md](docs/archive/motion_health/76_other_mhq_20min_deep_dive.md): MHQ001以外のMHQ002/004/006/007/008/009/010を20分枠で深掘りした最終補強メモ。市場側のYesはあるが、外販Stop判断は変わらない。
1. [docs/archive/motion_health/77_mhq004_007_008_deeper_review.md](docs/archive/motion_health/77_mhq004_007_008_deeper_review.md): MHQ004/007/008を追加深掘りし、外販ではなく再開条件として残す判断を整理。MHQ004はoutput rubric、MHQ007はbundle boundary、MHQ008はfield-to-engineering feedbackとして保存。
1. [data/archive/motion_health/motion_health_mhq_work_surface.tsv](data/archive/motion_health/motion_health_mhq_work_surface.tsv): MHQ001〜010の作業面。各questionの現在結論、confidence、弱点、次アクション、priorityを整理。
1. [data/archive/motion_health/motion_health_mhq001_deep_dive_evidence.tsv](data/archive/motion_health/motion_health_mhq001_deep_dive_evidence.tsv): MHQ001向けにfleet downtime general、AV maintenance、chassis/motion specific、steering specificのevidenceを分類したTSV。
1. [data/archive/motion_health/motion_health_mhq003_005_evidence.tsv](data/archive/motion_health/motion_health_mhq003_005_evidence.tsv): MHQ003/MHQ005向けに、vehicle data access、OEM/API、supplier cloud連携、既存remote diagnostics、SOVDの反証材料を整理したTSV。
1. [data/archive/motion_health/motion_health_mhq001_final_kill_check_sample.tsv](data/archive/motion_health/motion_health_mhq001_final_kill_check_sample.tsv): 高負荷操舵でEPS thermal limit / assist limitationに入った仮想ケースを、DTCだけ、既存remote diagnostics、supplier domain triageの3列で比較したKill確認sample。
1. [data/archive/motion_health/motion_health_other_mhq_deep_dive.tsv](data/archive/motion_health/motion_health_other_mhq_deep_dive.tsv): MHQ002/004/006/007/008/009/010のitem別結論、support/counter-signal、EPS supplier decisionを整理したTSV。
1. [data/archive/motion_health/motion_health_mhq004_007_008_deeper.tsv](data/archive/motion_health/motion_health_mhq004_007_008_deeper.tsv): MHQ004/007/008について、深掘り結論、support/counter-signal、再開条件、EPS supplier boundaryを整理したTSV。
1. [docs/66_return_to_eps_product_value_after_kaggle_branch.md](docs/66_return_to_eps_product_value_after_kaggle_branch.md): Kaggle/Bosch線を需要調査の枝に下げ、本題をEPS製品価値へ戻すための判断。次候補はEPS診断コンテンツの次世代化。
1. [docs/67_next_generation_diagnostic_content_value_check.md](docs/67_next_generation_diagnostic_content_value_check.md): EPS診断コンテンツの次世代化が製品仕様・診断仕様・RFQ回答に残るかをKill-firstで確認した最新メモ。SOVD基盤ではなく、公開範囲、権限、禁止主張、software/calibration接続だけを見る。
1. [data/next_generation_diagnostic_content_value_check.tsv](data/next_generation_diagnostic_content_value_check.tsv): 25件の仮診断コンテンツを、次世代診断での見せ方、EPSサプライヤ境界、RFQ/仕様文言、禁止主張、Kill signalへ整理したproxy demo。
1. [docs/62_kaggle_competition_hidden_demand_review.md](docs/62_kaggle_competition_hidden_demand_review.md): Kaggleコンペを、公開代替データではなく「企業が外に出した隠れた需要」として読み直した最新メモ。最有力はEPS市場故障ではなく、製造品質と評価時間短縮。
1. [data/kaggle_hidden_demand_candidates.tsv](data/kaggle_hidden_demand_candidates.tsv): Bosch、Mercedes-Benz、OBD-II/CAN、Car-Hacking等を、隠れた需要、EPSサプライヤ適合、使ってはいけない主張、Kill条件で整理。
1. [docs/84_kaggle_problem_setting_lens.md](docs/84_kaggle_problem_setting_lens.md): Kaggleを「データセット」ではなく、企業が外に出した問題設定として読む観点。目的変数、入力データ、評価指標から隠れた業務意図を読む。
1. [data/kaggle_problem_setting_lens.tsv](data/kaggle_problem_setting_lens.tsv): Kaggle課題ごとに、何を読むか、隠れた意図、EPSサプライヤでの読み替え、使ってよい用途、使ってはいけない用途を整理。
1. [docs/85_kaggle_problem_setting_id_deep_dive.md](docs/85_kaggle_problem_setting_id_deep_dive.md): Kaggle問題設定をKGL001〜KGL006に分け、各IDの結論、EPSサプライヤへの読み替え、Proceed/Kill条件、次アクションを整理。工程検査を目的にしない前提では、KGL003/005/006を実使用条件proxyとして残し、KGL004を通信異常・禁止主張の境界確認として残す。KGL001/002は製造・評価効率の別枝として保存。
1. [data/kaggle_problem_setting_id_deep_dive.tsv](data/kaggle_problem_setting_id_deep_dive.tsv): KGL001〜KGL006のID別作業面。problem setting signal、hidden intent、buyer/user、evidence、decision、kill condition、source URLを整理。
1. [docs/86_kaggle_usage_proxy_refresh.md](docs/86_kaggle_usage_proxy_refresh.md): 工程検査ではなく実使用条件proxyとしてKaggleを再調査し、KGL007〜KGL012を追加。KGL003/005/006/007/008を実使用条件family、KGL011/KGL004を通信異常と禁止主張の境界確認に置く。
1. [data/kaggle_usage_proxy_refresh.tsv](data/kaggle_usage_proxy_refresh.tsv): KGL003/005/006/007/008/009/010/011/012のproxy type、EPSサプライヤ用途、優先度、limit、next action、kill condition、source URLを整理。
1. [docs/87_kaggle_each_id_deep_dive.md](docs/87_kaggle_each_id_deep_dive.md): KGL001〜KGL012を同じ判定軸で深掘り。KGL003/005/006/007/008を使用条件familyの主材料、KGL004/011を通信異常境界、KGL001/002/009/010/012を別枝または補助に整理。
1. [data/kaggle_each_id_deep_dive.tsv](data/kaggle_each_id_deep_dive.tsv): 各IDのdeep_dive_decision、何を示すか、EPSサプライヤでの読み替え、次artifact、禁止主張、次checkを整理。
1. [docs/88_kaggle_usage_condition_family_table.md](docs/88_kaggle_usage_condition_family_table.md): KGL003/005/006/007/008を中心に、KGL004/011通信異常境界も含めた30件の使用条件familyを人間向けに説明。最新ルールでは主成果物ではなく、予測的な付加価値候補を検証するための中間成果物として扱う。
1. [data/kaggle_usage_condition_families.tsv](data/kaggle_usage_condition_families.tsv): 30件のusage family作業表。source ID、proxy signal、EPS評価質問、診断質問、顧客説明質問、禁止主張、priority、next checkを整理。次に「何を先読みできる可能性があるか」へ変換する土台として使う。
1. [docs/89_kaggle_predictive_value_plan.md](docs/89_kaggle_predictive_value_plan.md): Kaggle / 公開proxyを、予測的付加価値候補として順次検証する計画。PVC001〜PVC007の優先順位、実施順、Kill条件を整理。
1. [data/kaggle_predictive_value_candidates.tsv](data/kaggle_predictive_value_candidates.tsv): KGL/UFをPVC001〜PVC007へ変換した候補表。何を先読みするか、買い手/利用者、EPSサプライヤが関与できる理由、禁止主張、Kill条件を整理。
1. [docs/90_pvc001_usage_load_class_deep_dive.md](docs/90_pvc001_usage_load_class_deep_dive.md): 最有望候補PVC001「使用負荷classの先読み」の初回深掘り。外販商品ではなく、EPSサプライヤ内の製品企画、診断企画、品質改善、評価企画へ転記できるかを見る。
1. [data/pvc001_usage_load_class_sample.tsv](data/pvc001_usage_load_class_sample.tsv): PVC001の9件の使用負荷class sample。ULC001〜ULC009ごとに公開proxy、先読み対象、部署、価値、禁止主張、Kill条件、次checkを整理。
1. [docs/91_pvc001_1h_goal_deep_dive.md](docs/91_pvc001_1h_goal_deep_dive.md): PVC001を1時間Goalで深掘りした結果。ULC001/003/004/008のitem別結論、ULC008中心の1枚sample、部署別価値、弱点、Continue/Kill条件を整理。
1. [data/pvc001_four_class_deep_dive.tsv](data/pvc001_four_class_deep_dive.tsv): ULC001/003/004/008の4件について、結論、confidence、部署適合、価値、弱点、Proceed/Kill impact、next actionを整理。
1. [data/pvc001_ulc008_one_page_sample.tsv](data/pvc001_ulc008_one_page_sample.tsv): ULC008「駐車場走行で低速・大舵角・凹凸が重なる使われ方」の1枚sample。市場需要、未解決pain、仮説、部署別用途、禁止主張、Kill条件を整理。
1. [docs/92_pvc001_ulc008_department_review_deep_dive.md](docs/92_pvc001_ulc008_department_review_deep_dive.md): ULC008を、製品企画・診断企画に見せる社内レビューsampleとして深掘り。出力形式、evidence boundary、最小信号契約、部署別判断、Kill gateを整理。
1. [data/pvc001_ulc008_department_review_questions.tsv](data/pvc001_ulc008_department_review_questions.tsv): ULC008の部署別レビュー質問。製品企画、診断企画、品質改善、評価企画、全体Kill gateごとに、Proceed signal、Kill signal、次アクションを整理。
1. [data/pvc001_ulc008_kill_gate.tsv](data/pvc001_ulc008_kill_gate.tsv): ULC008の最小Kill gate。2部署以上に具体的な使い道があるか、原因断定に見えないか、既存評価・診断の言い換えで終わらないかを判定する表。
1. [docs/93_predictive_value_id_status_inventory.md](docs/93_predictive_value_id_status_inventory.md): 手持ちのPVC/ULC/KGL IDを棚卸しした補正前レポート。EPS内部事実不足を主Kill理由にしすぎたため、最新判断はdocs/96を見る。
1. [data/predictive_value_id_status_inventory.tsv](data/predictive_value_id_status_inventory.tsv): PVC001〜007、ULC001〜009、KGL001〜012の補正前ステータス表。最新ステータスはdata/predictive_value_corrected_status.tsvを見る。
1. [docs/94_predictive_value_next_items_deep_dive.md](docs/94_predictive_value_next_items_deep_dive.md): 次アイテムとして挙げたULC008、ULC004、PVC004を深掘り。ULC008は製品企画向け/診断企画向けに分割し、ULC004は品質改善・顧客説明向け、PVC004は診断信頼性境界として整理。
1. [data/pvc001_ulc008_two_department_sheets.tsv](data/pvc001_ulc008_two_department_sheets.tsv): ULC008を製品企画向けと診断企画向けに分けた社内レビュー用作業表。各sheetの判断、需要、evidence boundary、初期artifact、禁止主張、Proceed/Kill signalを整理。
1. [data/ulc004_rough_road_steering_deep_dive.tsv](data/ulc004_rough_road_steering_deep_dive.tsv): ULC004「荒れた路面 + 操舵」の深掘り表。品質改善、評価企画、顧客技術説明で使えるか、路面分類productや原因断定へ流れないかを整理。
1. [data/pvc004_communication_boundary_deep_dive.tsv](data/pvc004_communication_boundary_deep_dive.tsv): PVC004「通信異常context」の境界表。診断企画、サイバー担当、顧客技術説明での使い道、汎用IDS/CSMS/TARAへの逸脱、禁止主張を整理。
1. [docs/95_predictive_value_continue_final_decision.md](docs/95_predictive_value_continue_final_decision.md): 残っていたContinue項目の最終判断。公開情報とKaggle proxyだけで継続深掘りする項目は残さず、ULC008/ULC004/PVC004を社内レビュー材料に限定。
1. [data/predictive_value_continue_final_decisions.tsv](data/predictive_value_continue_final_decisions.tsv): PVC/ULC/KGL各IDのprevious status、final status、最終結論、停止理由、再開条件、次owner、禁止主張を整理。
1. [docs/96_predictive_value_internal_fact_correction.md](docs/96_predictive_value_internal_fact_correction.md): 前回の全滅判断を補正した最新判断。EPS内部事実が見えないことを主Kill理由にせず、PVC001/ULC008/ULC004/PVC004を公開proxy価値の検証候補として戻す。
1. [data/predictive_value_corrected_status.tsv](data/predictive_value_corrected_status.tsv): 補正後のID別ステータス。使用条件class、路面・操舵context、通信異常contextを、故障予測ではなくEPSサプライヤの業務価値候補として整理。
1. [docs/63_kaggle_supplier_owned_data_pdca.md](docs/63_kaggle_supplier_owned_data_pdca.md): Kaggle方向を1時間Goalで深掘りし、データ収集、仮説、検証PDCAを回した結果。Bosch型の製造・EOL検査の早期不良候補抽出を最優先、Mercedes型の評価時間見積もりを2番手に置く。
1. [data/kaggle_supplier_owned_source_collection.tsv](data/kaggle_supplier_owned_source_collection.tsv): Bosch、Mercedes-Benz、EPS/EPAS EOL、EOL品質データ、OBD/CAN、Car-Hackingのソース収集表。
1. [data/kaggle_supplier_owned_hypotheses.tsv](data/kaggle_supplier_owned_hypotheses.tsv): 製造・EOL検査、bench/HILS評価時間、説明1枚、停止候補を、市場需要、未解決pain、解決策、買い手、Kill条件で整理。
1. [data/kaggle_supplier_owned_pdca.tsv](data/kaggle_supplier_owned_pdca.tsv): 4周分のPlan / Do / Check / Actと判断。
1. [docs/64_kaggle_pre_shipment_predictive_quality_deep_dive.md](docs/64_kaggle_pre_shipment_predictive_quality_deep_dive.md): Kaggleから「出荷前の予知保全」を掘り直した最新メモ。Bosch型を、出荷前品質スクリーニングとして読み替える。
1. [data/kaggle_pre_shipment_quality_findings.tsv](data/kaggle_pre_shipment_quality_findings.tsv): Bosch/Mercedesから得られた具体情報、EPSサプライヤへの読み替え、使えること/使えないこと。
1. [data/pre_shipment_quality_offer_candidate.tsv](data/pre_shipment_quality_offer_candidate.tsv): 出荷前品質スクリーニング候補を、市場需要、痛み、仮説、解決、買い手、初期artifact、検証、Kill条件で1行ずつ整理。
1. [docs/65_pre_shipment_quality_screening_proxy_demo.md](docs/65_pre_shipment_quality_screening_proxy_demo.md): Bosch型の構造を再現した出荷前品質スクリーニングproxy demo。上位5%個体でfail/retest候補17.5%を捕捉し、再検査・保留・工程確認への転記可否を確認。
1. [generated/pre_shipment_quality_screening_proxy.html](generated/pre_shipment_quality_screening_proxy.html): ブラウザで見られるproxy demo。Kaggle実データではなくsynthetic proxyであることを明記。
1. [docs/60_sbw_explanation_support_no_go_reasoning.md](docs/60_sbw_explanation_support_no_go_reasoning.md): Steer-by-wire向けの説明資料整理支援が、なぜ有償サービスとしてNo-Goなのかを、市場需要からKill条件まで一本の論理で整理した最新判断。
1. [data/sbw_explanation_support_no_go_reasoning.tsv](data/sbw_explanation_support_no_go_reasoning.tsv): 市場需要、未解決pain、仮説縮小、既存業務重複、EPSサプライヤ境界、Kill条件を対応づけたTSV。
1. [docs/59_wheel_side_steering_unit_plain_deep_dive.md](docs/59_wheel_side_steering_unit_plain_deep_dive.md): `road wheel actuator` を「車輪側操舵ユニット」と言い直し、何が市場変化で、何が既存安全・認証・診断業務の範囲かを平易に整理した判断。
1. [data/wheel_side_steering_unit_plain_deep_dive.tsv](data/wheel_side_steering_unit_plain_deep_dive.tsv): 車輪側操舵ユニットについて、市場需要、未解決の痛み、仮説、解決策、利用者、初期提供物、検証方法、Kill条件を平易な言葉で整理したTSV。
1. [docs/58_sbw_public_only_info_collection.md](docs/58_sbw_public_only_info_collection.md): 内部資料を使わず、公開情報だけでSbW方向を追加収集した判断。市場変化はあるが、汎用安全・認証・診断支援は既存論点と重なり、外販Proceedには進めない。
1. [data/sbw_public_only_source_inventory.tsv](data/sbw_public_only_source_inventory.tsv): Bosch、ZF、Nexteer、Schaeffler、HELLA、JTEKT、Tesla、NHTSA、VCA、R79、ASAM SOVDの公開情報を、何を支持し、何を支持しないかで整理したTSV。
1. [data/sbw_public_only_value_check.tsv](data/sbw_public_only_value_check.tsv): 公開情報だけで市場変化、未解決pain、既存業務との差分、診断コンテンツ余地、初期提供物をどこまで言えるかの判定表。
1. [docs/54_steer_by_wire_business_deep_dive.md](docs/54_steer_by_wire_business_deep_dive.md): Steer-by-wire方向を事業成立性まで深掘りした判断。汎用安全支援ではなく、OEM説明・診断設計へ転記するcomponent-boundary整理だけを狭く残す。
1. [data/steer_by_wire_business_deep_dive.tsv](data/steer_by_wire_business_deep_dive.tsv): SbW方向の市場需要、未解決の痛み、仮説、初期提供物、Kill条件を整理したTSV。
1. [docs/57_sbw_8_material_verification.md](docs/57_sbw_8_material_verification.md): SbW 8項目を公開情報で検証した結果。1-4はPartial、5-8はUnknown。現行方針では内部資料を要求しないため、外販Proceedには進めない。
1. [data/sbw_8_material_verification.tsv](data/sbw_8_material_verification.tsv): 8項目ごとのpublic verification result、公開情報で分からないこと、decision impact、公開情報だけでの限界。
1. [docs/56_sbw_decision_materials.md](docs/56_sbw_decision_materials.md): SbW方向をProceed / Killするために集めた判断材料。公開ソースから見えることと、公開情報だけでは埋まらない8項目を分ける。
1. [data/sbw_decision_materials.tsv](data/sbw_decision_materials.tsv): ZF、Mercedes-Benz、Tesla、Lexus、HELLA、NHTSA、VCAの公開情報を、判断への使い方、強める点、弱める点へ対応づけたTSV。
1. [docs/55_sbw_redundancy_degraded_one_page_sample.md](docs/55_sbw_redundancy_degraded_one_page_sample.md): 車輪を動かす側の冗長系が一部落ちた場合を題材にした公開情報ベースの1ケースsample。これ単体で独自価値が出るかを見る。
1. [data/steer_by_wire_redundancy_degraded_sample.tsv](data/steer_by_wire_redundancy_degraded_sample.tsv): 1ケースsampleのfield、supplier-owned source、OEM回答価値、Kill条件。
1. [docs/51_steer_by_wire_kill_first_review.md](docs/51_steer_by_wire_kill_first_review.md): Steer-by-wire安全・冗長・cyber方向の一次レビュー。市場変化はあるが、既存安全業務と被るためHold / explore next。
1. [data/steer_by_wire_kill_first_review.tsv](data/steer_by_wire_kill_first_review.tsv): Steer-by-wireの市場シグナル、EPSサプライヤが持てる手札、Kill条件を整理したTSV。
1. [docs/52_sovd_kill_first_review.md](docs/52_sovd_kill_first_review.md): SOVD / next-generation diagnostics方向の一次レビュー。主商品ではなく、EPS診断コンテンツ設計のextensionとしてのみ残す。
1. [data/sovd_kill_first_review.tsv](data/sovd_kill_first_review.tsv): SOVD標準・既存ツール・EPSサプライヤ残余価値・Kill条件を整理したTSV。
1. [docs/42_coverage_benchmark_artifact_intake_result.md](docs/42_coverage_benchmark_artifact_intake_result.md): Coverage BenchmarkのArtifact Intake実行結果。
1. [data/coverage_benchmark_artifact_intake_result.tsv](data/coverage_benchmark_artifact_intake_result.tsv): 10 artifactごとのplaceholder、実資料有無、今判定できること、できないこと、status。
1. [data/coverage_benchmark_artifact_intake_decision.tsv](data/coverage_benchmark_artifact_intake_decision.tsv): Artifact intake後のProceed/Hold/Kill判断表。
1. [data/coverage_benchmark_internal_placeholder_screening_sheet.tsv](data/coverage_benchmark_internal_placeholder_screening_sheet.tsv): 内部資料を使える場合だけ参照する4項目screening sheet。
1. [generated/coverage_benchmark_p1_assessment.html](generated/coverage_benchmark_p1_assessment.html): FAM08/FAM02/FAM11を使ったP1 assessment packageのクイックHTML。
1. [docs/40_coverage_benchmark_p1_assessment_package.md](docs/40_coverage_benchmark_p1_assessment_package.md): Coverage BenchmarkのP1 assessment最小構成。
1. [data/coverage_benchmark_p1_assessment_plan.tsv](data/coverage_benchmark_p1_assessment_plan.tsv): P1 workstream、入力、出力、owner、timebox、Proceed/Kill条件。
1. [data/coverage_benchmark_family_reuse_matrix.tsv](data/coverage_benchmark_family_reuse_matrix.tsv): FAM08/FAM02/FAM11で同じrow構造を再利用できるかのmatrix。
1. [data/coverage_benchmark_p1_decision_rubric.tsv](data/coverage_benchmark_p1_decision_rubric.tsv): P1のProceed / Hold / Kill判定ルーブリック。
1. [generated/fam08_immediate_visibility_review.html](generated/fam08_immediate_visibility_review.html): FAM08が今日すぐProceed / Hold / Kill判定できるかを見るクイックHTML。
1. [docs/39_fam08_immediate_visibility_review.md](docs/39_fam08_immediate_visibility_review.md): `FAM08 stop-start low-speed` の即時可視性レビュー。
1. [data/fam08_immediate_visibility_triage.tsv](data/fam08_immediate_visibility_triage.tsv): FAM08のmarket fit、HILS重複、DTC snapshot、workflow fitを即時triageするTSV。
1. [docs/38_fam08_stop_start_low_speed_coverage_benchmark_sample.md](docs/38_fam08_stop_start_low_speed_coverage_benchmark_sample.md): `FAM08 stop-start low-speed` の1ページcoverage benchmark sample。
1. [data/fam08_stop_start_low_speed_coverage_benchmark_sample.tsv](data/fam08_stop_start_low_speed_coverage_benchmark_sample.tsv): FAM08 sampleのreview item、expected EPS facts、coverage question、HILS/bench scenario、Kill条件。
1. [docs/37_eps_coverage_benchmark_business_value.md](docs/37_eps_coverage_benchmark_business_value.md): Coverage Benchmark線でビジネス価値が出るかを、買い手・予算・代替・Kill条件まで深掘りしたレポート。
1. [data/eps_coverage_benchmark_business_value.tsv](data/eps_coverage_benchmark_business_value.tsv): business model別に市場需要、未解決痛み、買い手、予算経路、proof demo、Kill条件を整理したTSV。
1. [docs/36_eps_common_pain_productization_scan.md](docs/36_eps_common_pain_productization_scan.md): EPS共通pain familyから、スケール可能な事業候補を再抽出したレポート。
1. [data/eps_common_pain_business_scores.tsv](data/eps_common_pain_business_scores.tsv): 13 familyの共通性、サプライヤ制御性、差別化、スケール性のスコア表。
1. [data/eps_common_market_pain_reclassification.tsv](data/eps_common_market_pain_reclassification.tsv): 公開EPS case 30件の共通pain family再分類。
1. [docs/35_rca_8d_case_pack_viability_report.md](docs/35_rca_8d_case_pack_viability_report.md): `RCA / 8D Evidence Case Pack` が単独主商品として弱いことを検証したレポート。
1. [data/rca_8d_case_pack_viability_assessment.tsv](data/rca_8d_case_pack_viability_assessment.tsv): 成立条件、代替品、EPSサプライヤ適合、収益モデル、Kill条件の評価表。
1. [docs/34_eps_supplier_business_model_reassessment.md](docs/34_eps_supplier_business_model_reassessment.md): 上位ルール後に既存データを再評価し、主商品をcase packへ寄せた判断。現在はhistorical寄り。
1. [data/eps_supplier_business_model_reassessment.tsv](data/eps_supplier_business_model_reassessment.tsv): EPSサプライヤ視点の再評価表。現在はhistorical寄り。
1. [docs/20_existing_diagnostics_oem_boundary.md](docs/20_existing_diagnostics_oem_boundary.md): 既存DEM/UDS診断との差分、OEM領分、サプライヤ側の現実的な手札。
1. [docs/22_public_proxy_data_reset.md](docs/22_public_proxy_data_reset.md): 内部ケースにアクセスできない前提で、公開市場情報/Kaggle/公開CANデータで補える範囲を再定義。
1. [docs/27_s2e001_diagnostic_evidence_gap_check.md](docs/27_s2e001_diagnostic_evidence_gap_check.md): S2E001を既存DTC/freeze frameで説明できるか見るgap check。
1. [docs/28_s2e001_diagnostic_evidence_review_template.md](docs/28_s2e001_diagnostic_evidence_review_template.md): 内部DTC仕様を入れてProceed/Kill/Holdを判定するレビュー手順。
1. [docs/29_business_model_rebranch_after_s2e001_hold.md](docs/29_business_model_rebranch_after_s2e001_hold.md): S2E001 Hold後のビジネスモデル再分岐。
1. [docs/30_bmr001_market_pain_scenario_cards.md](docs/30_bmr001_market_pain_scenario_cards.md): BMR001の初期3枚scenario cardと商品化境界。最新では主商品ではなく前段材料。
1. [docs/31_bmr002_rfq_design_review_pack.md](docs/31_bmr002_rfq_design_review_pack.md): BMR001をRFQ/設計レビュー1ページへ変換したBMR002 sample。最新では主商品ではなく副産物。
1. [docs/23_public_proxy_demo_plan.md](docs/23_public_proxy_demo_plan.md): `Steering Context Risk Explorer` の代理デモ計画。
1. [generated/bmr002_rfq_design_review_pack.html](generated/bmr002_rfq_design_review_pack.html): BMR002 Scenario Readiness Pageのブラウザ表示。
1. [generated/bmr001_market_pain_scenario_cards.html](generated/bmr001_market_pain_scenario_cards.html): BMR001 scenario cardのブラウザ表示。
1. [generated/business_model_rebranch_after_s2e001_hold.html](generated/business_model_rebranch_after_s2e001_hold.html): 再分岐の意思決定ビュー。
1. [generated/s2e001_diagnostic_evidence_review_template.html](generated/s2e001_diagnostic_evidence_review_template.html): S2E001 review templateの意思決定ビュー。
1. [generated/s2e001_diagnostic_evidence_gap_check.html](generated/s2e001_diagnostic_evidence_gap_check.html): S2E001 gap checkの意思決定ビュー。
1. [generated/eps_scenario_to_evidence_pack.html](generated/eps_scenario_to_evidence_pack.html): Scenario-to-Evidence Packの意思決定ビュー。
1. [generated/low_speed_high_steering_proxy.html](generated/low_speed_high_steering_proxy.html): Phase 2の代表window可視化。
1. [generated/steering_context_risk_explorer_phase1_ja.html](generated/steering_context_risk_explorer_phase1_ja.html): ブラウザで見られるPhase 1静的デモ日本語版。
1. [generated/steering_context_risk_explorer_phase1.html](generated/steering_context_risk_explorer_phase1.html): Phase 1静的デモ英語版。
1. [data/eps_public_market_pain_cases.tsv](data/eps_public_market_pain_cases.tsv): NHTSA/recall/investigationから抽出したdriver-visible EPS painケース。
1. [data/public_steering_dataset_inventory.tsv](data/public_steering_dataset_inventory.tsv): 公開steering / CAN / Kaggle dataset棚卸し。

## プロジェクトSkill

このRepoでは、事業仮説の探索と検証をCodex側に寄せるため、プロジェクトSkillを追加している。

- `future-need-interviewing`: 顧客の最初のニーズ、最悪の未来、最高の未来、欲しい感情から本当のニーズを掘る。
- `chain-of-verification`: 叩き台の結論を検証質問に分解し、エビデンスで潰してから修正版を出す。
- `human-readable-reporting`: 人間向けレポートで、造語・商品名・phase名より先に自然言語で結論、業務文脈、判定条件を説明する。

## ビジネスモデル成立性の整理

今回追加した100案の整理では、以下を重視した。

- ECUメーカー起点で始められる
- OEMデータを初期前提にしない
- EPS / ECUの付加価値として説明できる
- HILS / bench / durability logでデモしやすい
- 将来OEM VHM / connected diagnosticsへ拡張できる

Best5:

| Rank | ID | Candidate |
|---:|---|---|
| 1 | BMFE020 | Health-ready EPS Feature Bundle |
| 2 | BMFE001 | EPS Health Indicator Set Licensing |
| 3 | BMFE031 | Offline Health Indicator Analyzer |
| 4 | BMFE041 | Return-part Health Summary Reader |
| 5 | BMFE096 | Co-development with Gear Maker |

推奨初手:

> Health Indicator Starter Kitを入口にして、Offline Health Indicator Analyzerでデモし、成功した指標をHealth-ready EPS Feature Bundleへ拡張する。

## 主要プロダクト仮説

### EPS Health Intelligence Package

過去の仮説。
EPSを、故障してからDTCを出す部品ではなく、劣化兆候と予測材料を持つhealth-aware subsystemにする方向を検討した。

現在は、`劣化兆候` や `内蔵証跡` を新規価値として主張するのは弱いと判断している。
以下の候補指標は、内部案件レビューで `実際に解析を進める証跡か` を確認するまでは仮説扱いにする。

候補指標:

- assist current / load proxy
- steering torque to motor current ratio
- current tracking warning count
- torque sensor redundancy / drift
- steering angle sensor redundancy / drift
- thermal derating accumulation
- low voltage stress history
- assist limitation recurrence
- high-load / low-speed event count
- end-stop / curb-hit-like event count
- transient abnormal recovery count

### Development Evaluation Indicator

ギア / ラック / 機械負荷を、ECU信号ベースのcontrol effort / stress / margin indicatorで比較する。
ただし、開発時の外付けモニタとの差分が弱いため、現在は主軸から下げている。

### Common ECU Hardware Health Layer

EPS固有メカ指標に閉じず、電源、温度、リップル、brownout、reset、capacitor stressなど、ECU横断で使えるhardware health evidenceへ広げる。
これは将来ピボットとして残すが、現在のEPSサプライヤ視点では、先に返却品・NTFケースの不足証跡分類を行う。

## リポジトリ構成

```text
AGENTS.md
  Repo-wide operating rule: market demand -> hypothesis -> solution.

docs/
  00_context.md
  01_business_model_options.md
  02_option_comparison.md
  03_supplier_scope.md
  04_project_charter_diagnostic_evidence.md
  05_risks_and_open_questions.md
  06_next_actions.md
  07_market_needs_and_positioning.md
  08_ota_connected_health_market.md
  09_feasibility_and_targeting.md
  10_project_charter_eps_health_intelligence.md
  11_virtual_health_sensor_market.md
  12_reset_hypothesis_development_evaluation.md
  13_business_scheme_reset.md
  15_public_driving_data_proxy_simulation.md
  16_common_ecu_hardware_health_pivot.md
  17_customer_value_reality_check.md
  18_market_research_customer_pain.md
  19_market_research_eps_event_context.md
  20_existing_diagnostics_oem_boundary.md
  21_value_of_ntf_case_classification.md
  22_public_proxy_data_reset.md
  23_public_proxy_demo_plan.md
  24_steering_context_risk_phase1.md
  25_low_speed_high_steering_proxy_phase2.md
  26_scenario_to_evidence_pack_direction.md
  27_s2e001_diagnostic_evidence_gap_check.md
  28_s2e001_diagnostic_evidence_review_template.md
  29_business_model_rebranch_after_s2e001_hold.md
  30_bmr001_market_pain_scenario_cards.md
  31_bmr002_rfq_design_review_pack.md
  32_market_demand_solution_framing.md
  33_public_data_validation_scn001.md
  34_eps_supplier_business_model_reassessment.md
  35_rca_8d_case_pack_viability_report.md
  36_eps_common_pain_productization_scan.md
  37_eps_coverage_benchmark_business_value.md
  38_fam08_stop_start_low_speed_coverage_benchmark_sample.md
  39_fam08_immediate_visibility_review.md
  40_coverage_benchmark_p1_assessment_package.md
  41_coverage_benchmark_artifact_request_pack.md
  42_coverage_benchmark_artifact_intake_result.md
  43_coverage_benchmark_forced_conclusion.md
  48_steering_ecu_cyber_value_check.md
  49_steering_ecu_cyber_kill_evidence_dossier.md
  50_next_exploration_plan_after_cyber_kill.md
  51_steer_by_wire_kill_first_review.md
  52_sovd_kill_first_review.md
  53_public_market_monitor_input_only.md
  54_steer_by_wire_business_deep_dive.md
  55_sbw_redundancy_degraded_one_page_sample.md
  56_sbw_decision_materials.md
  57_sbw_8_material_verification.md

data/
  business_model_research.tsv
  business_model_feasibility_100.tsv
  business_model_feasibility_sources.md
  best5_business_model_candidates.md
  demo_eps_health_summary_examples.tsv
  customer_pain_market_signals.tsv
  eps_public_market_pain_cases.tsv
  eps_event_context_market_research.tsv
  eps_ntf_case_classification_value_map.tsv
  eps_ntf_case_review_template.tsv
  public_steering_dataset_inventory.tsv
  steering_context_risk_phase1_summary.tsv
  low_speed_high_steering_proxy_summary.tsv
  low_speed_high_steering_proxy_windows.tsv
  low_speed_high_steering_proxy_timeseries.tsv
  eps_scenario_to_evidence_pack.tsv
  s2e001_diagnostic_evidence_gap_check.tsv
  s2e001_diagnostic_evidence_review_template.tsv
  business_model_rebranch_after_s2e001_hold.tsv
  bmr001_market_pain_scenario_cards.tsv
  bmr002_rfq_design_review_pack.tsv
  market_demand_solution_map.tsv
  public_data_validation_sources.tsv
  scn001_public_data_evidence_readiness.tsv
  eps_supplier_business_model_reassessment.tsv
  rca_8d_case_pack_viability_assessment.tsv
  eps_common_market_pain_reclassification.tsv
  eps_common_pain_business_scores.tsv
  eps_coverage_benchmark_business_value.tsv
  fam08_stop_start_low_speed_coverage_benchmark_sample.tsv
  fam08_immediate_visibility_triage.tsv
  coverage_benchmark_p1_assessment_plan.tsv
  coverage_benchmark_family_reuse_matrix.tsv
  coverage_benchmark_p1_decision_rubric.tsv
  coverage_benchmark_artifact_request_pack.tsv
  coverage_benchmark_artifact_intake_result.tsv
  coverage_benchmark_artifact_intake_decision.tsv
  coverage_benchmark_internal_placeholder_screening_sheet.tsv
  coverage_benchmark_forced_conclusion.tsv
  steering_ecu_cyber_value_check.tsv
  steering_ecu_cyber_kill_evidence_dossier.tsv
  steering_ecu_cyber_kill_questions.tsv
  next_exploration_candidates_after_cyber_kill.tsv
  steer_by_wire_kill_first_review.tsv
  sovd_kill_first_review.tsv
  public_market_monitor_input_plan.tsv
  steer_by_wire_business_deep_dive.tsv
  steer_by_wire_redundancy_degraded_sample.tsv
  sbw_decision_materials.tsv
  sbw_8_material_verification.tsv
  public_proxy_data_sources.tsv
  useful_items_for_steering_diagnostic_evidence.md
  ota_connected_health_market_signals.tsv
  target_feasibility_matrix.tsv
  eps_health_indicator_candidates.tsv

generated/
  coverage_benchmark_forced_conclusion.html
  coverage_benchmark_artifact_intake_result.html
  coverage_benchmark_artifact_request.html
  coverage_benchmark_p1_assessment.html
  fam08_immediate_visibility_review.html
  public_data_validation_scn001.html
  market_demand_solution_framing.html
  bmr002_rfq_design_review_pack.html
  bmr001_market_pain_scenario_cards.html
  business_model_rebranch_after_s2e001_hold.html
  s2e001_diagnostic_evidence_review_template.html
  s2e001_diagnostic_evidence_gap_check.html
  eps_scenario_to_evidence_pack.html
  low_speed_high_steering_proxy.html
  steering_context_risk_explorer_phase1_ja.html
  steering_context_risk_explorer_phase1.html

scripts/
  extract_low_speed_high_steering_proxy.py
```

## 現在の次アクション

- 以後の提案は `AGENTS.md` の上位ルールに従い、市場需要 -> 未解決の痛み -> 仮説 -> 解決策 -> 買い手 -> 初期提供物 -> 検証方法 -> Kill条件で書く
- 旧テーマはArchiveとして閉じる。詳細は [docs/68_repo_closure_inventory.md](docs/68_repo_closure_inventory.md) と [data/repo_closure_inventory.tsv](data/repo_closure_inventory.tsv) を参照する
- motion health新テーマも外販テーマとしてはArchive。最終判断は [docs/archive/motion_health/75_motion_health_mhq001_final_decision.md](docs/archive/motion_health/75_motion_health_mhq001_final_decision.md) を参照する
- RDI / OEM remote diagnostics系は [docs/archive/oem_remote_diagnostics/README.md](docs/archive/oem_remote_diagnostics/README.md) を入口にArchive参照する
- RDI001〜RDI006の公開情報調査は [docs/archive/oem_remote_diagnostics/81_rdi001_006_research_report.md](docs/archive/oem_remote_diagnostics/81_rdi001_006_research_report.md) と [data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi_research_findings.tsv](data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi_research_findings.tsv) を参照する
- RDI006の4列sampleは [docs/archive/oem_remote_diagnostics/82_rdi006_thermal_limit_4_column_sample.md](docs/archive/oem_remote_diagnostics/82_rdi006_thermal_limit_4_column_sample.md) と [data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_thermal_limit_sample.tsv](data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_thermal_limit_sample.tsv) に置いた
- RDI006の穴埋めPDCAは [docs/archive/oem_remote_diagnostics/83_rdi006_program_gap_pdca.md](docs/archive/oem_remote_diagnostics/83_rdi006_program_gap_pdca.md) と [data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_program_gap_filled.tsv](data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_program_gap_filled.tsv) に置いた
- 次に作業する場合は、[docs/84_kaggle_problem_setting_lens.md](docs/84_kaggle_problem_setting_lens.md) を入口に、Bosch型をEPS製造 / EOL検査へ読み替える
- 過去のmotion health調査は [docs/archive/motion_health/79_motion_health_archive_index.md](docs/archive/motion_health/79_motion_health_archive_index.md) と [data/archive/motion_health/motion_health_archive_links.tsv](data/archive/motion_health/motion_health_archive_links.tsv) から参照する
- 「EPS交換時期を当てる」方向には戻さない
