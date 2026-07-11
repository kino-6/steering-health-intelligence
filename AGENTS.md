# Repository Operating Rule

このRepoの事業仮説、調査、デモ、ドキュメント更新では、以下を最上位ルールにする。

## Personal Public-Only Research Rule

このRepoの活動は、**現段階では仕事(所属組織の業務)ではない**。個人の事業仮説研究である。

1. **内部情報・内部資料は使わない。使う予定もない。**(所属先のprogram仕様、RFQの中身、Dem設定、保証データ、社内部署の意向などすべて)
2. したがって、内部資料の確認を次アクション・実施条件・再開条件として**ユーザに提案しない・尋ねない**。内部資料がないと閉じない判断(例: docs/123の質問シート回答、docs/138のBM-KQ1〜3)は、「ここから先は内部の領域」という**境界の記録**として文書に残すだけにする。以後この話題を蒸し返さない
3. 成果物の宛先は**技術者(エンジニア)**である。営業・経営向けの体裁より、根拠・再現性・限界の明示を優先する
4. Demoの方針: **公開データのlogから、人間には読み取れない兆候を機械的に読み取り、SOTIF(運用フェーズ監視、EooCの仮定検証)へ部品側として参加できる形**を見せる
5. **結論の書き方**: 判断を先に、根拠を箇条書きで。日本語を優先し、専門語・英語には言い換えを添える。**「内部情報があれば分かる」を結論・次の一手・締めの言葉にしない**——問いは公開情報の枠内で閉じる(内部依存の論点は「ここで問いを閉じる」と書いて終える)
6. **公開による反応測定をしない**: リポジトリや成果物を公開して問い合わせ・反論・関心を測る「公開の需要試験」は行わない(2026-07-11 ユーザ却下)。理由: 実務者の反応を引き出す設計は、内部情報を持つ人からの情報流入経路を作ることと不可分であり、「内部情報を使わない」方針の趣旨(入手経路を作らない)に反する。公開・発信はユーザの明示指示がある場合のみ
7. **ビジネス判断は外から組み立てる**: 支払い意思・市場成立の判断を「内部情報がないと分からない」で止めない(それは判断の放棄であり三流)。競合の製品行動(継続投資・量産開発は支払い意思の最も硬い証拠)、買収の事実、規制の時間表、過去の先例の類型(法規化でタダ化した機能/有償化に成功した機能)、価格と工数の桁感——**公開の構造証拠で最も確からしい判断を下し、必ず誤り条件(何が観測されたらこの判断は間違いか)を添える**
7. **実行の自律性(ユーザの手番を最小化する)**: ユーザは包括許可(`Bash(git *)`、`Bash(python3 *)`、`Bash(curl *)` 等 + `defaultMode: acceptEdits`)を `.claude/settings.local.json` に設定済みであり、「常識の範囲内で止めずに実行してよい」と明示している。確認質問は設計判断・方針転換に限る。許可設定の手編集は承認記録の自動書き込みと競合するため、変更が要る場合はセッション開始直後か `/permissions` UIで行う(このセッションで2回競合が実際に起きた教訓)

## Market Demand First

必ず次の順で提示する。

1. 市場需要
2. 未解決の痛み
3. 仮説
4. 解決策
5. 買い手 / 利用者
6. 初期提供物
7. 検証方法
8. Kill条件

悪い提示:

> EPSにこういう公開事例がある。

良い提示:

> 市場ではloss of assist、低速高操舵、警告灯+DTC、intermittent assist loss、stop-start、software/failsafeなどのEPS共通pain familyが繰り返し問題化している。EPSサプライヤは、各scenarioに対して既存DTC/freeze frame/extended data、reader、HILS/bench評価がどこまで説明・再現できるかをCoverage Benchmarkとして提示できる。

## Natural Language First

レポートや結論では、造語、商品名、略称、phase名を先に出さない。
必ず先に、自然言語で以下を説明する。

1. 何を判断しているのか
2. 誰のどの業務の話なのか
3. 何が分かれば進み、何が分かれば止めるのか
4. 既存業務、既存診断、既存評価と何が違う可能性があるのか

悪い提示:

> P1 paid assessmentとしてCoverage BenchmarkはNo-Go。P0 ScreeningだけProceed。

良い提示:

