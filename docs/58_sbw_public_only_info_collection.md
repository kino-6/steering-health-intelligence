# SbW公開情報収集

## 結論

公開情報を追加で集めた結果、Steer-by-wireについて言えることはかなり絞られる。

市場変化はある。
Bosch、ZF、Nexteer、Schaeffler、HELLA、JTEKTなどの公開情報から、SbWは研究テーマではなく、量産化・量産準備・商用化に向かう技術として扱われている。
構成要素も、steering wheel / hand wheel actuator、road wheel / steering rack actuator、sensor、software、redundant power/data、feedback actuatorとしてかなり共通している。

一方で、事業として売る余地は弱く見える。
NHTSAのfunctional safety assessment、VCAのR79 Annex 6説明、EUR-LexのR79本文を見ると、SbWの文書、fault strategy、verification、FMEA/FTA、safe state、driver warning、DTC coverageは既に安全・認証・診断の既存論点である。
つまり、公開情報だけで「SbW安全分析を売る」「SbW証拠パックを売る」と言うと、既存業務の焼き直しに見える。

現時点のEPSサプライヤ視点の結論:

> 公開情報だけで外販Proceedする材料はまだない。次に見るなら、`road wheel actuator redundancy degraded` の1ケースsampleを、公開サプライヤ資料、NHTSA/VCA/R79、ASAM SOVDに接続し、「安全分析の言い換え」ではなく「診断・説明・禁止主張の整理」として独自価値が出るかを見る。出なければSbW方向もStopする。

## 何を集めたか

今回集めたのは、内部資料ではない。
すべて公開情報である。

見た情報は4種類である。

1. サプライヤ公開情報: SbW構成、冗長性、量産化、商用化
2. OEM / vehicle公開情報: driver-visible behavior、警告、低速退避、車両側連携
3. 規制・安全公開情報: R79 Annex 6、fault strategy、verification、FMEA/FTA、safe state
4. 診断公開情報: NHTSAのDTC coverage候補、ASAM SOVDの診断API範囲

## 市場需要として見えること

公開情報から見える市場需要は、次の範囲に留まる。

| 需要の見え方 | 根拠 | ただし |
|---|---|---|
| SbWが量産技術になりつつある | Boschは商用規模の市場投入を目指すと発表。ZFはMercedes-Benz向け供給やvolume ordersを説明。NexteerはSbWをEPSの進化として扱う | 市場規模や有償支援需要までは分からない |
| 部品境界が増える | Bosch/ZF/Nexteer/SchaefflerはHWA/RWA/SWA/Rack actuator/software/feedbackを説明 | 対象EPSサプライヤの実構成は分からない |
| 冗長性と高可用性が訴求点になる | Boschはredundant data/power、Nexteerはdual hardware / multi-path software、HELLAはredundant sensor architecture、JTEKTはparallel redundant systemを説明 | 冗長性は既に既存安全設計の範囲 |
| driver-visible degraded behaviorがある | Tesla manualはalert、chime、drive torque reduction、pull over、low-speed emergency operationを説明 | Tesla固有であり、他OEMやサプライヤ需要とは限らない |

## 既存業務との重複として見えること

公開情報から強く見えるのは、SbWが既存の安全・認証・診断業務とかなり重なることだ。

| 既存業務 | 公開情報で見えること | 意味 |
|---|---|---|
| Functional safety | NHTSA reportはISO 26262 concept phase、functional FMEA、STPA、safety requirements、safe statesを扱う | 汎用安全分析としては売りにくい |
| Regulation / approval | VCAはR79 Annex 6でdocumentation、fault strategy、verification、FMEA/FTA等が必要と説明 | 認証資料パッケージ代替としては売りにくい |
| Driver warning / safe state | NHTSA reportはfailure detection時のdriver warningやsafe stateを扱う | 異常時状態マップは既存論点 |
| DTC coverage | NHTSA reportはSbW-relevant DTCや追加DTC coverage areaを扱う | 診断coverageも既存論点 |
| SOVD / next diagnostics | ASAM SOVDはfault information、data access、software update、logging/tracing等を扱う | 診断API/基盤は既存標準領域 |

## 公開情報だけで残る可能性

