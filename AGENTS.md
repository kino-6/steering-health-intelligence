# Repository Operating Rule

このRepoの事業仮説、調査、デモ、ドキュメント更新では、以下を最上位ルールにする。

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

## Current Main Hypothesis

`EPS Diagnostic / Robustness Coverage Benchmark` は、内部資料を使わない現行方針ではNo-Goで止める。
対象EPSの実HILS、DTC、freeze frame / extended data、既存レビューとの差分を確認できないためである。

現在の探索ブランチは以下。

> EPS / steering ECU public-regulation and software evidence branch

これは商品名ではない。
公開されている規制、標準、業界動向から、EPSサプライヤ側に実務負荷が増えている領域を探すための一時的な探索軸である。

有力候補:

- EPS / steering ECU software/cyber evidence pack
- SOVD / next-generation diagnostics content design for EPS
- Steer-by-wire safety / cybersecurity / redundancy evidence pack
- Public recall / ODI / TSB monitor as input only

これらは、故障予測、劣化兆候通知、追加ログではない。
EPSサプライヤが、診断、ソフト更新、セキュリティ、SBOM、steer-by-wire移行に対して、OEM説明・監査・設計レビューに使える材料を作れるかを見る。

現在の最優先候補は、`EPS / steering ECU software/cyber evidence pack` である。
サイバーセキュリティ設計証拠とSBOM / 脆弱性対応は分けず、診断アクセス、ソフト更新、software/calibration ID、SBOM、CVE impact triage、security access、fail-safe stateをcomponent-level evidenceとして束ねる。

初期offerは、SaaSではなく固定スコープassessmentとして扱う。
目的は、既存CSMS/TARA/SBOM/CVE運用の代替ではなく、steering ECU固有の診断アクセス、ソフト更新、SBOM-to-function impact、fail-safe state、OEM回答文への接続に差分があるかを確認すること。
既存業務に同等成果物があるならKillする。

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