> 現時点では、有償サービスとして売りに行く段階ではない。内部資料を使わない前提では、対象EPSのHILS試験名、関連DTC、freeze frame / extended data項目、既存レビュー会議体を見られず、既存レビューとの差分を示せないためである。これらの4項目は、内部資料を使える条件になった場合だけの再開条件として扱う。

使ってよい言葉:

- `Coverage Benchmark`
- `P0`
- `P1`
- `Evidence Pack`
- `Readiness`
- `screening`

ただし、これらは自然言語で意味を説明した後にだけ使う。
読者がその単語を知らなくても、結論と次アクションが理解できる状態にする。

## EPS Supplier Lens

このRepoの結論は、必ずEPSサプライヤの立場に帰着させる。

市場、OEM、エンドユーザ、サービス、connected platform、規制、Kaggle/公開データをメタ視点で見るのはよい。
ただし、最終判断は以下で締める。

- EPSサプライヤとして何を売るか
- EPSサプライヤとして何を実施できるか
- EPSサプライヤとして何を言ってはいけないか
- OEM領域、サービス領域、fleet platform領域として初期対象外に置くものは何か
- 次にEPSサプライヤ内のどの部署に見せるか

悪い結論:

> OEMや市場にはこういう需要がある。

良い結論:

> 市場にはこういう需要がある。そのうちEPSサプライヤが初期に取れる手札は、EPS共通scenarioに対する既存DTC/freeze frame/extended data、reader、HILS/bench評価のCoverage Benchmarkである。RCA/8DやOEM保証DB連携は主商品ではなく、副次用途またはoptional extensionに置く。

## Kaggle / Public Proxy Predictive Value Rule

Kaggleや公開データを見るときの主目的は、EPSサプライヤが「予測のような付加価値」を作れる余地があるかを探索することである。

ここでいう「予測のような付加価値」とは、個車のEPS残寿命、交換時期、故障発生、安全保証、保証費削減、root causeを当てることではない。
公開proxyから、操舵要求、路面・振動exposure、使用負荷class、通信異常context、熱や走行環境の負荷傾向などを先読みまたは分類し、それがEPSサプライヤの製品価値、診断価値、サービス価値、品質改善価値に変わるかを見ることである。

「実使用条件からEPS評価・診断の問いを作る」ことを主目的にしない。
評価scenario、診断質問、顧客説明質問は、予測的な付加価値候補を検証するための副次artifactである。
それ自体を最終成果物や有償価値として扱わない。

Kaggle調査の成果物は、各IDや各proxyについて、最低限次を自然言語で整理する。

1. 誰が、どの業務で、何を先読みできると嬉しいのか
2. その先読みがEPSサプライヤの価値になる理由
3. 公開proxyで何が見え、何が見えないのか
4. 既存の評価、診断、品質、サービス業務と何が違う可能性があるのか
5. EPSサプライヤとして売る / 内部で使う / 言ってはいけないこと
6. 何が確認できなければKillするか

Kaggle/Bosch/Mercedesを、製造品質、EOL検査、評価時間短縮だけへ閉じない。
それらは別枝または補助材料であり、現行の中心は「予測のような付加価値がEPSサプライヤ側に残るか」である。

## Steering Predictive Diagnostics Value Rule

Bosch predictive diagnostics / predictive maintenance / vehicle health から派生した `SPD` 系の調査では、診断読み順、顧客説明、品質feedback、追加ログschemaを最終目的にしない。
これらは、EPSサプライヤが「予測のような付加価値」を持てるかを検証するための副次artifactである。

現行の中心は、EPSがruntimeで「普段と違う」状態を内部重要モジュール単位で検知、分類、説明できるかである。
ここでいう「普段と違う」は、個車のEPS残寿命、交換時期、故障発生、安全保証、保証費削減、root causeを当てることではない。
過去一定期間、同一条件、標準データ、設計上の期待応答、または既存monitorの境界に対して、入出力や状態遷移が通常範囲内だが偏っている、揺らいでいる、繰り返している、または依存contextと同時に出ていることを指す。

SPD008では、EPS製品全体をE2Eで見て「普段と違う」と言わない。
E2Eでは路面、タイヤ、車両重量、運転者、上位制御、外部ECU、電源、温度などの外乱が混ざり、外乱とEPS内部状態を切り分けにくい。
したがって、対象は torque / angle sensor plausibility、motor / inverter response、power monitor、thermal derating、communication input validity のような内部重要モジュール単位に限定する。

