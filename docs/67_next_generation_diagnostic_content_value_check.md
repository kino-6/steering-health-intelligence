# EPS診断コンテンツの次世代化は製品価値として残るか

## 結論

現時点では、これを有償サービスとして売りに行く段階ではない。
公開情報から分かるのは、車両診断がリモート、車内、近接整備の3つの場面へ広がり、従来ECUも次世代診断APIの対象に入るという市場変化までである。
しかし、EPSサプライヤがその変化に対して独自に予算を取れる未解決の痛みは、公開情報だけでは確認できない。

残すなら、SOVD基盤や変換ツールではない。
EPSサプライヤが持っているDTC、DID、freeze frame、extended data、software ID、calibration ID、routine、security accessを、どの診断利用者に見せ、何を隠し、どの権限で読ませ、製品仕様やRFQ回答にどう残すかを整理する短期の内部向け検討である。

この整理が、既存の診断仕様書、ODX authoring、security access表、OEM指定の診断要件にすでに入っているなら止める。
逆に、リモート診断や車内診断へ出す情報の粒度、権限、禁止操作、安全影響、software/calibrationとの接続が部署ごとに分かれており、OEM説明やRFQ回答へ毎回つなぎ直しているなら、狭く残す。

## 何を判断しているか

判断しているのは、EPSサプライヤが次世代診断の「基盤」を持てるかではない。
判断しているのは、EPSサプライヤがサプライヤECUの診断コンテンツを、製品仕様、診断仕様、RFQ回答、顧客技術説明へ転記できる形に整理する価値が残るかである。

言い換えると、次の問いである。

> EPSで検知した異常、周辺条件、識別情報、許可する操作、禁止する操作を、近接整備、リモート診断、車内アプリケーションにどこまで見せるか。その判断を、OEM診断基盤任せではなく、EPS製品側の責任境界として説明できるか。

ここで初めて、以後 `EPS診断コンテンツの次世代化` と呼ぶ。

## 市場需要

車両診断は、整備工場の外部テスターだけでなく、リモート診断、車内診断、ソフトウェア更新、ログ、故障情報、識別情報へ広がっている。
ASAM SOVDは、HPCだけでなくclassic ECUの診断コンテンツにも統一アクセスを与えるAPIとして説明されている。
ISO 17978-3:2026の公開要約も、classic ECUとHPCへの統一アクセス、fault entry、environment data、measurement、identification、routine、I/O control、configuration、software updateを範囲に含めている。

一方で、SoftingはSOVD診断は車両またはHPC経由で可能であり、部分的な導入や個別ECUには並行解が必要になると説明している。
VectorもSOVDのauthoring、車両実装、API検証、Explorer、PoC、trainingまでを提供領域として説明している。
したがって、市場変化はあるが、SOVD基盤、サーバ、API、toolchainをEPSサプライヤ独自の外販商品として持つのは弱い。

## 未解決の痛み

公開情報だけで確実に言える痛みは、OEMやツールベンダー側の「次世代診断へ移行する複雑さ」である。
EPSサプライヤ側の痛みとしては、次の可能性があるが、これはまだ仮説である。

- DTCやfreeze frameはあるが、リモート診断に出してよい情報と出してはいけない情報の境界が診断仕様だけでは説明しにくい
- software ID、calibration ID、variant、post-update checkが、異常時状態やDTC説明と分かれている
- routineやI/O controlに、安全上やサイバー上の禁止操作があるが、RFQ回答や顧客説明へ自然言語で転記しにくい
- 近接整備、リモート診断、車内アプリケーション、製造、開発で、同じDIDや状態情報の見せ方が変わる

ここが既存診断設計担当の通常業務で完結しているなら、この方向は止める。

## 仮説

EPSサプライヤは、次世代診断APIそのものではなく、EPS診断コンテンツの公開範囲、権限、説明文、禁止操作、安全影響、software/calibrationとの紐付けを整理することで、製品側の説明価値を出せるかもしれない。

ただし、これは大きな商品ではない。
売れる可能性があるとしても、特定programで既存診断仕様、security access、software update、顧客技術説明が分かれており、OEM向けに短くつなぎ直す必要がある場合だけである。

## 解決策

初期に作るものは、診断基盤ではなく、診断コンテンツの判断表である。

1. EPS診断コンテンツ一覧  
   DTC、DID、freeze frame、extended data、software/calibration ID、routine、I/O control、security accessを並べる。

2. 利用場面ごとの公開範囲  
   近接整備、リモート診断、車内診断、製造、開発で、読ませる、制限する、読ませないを分ける。

3. EPSサプライヤが言える説明文  
   その情報が何を示し、何を示さず、どの安全状態や異常時状態と関係するかを自然言語で書く。

4. 禁止主張リスト  
   root cause断定、保証費削減、個車故障予測、車両全体の安全承認、OEM保証DBなしのfield判断を禁止する。

5. RFQ/診断仕様への転記欄  
   EPS製品仕様、診断仕様、security access表、RFQ回答に残る文言だけを採用する。

対応するproxy demoとして、[data/next_generation_diagnostic_content_value_check.tsv](../data/next_generation_diagnostic_content_value_check.tsv) に25件の診断コンテンツ項目を置いた。
これは対象EPSの実DTCではなく、判断表の形を確認するための仮データである。

## 買い手 / 利用者

初期利用者は、EPSサプライヤ内のdiagnostic engineering、software / calibration、cybersecurity、systems engineering、customer technical interfaceである。
買い手として成立するなら、診断設計責任者またはprogram technical leadに近い。