残る可能性はかなり狭い。

公開情報だけでできること:

- SbWの典型architectureを整理する
- 異常時状態、driver warning、診断表示、safe stateを公開情報から対応づける
- NHTSA/VCA/R79/ASAM SOVDに対して、どこが既存論点かを示す
- EPSサプライヤが言ってよいこと、言ってはいけないことを整理する

公開情報だけではできないこと:

- 対象EPSのDTC不足を言う
- 対象EPSのFMEA不足を言う
- 対象OEMが困っていると言う
- 顧客回答templateが不足していると言う
- safety caseやR79対応の代替を言う

## Public-only One-case Check

次に進めるなら、次の1ケースだけでよい。

> road wheel actuator redundancy degraded

公開情報だけで、以下を1ページにできるかを見る。

| Field | Public-only evidence candidate |
|---|---|
| Architecture | Bosch/ZF/Nexteer/SchaefflerのHWA/RWA/SWA/Rack actuator説明 |
| Redundancy | Bosch redundant power/data、Nexteer dual hardware / multi-path software、HELLA redundant sensor、JTEKT parallel redundant system |
| Driver-visible behavior | Tesla alert / chime / torque reduction / pull over / low-speed emergency operation |
| Safety baseline | NHTSA safe state / driver warning / FSR / FMEA / DTC coverage |
| Regulation baseline | VCA / R79 Annex 6 documentation, fault strategy, verification |
| Diagnostics baseline | NHTSA DTC coverage、ASAM SOVD fault information / data access |
| Supplier boundary | Public supplier architecture only。対象サプライヤ固有の不足は主張しない |
| Do-not-claim | root cause、保証費削減、対象EPS不足、vehicle-level approval代替 |

この1ページが、単に「NHTSA/VCA/R79に書いてあることの要約」になるならStop。
逆に、公開情報だけで「SbWでは安全・診断・SOVD・driver warningを横断して説明しないと、サプライヤの公開説明が薄く見える」という独自判断が出せるなら、もう1段だけ探索を続ける。

## Source Inventory

| Source | 何が取れるか | 判断への効き方 |
|---|---|---|
| Bosch SbW product page | SWA、steering rack actuator、software functions、mechanical link elimination、redundant data/power | architectureと冗長性の公開根拠 |
| Bosch / Arnold NextG press release | commercial-scale market entry, redundancy and approvals | 市場投入・認証文脈の公開根拠 |
| ZF by-wire release | mechanical connectionを不要にするby-wire chassis、industrialization、2030年市場share expectation | 量産化・市場変化 |
| ZF / Mercedes-Benz release | Mercedes-Benzへの2026年供給 | supplier / OEM interfaceの公開根拠 |
| Nexteer SbW | HWA/RWA/software integration、dual hardware、multi-path software、prognostics、steer-by-brake | supplierがどこまで公開訴求しているか |
| Schaeffler RWA | dedicated SbW architecture、RWA、driver feedback、software vehicle dynamics | road wheel actuator側の公開根拠 |
| Schaeffler Space Drive | steering column elimination、sensor、feedback motor | by-wire experience / motorsport-origin evidence |
| HELLA steering sensor | torque/angle as electrical signal、redundant sensor architecture | sensor redundancy |
| JTEKT engineering journal | parallel redundant system with CAN, power cables, motors, ECUs | redundancy architecture example |
| Tesla Cybertruck manual | alert、chime、pull over、torque reduction、low-speed emergency operation | driver-visible degraded behavior |
| NHTSA / Volpe SbW report | FMEA、safe states、functional safety requirements、DTC coverage | 既存安全・診断論点の強い根拠 |
| VCA R79 article | documentation、fault strategy、verification、FMEA/FTA、audit | 認証文書が既存業務である根拠 |
| EUR-Lex R79 | Annex 6 documentation / fault strategy / verification | regulation baseline |
| ASAM SOVD | fault information、data access、software update、logging/tracing | 診断API側の既存標準 |

TSVとしては、次の2つに分けて残した。