SPD008 / SPD002 / SPD003 / SPD004 などを扱うときは、必ず次の順に判断する。

1. 市場需要: 誰が、どの業務で、故障確定前または原因未確定の状態を早く知りたいのか
2. 予測的価値: 何を先読み、分類、早期検知、または状態説明できると嬉しいのか
3. EPSサプライヤの手札: EPS内部モジュール、既存monitor、設計上の期待応答、状態遷移、calibration境界、ログtriggerとして何を持てるのか
4. 既存monitorとの差分: 既存DTC、freeze frame、extended data、DEM/UDS、service manual、既存品質業務で十分ではないか
5. 事業上の出力: 製品価値、診断価値、品質改善価値、顧客技術説明価値、vehicle health基盤への部品側contributionのどれになるのか
6. 副次artifact: 診断読み順、顧客説明、品質feedback、追加ログschemaは上記を検証するためにだけ作る
7. 禁止主張: EPS RUL、交換時期、安全保証、root cause、保証費削減、外乱原因断定を言っていないか

悪いNext Action:

> SPD008の2サンプルを診断企画向け1枚schemaに落とす。

良いNext Action:

> SPD008の2サンプルについて、runtimeで普段と違う状態を内部重要モジュール単位で検知・分類できるか、既存monitorとの差分があるか、EPSサプライヤの製品価値・診断価値・品質改善価値・顧客技術説明価値・vehicle healthへの部品側contributionのどれに転記できるかを確認する。その検証のために、必要なら診断読み順や追加ログschemaを副次artifactとして作る。

SPD系で `Proceed` と書く場合は、「診断資料として作れる」では不十分である。
必ず、predictive diagnostics / predictive maintenance / vehicle health の文脈で、EPSサプライヤが何を売る、何を内部実施する、何を言ってはいけないかまで書く。

## OEM Usage Translation Rule

「駐車場 + 低速 + 大舵角 + 凹凸」のような表現を、有望用途や商品価値として先に出さない。
駐車場はほぼ全ての乗用車に関係する既知の使われ方であり、それ自体を見つけてもEPSサプライヤの差分にはなりにくい。

「平均的な乗用車ではなく使われ方が厳しい用途を特定する」という言い方にも注意する。
そのままだと、OEMが決める車両コンセプト、用途想定、サービス設計の領域に入る。
EPSサプライヤはOEMの車両コンセプトを公開proxyだけで代替定義しない。

現行探索で見るべき価値は、OEMが想定する車両用途や使われ方を、EPSサプライヤ側の確認観点、提案観点、説明境界へ翻訳できるかである。

具体的には、次へ転記できるかを見る。

1. RFQで確認すべき低速取り回し、反復操舵、路面外乱、温度、電源、通信の質問
2. 評価企画で厚く見るべき使用条件と、既存評価で足りる条件の切り分け
3. 診断企画で使用contextとして説明してよいことと、DTCや内部状態がないと説明してはいけないこと
4. 顧客技術説明で、EPSの製品価値として言えることと、故障予測や原因断定に見えるため避けること

公開proxyは、OEM用途想定を決めるためではなく、OEM用途想定を受けたときにEPSサプライヤが返すべき確認質問や説明境界を準備するために使う。

## Mandatory Rule Check Before Stop / Kill / Archive

このRepoで `Stop`、`Kill`、`Archive`、`No-Go`、`全滅`、`閉じる` といった結論を書く前に、必ず上位ルールを参照したRule Checkを本文に明示する。
Rule Checkを書いていない結論は、最終判断ではなくdraft扱いにする。

最低限、次を確認する。

1. 今回の判断に関係する上位ルールを、`AGENTS.md` のどの節から適用したか
2. 市場需要から始まっているか
3. 自然言語で、誰のどの業務の話かを説明しているか
4. EPSサプライヤとして何を売る / 実施する / 言ってはいけないかに戻っているか
5. Kill理由が、上位ルールで禁止または制限された旧ロジックに戻っていないか
6. 具体的な再開条件または次の検証質問があるか

特に `Kaggle / Public Proxy / Predictive Value` 系で `Stop`、`Kill`、`Archive`、`全滅` と書く前には、必ず次を明示する。