ただし、公開情報だけでは、これに独立予算がつくとは言えない。
したがって、現時点では外販商品ではなく、サプライヤ内または特定案件の短期整理支援にとどめる。

## Why supplier can play

EPSサプライヤが持てる手札は、車両診断基盤そのものではない。
持てるのは、EPS ECU内で何を検知し、どの状態を保持し、どのDIDやroutineを提供し、どのsecurity accessで制限し、software/calibrationのどの識別情報と結びつけるかである。

この範囲なら、OEM領域ではなくEPS製品側の責任境界として説明できる可能性がある。
ただし、OEMが診断コンテンツ、アクセス権、SOVD resource、ODX/authoringルールを完全指定している場合、サプライヤ独自の価値はほぼ残らない。

## EPS supplier conclusion

EPSサプライヤとして売ること:

> 現時点では売らない。公開情報だけでは、買い手の未解決painと予算を確認できないためである。

EPSサプライヤとして実施できること:

> 特定programで、既存DTC、DID、freeze frame、extended data、software/calibration ID、routine、security accessを、近接整備、リモート診断、車内診断、製造、開発の利用場面ごとに、公開/制限/禁止へ整理する。

EPSサプライヤとして言ってはいけないこと:

> SOVD対応基盤を提供できる、保証費を削減できる、field failureを予測できる、root causeを診断情報だけで断定できる、車両全体の安全承認まで説明できる、とは言わない。

初期対象外:

> OEM診断プラットフォーム、fleet analytics、サービスツール運用、ODX/UDS変換ツール、SOVD server実装、OTA基盤は初期対象外に置く。

次に見せる部署:

> diagnostic engineeringを起点に、software / calibration、cybersecurity、systems engineering、customer technical interfaceへ見せる。最初から営業資料にしない。

## Demo

デモは、実車データや実DTCではなく、25件の仮診断コンテンツを使う。
見るのは精度ではなく、次の判断が自然言語でできるかである。

- その情報はEPSサプライヤが持っているか
- 近接整備、リモート診断、車内診断、製造、開発のどこへ見せるか
- 見せる場合、どの権限が必要か
- その情報から何を言ってよいか
- 何を推定してはいけないか
- EPS製品仕様、診断仕様、RFQ回答に残る文言になるか

この25件の仮表が既存DTC表の整形にしか見えないなら、この方向は止める。
逆に、公開範囲、権限、禁止操作、安全影響、software/calibration接続を部署横断で整理できるなら、1ケースだけ特定program向けに試す価値は残る。

## What not to claim

- EPSの故障予測ができる
- 個車の残寿命を出せる
- 保証費を削減できる
- root causeを診断APIだけで断定できる
- OEM保証DBやfleet dataなしに市場判断ができる
- SOVD基盤、SOVD server、ODX/UDS変換をEPSサプライヤ商品として提供する
- 既存DTC、freeze frame、extended dataの不足を公開情報だけで断定する

## Kill criteria

以下のどれかが確認できれば止める。

- OEMがSOVD resource、DID、DTC、access policy、diagnostic contentを完全指定している
- 既存ODX authoring、診断仕様、security access表に、公開範囲、権限、禁止操作、安全影響、software/calibration接続がすでに入っている
- 診断設計担当が「これは通常のDTC/DID表で足りる」と判断する
- EPS製品仕様、診断仕様、RFQ回答に残る文言が出ない
- SOVD基盤、ODX変換、UDS tooling、OEM診断プラットフォームの話に流れる
- リモート診断や車内診断へ出す情報の粒度について、EPSサプライヤ側で判断できる余地がない

## CoVe

| 検証質問 | 回答 | Confidence | 判断への反映 |
|---|---|---|---|
| 市場変化は公開情報で確認できるか | ASAM SOVDとISO 17978-3:2026の公開要約で、classic ECU、fault、environment data、measurement、identification、routine、software updateが範囲に入ることは確認できる | High | 市場変化はある |
| SOVD基盤をEPSサプライヤ商品にできるか | SoftingやVectorがSOVD実装、authoring、API検証、PoC、trainingを公開しており、既存ツール領域が強い | High | 基盤商品は追わない |
| EPSサプライヤ側に残る範囲は何か | DTC、DID、freeze frame、extended data、software/calibration ID、routine、security accessの意味づけと公開範囲はEPS製品側に近い | Medium | content mapだけ残す |
| 既存診断設計の言い換えではないか | 実programの診断仕様を見ないと分からない | Unknown | 外販Proceedしない |
| 買い手の未解決painは公開情報で見えるか | 見えない。公開情報からは標準・ツール需要までは見えるが、EPS診断コンテンツ整理の予算は確認できない | Low | 売らずに短期整理支援へ縮小 |

## 参照ソース

- ASAM SOVD: https://www.asam.net/standards/detail/sovd/
- ISO 17978-3:2026 public summary via SIS: https://www.sis.se/en/produkter/road-vehicles-engineering/road-vehicle-systems/car-informatics-on-board-computer-systems/iso-17978-32026/
- Softing, SOVD: https://automotive.softing.com/standards/programming-interfaces/sovd-service-oriented-vehicle-diagnostics.html
- Vector, SOVD / ISO 17978-3: https://www.vector.com/us/en/products/solutions/diagnostic-standards/sovd-service-oriented-vehicle-diagnostics/