- [data/sbw_public_only_source_inventory.tsv](../data/sbw_public_only_source_inventory.tsv): 各ソースが支持すること、支持しないこと、EPSサプライヤとしての使い方。
- [data/sbw_public_only_value_check.tsv](../data/sbw_public_only_value_check.tsv): 公開情報だけで市場需要、未解決pain、既存業務との差分、初期提供物、Kill条件をどこまで言えるか。

## CoVe

| 検証質問 | 回答 | Confidence | 修正 |
|---|---|---|---|
| SbWが量産化へ向かうことは公開情報で言えるか | Bosch、ZF、Nexteer、Mercedes-Benzの公開情報から言える | High | 市場変化は維持 |
| EPSサプライヤが主語になれるか | Bosch/ZF/Nexteer/Schaeffler/HELLA/JTEKTがcomponentやsystemを公開説明している | Medium | supplier boundaryは公開architecture一般論までに限定 |
| 安全分析は新規価値か | NHTSA/VCA/R79で既存論点として扱われている | High | 汎用安全分析商品はKill寄り |
| 診断コンテンツは残るか | NHTSA DTC coverageとASAM SOVDで論点はあるが対象DTCは不明 | Medium | 診断価値は公開標準との整理まで |
| 買い手の痛みは公開情報で言えるか | 実RFQやOEM質問は見えない | Low | 買い手痛みは断定しない |

## EPSサプライヤとしての暫定結論

EPSサプライヤとして言えること:

> SbWでは、HWA/RWA、sensor、feedback、冗長電源/通信、driver warning、safe state、DTC coverage、SOVD fault informationが公開情報上の共通論点になっている。これらを横断して、言えることと言ってはいけないことを整理する公開情報ベースの1ケースsampleは作れる。

まだ言ってはいけないこと:

- 対象EPSの診断不足
- 対象OEMの未解決pain
- safety case代替
- R79 / ISO 26262 / CSMS対応代替
- field failure prediction
- warranty reduction

次にやるなら:

> `road wheel actuator redundancy degraded` を、公開情報だけで1ページにする。NHTSA/VCA/R79の要約で終わるならStop。診断・SOVD・driver warning・supplier boundaryを横断した独自の公開情報整理になるなら、もう1段だけ探索する。

## 参照ソース

- Bosch, Steer-by-wire: https://www.bosch-mobility.com/en/solutions/steering/steer-by-wire/
- Bosch Media Service, Bosch and Arnold NextG alliance: https://us.bosch-press.com/pressportal/us/en/press-release-21184.html
- ZF, By-Wire Future of Mobility: https://press.zf.com/press/en/releases/release_40533.html
- ZF, Mercedes-Benz steer-by-wire supply: https://press.zf.com/press/pt/releases/release_90433.html
- Nexteer, Steer-by-Wire: https://www.nexteer.com/a-d-a-s-automated-driving/steer-by-wire/
- Schaeffler, Road Wheel Actuator: https://www.schaeffler.de/en/products-and-solutions/powertrain-chassis/road-wheel-actuator/
- Schaeffler, Drive-by-wire technology: https://www.schaeffler.com/en/technology-innovation/motorsport/why-we-race/steer-by-wire-technology/
- HELLA, Steering technology of the future: https://www.hella.com/hella-com/en/press/Technology-Products-24-05-2023-21065.html
- JTEKT Engineering Journal, redundant system: https://www.jtekt.co.jp/e/engineering-journal/assets/1009/1009e_07.pdf
- Tesla Cybertruck Owner's Manual, steering alerts: https://www.tesla.com/ownersmanual/cybertruck/en_us/GUID-9A3F0F72-71F4-433D-B68B-0A472A9359DF.html
- NHTSA, Functional Safety Assessment of a Generic Steer-by-Wire Steering System: https://www.nhtsa.gov/sites/nhtsa.gov/files/documents/13502_812576_steerbywire.pdf
- UK VCA, Assessing the compliance of Steer-by-Wire systems: https://www.vehicle-certification-agency.gov.uk/blog/assessing-the-compliance-of-steer-by-wire-systems-for-individual-vehicle-approval/
- EUR-Lex, UN/ECE Regulation No 79: https://eur-lex.europa.eu/eli/reg/2008/79%282%29/oj/eng
- ASAM SOVD: https://www.asam.net/standards/detail/sovd/