1. Kill理由が「EPS内部状態、DTC、freeze frame、extended data、assist state、交換結果が見えないから」になっていないか
2. それを主Kill理由にしていないか
3. 代わりに、以下で判断しているか
   - EPSサプライヤの業務成果物に転記できるか
   - 汎用テレマティクス、路面分類、ADAS、IDSと区別できるか
   - 故障予測、交換時期、保証費削減、原因断定に寄らず価値説明できるか
4. 内部事実不足は、故障予測や原因断定を禁止する境界として扱い、公開proxy価値そのものの主Kill理由にしていないか

このRule Checkに失敗した場合は、結論を出さず、まず判断軸を修正する。

## Current Main Hypothesis

旧テーマはArchive扱いにする。
旧テーマとは、乗用車向けEPS単体について、公開情報だけを使い、故障予測、劣化兆候通知、追加ログ、公開市場pain分類、Coverage Benchmark、汎用SbW説明支援、SOVD基盤支援を外販商材にできるかを探した一連の探索である。
現行条件では、この方向は閉じる。

次のLLMは、まず [docs/61_llm_kill_knowledge_base.md](docs/61_llm_kill_knowledge_base.md) を前提知識として読むこと。
現行条件では外販ビジネスとしてProceedできる強い手札はほぼ残っていない。
過去にKillした仮説を、名前や英語ラベルだけ変えて再提案しない。

追加で検証した新ブランチも、EPS/SbWサプライヤ単独の外販テーマとしてはArchiveする。

> 自動運転・商用車両群向けの操舵系運行可否 / 点検優先度判断

このブランチでは、EPS単体の寿命を当てるのではなく、自動運転車両、配送車、商用車、シャトルなどの車両群で、操舵系を含む重要部品について、次の運行に出してよいか、次回点検まで持つか、先に入庫させるべきかを判断できるかを見た。

最終判断は [docs/archive/motion_health/75_motion_health_mhq001_final_decision.md](docs/archive/motion_health/75_motion_health_mhq001_final_decision.md) に置いた。
結論は、fleet downtimeや診断時間短縮の市場需要はあるが、EPS/SbWサプライヤ単独の外販テーマとしてはStop / Archiveである。
理由は、必要データがOEM/fleet/platform契約に依存し、既存remote diagnosticsがDTC severity、action plan、API連携、診断時間短縮をすでに強く扱っているためである。

追加で検証した以下の作業仮説も、内部資料を使わない現行ルールではArchiveする。

> OEM遠隔診断に組み込む操舵系状態説明レイヤー

これはfleet監視サービスではない。
OEM remote diagnostics networkに、EPS/SbWサプライヤが操舵系の説明ロジックを提供する仮説である。
価値は、EPS内部データから、DTCだけでは分からない状態説明、追加で読むべきDID、service側に出す注意文、言ってよいことと言ってはいけないこと、field-to-engineering feedbackを作ることである。

最初に読む資料は [docs/archive/oem_remote_diagnostics/README.md](docs/archive/oem_remote_diagnostics/README.md) である。
過去のmotion health調査は [docs/archive/motion_health/79_motion_health_archive_index.md](docs/archive/motion_health/79_motion_health_archive_index.md) にArchiveする。

この仮説のArchive判断は以下である。

公開情報だけでは、EPS/SbW固有DID、freeze frame、assist / limit state、thermal indicators、software / calibration ID、service note転記先、service outcome feedbackが埋まらない。
既存remote diagnosticsはDTC description、severity、action plan、service routingをすでに強く扱う。
したがって、現行条件では外販テーマとしてStop / Archiveとする。

再開できるのは、特定OEM programで以下が確認できる場合だけである。

1. EPS/SbW固有のDTC、DID、freeze frame、extended data、assist state、limit state、software/calibration IDへ触れる
2. 整備履歴、交換結果、再発有無、作業時間の少なくとも一部へ接続できる
3. 既存remote diagnosticsのseverity / action planでは足りない操舵系固有の判断がある
4. 出力が、交換時期予測ではなく、運行可否、入庫優先度、診断読み順、顧客説明へ落ちる
5. 安全保証、root cause断定、交換時期予測、既存remote diagnostics置換を主張しない

追加で検証したKaggle / 公開proxyによる予測的付加価値探索は、前回いったん「全滅 / Archive」としたが、この判断は補正済みである。
EPS内部状態、DTC、freeze frame、交換結果が見えないことを主Kill理由にしてはいけない。

この探索では、Kaggleを「公開データ」ではなく「企業や研究者が外に出した問題設定」として読み、EPSサプライヤが予測のような付加価値を作れる余地があるかを見た。
入口は [docs/84_kaggle_problem_setting_lens.md](docs/84_kaggle_problem_setting_lens.md) と [data/kaggle_problem_setting_lens.tsv](data/kaggle_problem_setting_lens.tsv) に置く。
補正前の判断は [docs/95_predictive_value_continue_final_decision.md](docs/95_predictive_value_continue_final_decision.md) に置く。
最新判断は [docs/96_predictive_value_internal_fact_correction.md](docs/96_predictive_value_internal_fact_correction.md) に置く。

最新結論は、Kaggleにあったネタは全滅ではない、である。
公開proxyから、操舵要求、路面・振動exposure、使用負荷class、通信異常context、熱や走行環境の負荷傾向などを先読みまたは分類できる可能性は残る。
ただし、それはEPS故障予測、交換時期予測、安全保証、保証費削減、root cause断定ではない。

残すものは、PVC001を本線、ULC008を最有力候補、ULC004を二番手候補、PVC004を境界候補として、公開proxyだけでEPSサプライヤの業務価値へ転記できるかを見る方向である。
次にやるなら、製品企画、診断企画、品質改善、評価企画、顧客技術説明、サイバー担当のどの成果物に、使用条件classや通信異常contextを転記できるか確認する。
内部事実が見えないことは、故障予測や原因断定を禁止する境界として使う。
しかし、それだけでKaggle / 公開proxy方向をKillしてはいけない。

Kaggleを、EPS市場故障予測やRDI006の内部data field穴埋めには使わない。
「実使用条件からEPS評価・診断の問いを作る」だけを成果物にしない。
評価scenario、診断質問、顧客説明質問は、予測的な付加価値候補を検証するための副次artifactであり、現行では外販価値として扱わない。

以下は旧テーマArchiveと過去探索の詳細であり、現在の探索優先順位ではない。

SOVD / next-generation diagnostics content designはextensionとして扱う。
OEM診断基盤依存が強いため、EPSサプライヤが主語になれるのはUDS/DTC/DID/freeze frame/software ID/security accessを次世代診断コンテンツへ整理する部分までである。

Public recall / ODI / TSB monitorは単体商品にしない。
Steer-by-wireとSOVDの市場入力、設計レビュー質問、RFQ質問生成にだけ使う。

直近レビュー後の判断:

- Steer-by-wireは、従来EPSからの市場変化があるため探索継続。ただし、汎用安全支援や汎用cyber支援は既存ISO 26262 / SOTIF / CSMS業務と被るため追わない。残す場合は、fail-operational / degraded state / redundancyをEPSサプライヤのcomponent boundaryで説明できる部分に限定する。
- SOVDは主商品にしない。SOVD platform / server / API / ODX / UDS変換は既存標準・既存ツール領域である。残す場合は、EPSのDTC、DID、freeze frame、extended data、software ID、security accessを次世代診断でどう見せるかというcontent designに限定する。
- Public recall / ODI / TSB monitorは単体商品にしない。市場シグナルを売るのではなく、Steer-by-wireとSOVDの設計質問・診断質問・禁止主張を作る入力に限定する。

Steer-by-wire深掘り後の現在地:

- 残すのは、SbW汎用安全支援ではない。既存の安全・サイバー・診断・software update成果物を、OEM説明、RFQ回答、診断コンテンツ設計に転記しやすくするcomponent-boundary整理だけである。
- `road wheel actuator`、`front axle actuator`、`steering rack actuator` のような表現を先に出さない。まず「車輪を動かす側の部品」「車輪側操舵ユニット」と平易に言い、必要な場合だけ括弧で英語名を添える。
- 初期提供物は、異常時状態マップ、既存成果物リンク表、診断コンテンツ質問表、禁止主張リストの4点に絞る。
- 「車輪を動かす側の冗長系が一部落ちた」1ケースsampleは作成済み。これが既存safety caseの焼き直しに見えるならKillする。
- 判断材料として、ZF、Mercedes-Benz、Tesla、Lexus、HELLA、NHTSA、VCAの公開情報を整理済み。公開情報は市場変化と既存業務重複を示す材料であり、商品価値の証明には使わない。
- 8項目を公開情報で検証した結果、architecture、degraded state、FMEA、DTC coverageはPartial、software/calibration、security access、OEM質問、既存回答templateはUnknown。
- 現行方針では内部資料を要求しない。したがって、SbW方向は公開情報だけで外販Proceedしない。内部資料確認を次アクションに置かず、公開情報だけで示せる価値がなければKillする。
- この段階での次アクションは、公開情報だけで作った1ケースsampleが、EPSサプライヤの公開営業資料・RFQ一般論・診断標準動向に対して独自の判断を出せるかを見ることだった。後続レビューで、SbW汎用説明支援は有償サービスとしてNo-Goに下げた。
- 追加の公開情報収集では、Bosch、ZF、Nexteer、Schaeffler、HELLA、JTEKT、Tesla、NHTSA、VCA、R79、ASAM SOVDを見た。市場変化はあるが、fault strategy、verification、FMEA/FTA、safe state、driver warning、DTC coverage、SOVD fault informationは既存安全・認証・診断論点として既に強い。
- よって現時点のSbW判断は、公開情報だけでは有償offerにしない。次にやる場合も、「車輪を動かす側の冗長系が一部落ちた」1ケースが既存資料の要約を超え、EPSサプライヤが言えること / 言ってはいけないことを自然言語で切れるかだけを見る。
- さらに深掘りした結論として、Steer-by-wire向けの説明資料整理支援も、汎用の有償サービスとしてはNo-Goである。市場変化はあるが、異常時説明、安全設計、認証、診断、ソフト更新、顧客説明には既存業務の持ち主がいる。残すなら、特定案件で既存資料をOEM向け1枚へつなぐ短期支援だけである。

SOVD / 次世代診断コンテンツ深掘り後の現在地:

- 次世代診断は、公開情報上、classic ECU、fault entry、environment data、measurement、identification、routine、configuration、software updateを扱う方向に進んでいる。
- ただし、SOVD基盤、SOVD server、SOVD stack、ODX/UDS変換、API検証、authoring、trainingは既存標準・既存ツール領域である。EPSサプライヤの外販商品として追わない。
- 残すなら、DTC、DID、freeze frame、extended data、software/calibration ID、routine、security accessを、近接整備、リモート診断、車内診断、製造、開発の利用場面ごとに公開/制限/禁止へ整理するcontent mapだけである。
- 25件の仮診断コンテンツproxy demoは作成済み。対象EPSの実DTCではなく、公開範囲、権限、禁止操作、安全影響、software/calibration接続が自然言語で切れるかを見るための表である。
- これが既存DTC/DID表、ODX authoring、security access表の整形にしか見えなければ、SOVD / 次世代診断方向もStopする。
- 現時点では、有償サービスとして売らない。残す場合も、特定programで既存診断仕様、security access、software update、顧客技術説明をOEM向けに短くつなぎ直す短期支援だけである。

## Recently Killed / Deprioritized

`EPS / steering ECU software/cyber evidence pack` は、広い商品としてはKillする。
サイバーセキュリティ設計証拠とSBOM / 脆弱性対応は分けず、診断アクセス、ソフト更新、software/calibration ID、SBOM、CVE impact triage、security access、fail-safe stateをcomponent-level evidenceとして束ねる。

初期offerは、SaaSではなく固定スコープassessmentとして扱う。
目的は、既存CSMS/TARA/SBOM/CVE運用の代替ではなく、steering ECU固有の診断アクセス、ソフト更新、SBOM-to-function impact、fail-safe state、OEM回答文への接続に差分があるかを確認すること。
既存業務に同等成果物があるならKillする。

最新判断では、この方向はかなりKill寄りのHoldである。
ETAS、Ansys、Siemens、ThreatZなど既存プレイヤーがTARA、SBOM、vulnerability management、ISO/SAE 21434、UN R155/R156対応をすでに厚く扱っているため、汎用サイバー/SBOM商品としては追わない。
残す場合も、steering ECU固有のOEM問い合わせ回答に既存成果物を翻訳する薄い支援に限定する。

Kill判断用の現行ルール:

- 汎用TARA / SBOM / CVE management / ISO21434 / UN R155/R156 supportはKill
- steering ECU固有のOEM回答翻訳だけ最後の存在確認対象
- KQ1「steering ECU固有のOEM cyber/SBOM/CVE問い合わせが実際に来ているか」がNoならKill
- KQ2-KQ5「既存CVE回答、診断security、安全状態mapping、OEM回答template」に3つ以上YesならKill
- KQ1がYesかつKQ2-KQ5で2つ以上Noの場合だけ、短期OEM回答支援として残す

## Historical Main Hypothesis

以下はhistoricalとして扱う。

> EPS Diagnostic / Robustness Coverage Benchmark

市場需要:

- loss of assist、低速高操舵、警告灯+DTC、intermittent assist loss、stop-start、software/failsafeなどのEPS共通pain familyが公開市場で繰り返し出ている
- 既存DTC / freeze frame / extended data / readerが、その共通scenarioをどこまで説明できるかをprogram横断で比較しにくい
- HILS / bench / vehicle evaluationで再現すべき市場scenarioが、公開caseから体系化されにくい
- 個別RCA/8Dは製品/OEM/案件固有で、主商品にするとスケールしない

解決:

- 公開EPS caseを共通pain familyへ分類する
- 各familyに対して、既存DTC / freeze frame / extended data / reader / HILS / bench評価のcoverage matrixを作る
- 現行診断で足りる、足りない、不要を分ける
- program / generation間でcoverage差分を比較する
- RCA/8Dや顧客品質報告は、coverage結果を転記する副次artifactとして扱う

現行判断:

- 内部資料なしでは有償assessmentとしてNo-Go
- 公開データ分析継続はStop
- SaaS/HILツール化はKill
- RCA/8D主商品化はKill
- 内部資料を使える条件になった場合だけ再開条件として残す

## Historical Notes

過去の以下の方向はhistoricalとして扱う。最新結論としてそのまま採用しない。

- EPS故障予測
- 劣化兆候通知
- Health-ready EPS Feature Bundle
- ECU追加ログそのもの
- OTA / remote diagnosticsを主商品にする案
- Market Pain Scenario Library単体
- RFQ / Design Review Pack単体
- RCA / 8D Evidence Case Pack単体

これらは、`EPS Diagnostic / Robustness Coverage Benchmark` の材料、副次用途、またはoptional extensionとしてのみ使う。

## Required Output Shape

新しい提案や調査結果は、最低限この形にする。

| Field | Required content |
|---|---|
| Market demand | 誰が、どの業務で、何に困っているか |
| Evidence signal | 需要を示す公開情報、Repo内データ、または明示した推論 |
| Hypothesis | その需要に対して何が売れると考えるか |
| Solution | 成果物、workflow、schema、template、demo |
| Buyer / user | 初期に使う部署と役割 |
| Why supplier can play | OEM領域ではなく、EPSサプライヤ側で持てる手札 |
| EPS supplier conclusion | EPSサプライヤとして売る/やる/やらない判断 |
| Demo | 20-50件の調査、1ケースsample、TSV/HTMLなどで何を見せるか |
| What not to claim | 故障予測、保証費削減、root cause断定など禁止主張 |
| Kill criteria | 何が確認できなければ止めるか |

上記の各項目は、まず自然言語で書く。
表やTSVでは短いラベルを使ってよいが、本文側ではそのラベルの意味を説明する。

## CoVe Rule

結論を出す前に、以下を必ず確認する。

- これは市場需要から始まっているか
- 単に `こういう事例がある` と言っていないか
- 買い手の業務成果物に転記できるか
- 結論がEPSサプライヤの立場に戻っているか
- OEM保証DB、fleet data、サービスツールに過度依存していないか
- 既存DTC / freeze frame / extended dataとの差分を断定しすぎていないか
- Kill条件が具体的か
- 造語やphase名だけで、読者に判断を押し付けていないか
- 自然言語で読んでも、結論と次アクションが分かるか

## Commit Guidance

Repo更新時は、READMEの現在地と推奨読書順が古い仮説を最新結論のように見せていないか確認する。

## Project Skills

- `future-need-interviewing`: 顧客の最初のニーズ、最悪の未来、最高の未来、欲しい感情から本当のニーズを掘る。
- `chain-of-verification`: 叩き台の結論を検証質問に分解し、エビデンスで潰してから修正版を出す。
- `human-readable-reporting`: 人間向けレポートで、造語・商品名・phase名より先に自然言語で結論、業務文脈、判定条件を説明する。
- `timeboxed-goal-deep-dive`: 時間指定Goalを初回ドラフトで終わらせず、item別結論、弱点深掘り、早期停止理由まで明示する。
