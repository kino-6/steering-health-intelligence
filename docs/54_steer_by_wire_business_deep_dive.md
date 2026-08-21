# Steer-by-wire方向の事業成立性深掘り

## 結論

Steer-by-wire方向は、**探索を続ける価値はあるが、売り物はかなり狭く置くべき**である。

市場側では、機械的な操舵リンクをなくす量産車が増え始めている。ZFはMercedes-Benz向けの2026年供給を発表し、Mercedes-Benz自身も新しいEQSでsteer-by-wireを使うと説明している。Tesla CybertruckやLexus / ToyotaのOne Motion Gripも、運転者の入力を電子的に伝える例として公開されている。

ただし、これをそのまま「安全証拠パック」として売るのは弱い。なぜなら、冗長設計、故障時状態、ASIL、FMEA、safety case、cybersecurity caseは、既存のISO 26262 / SOTIF / CSMS業務で既に扱われる可能性が高いからである。

残すなら、狙いはこれだけにする。

> EPS / steeringサプライヤが、サプライヤが持つsteer-by-wire部品、ECU、センサ、アクチュエータ、診断、software/calibration ID、security accessについて、「異常時に何が起き、何を検知し、何を診断で見せ、OEMへ何を説明できるか」を部品境界で整理する。

これは安全設計の代替ではない。
既存の安全・サイバー・診断成果物を、OEM設計レビュー、RFQ回答、診断コンテンツ設計に転記しやすくするための狭い整理である。

現時点判断は **Hold / narrow proceed**。

公開情報だけで商品価値は証明できない。
ただし、1ページsampleを作って「既存安全資料の焼き直しか、OEM説明に使える新しい境界整理か」を判定する価値はある。

## 何を判断しているか

判断しているのは、steer-by-wireが普及することで、EPSサプライヤ側に新しい説明業務が増えるかである。

悪い判断:

> Steer-by-wireは安全が重要なので、安全Evidence Packを売る。

この言い方だと、既存のfunctional safety、FMEA、safety case、cybersecurity caseとほぼ重なる。

良い判断:

> Steer-by-wireでは、機械的な操舵リンクがない、または薄くなる。だから、サプライヤは「電子制御・冗長系・診断・ソフト更新・異常時状態をどう説明するか」を、既存成果物からOEM回答や診断設計へ翻訳する必要があるかを見る。

## 市場需要

市場需要は、少なくとも「技術が量産に近づいている」という形では確認できる。

| 市場シグナル | 何が見えるか | EPSサプライヤへの意味 |
|---|---|---|
| ZF / Mercedes-Benz | ZFは2026年からMercedes-Benzにsteer-by-wireを供給し、機械リンクをソフトウェア接続に置き換えると説明している | steering supplierが量産開発・OEM説明の主語になる |
| Mercedes-Benz EQS | Mercedes-Benzは新しいEQSでsteer-by-wireを使い、操舵感、取り回し、エアバッグ構造まで説明している | SbWはECUだけでなく、運転者UI・passive safety・車両設計へ波及する |
| Tesla Cybertruck | Teslaのmanualは、機械的接続がなく、冗長センサ/アクチュエータ、警告、torque reduction、pull over、low-speed overrideを説明している | driver-visible behaviorとdegraded operationの説明が製品文脈に出ている |
| Lexus / Toyota One Motion Grip | steering wheelとrackの機械リンクなし、電子伝達、可変steering ratioを訴求している | 複数OEMが同じ方向を試している |
| NHTSA functional safety assessment | NHTSA reportはSbWのpower supply、steering wheel sensor、control module、actuator、communication、driver feedback、mechanical backupなどをFMEA対象にしている | 故障モードの論点は既に公的に整理されている。差分は新規分析ではなく、サプライヤ固有の説明へ落とすこと |

## 未解決の痛み

痛みは「安全分析がない」ではない。
安全分析はむしろ既にあるはずである。

痛みが残るとすれば、次のような断片化である。

| 断片化するもの | 何が困るか |
|---|---|
| Safety成果物 | HARA、FMEA、ASIL、safety goalはあるが、OEMレビューで使える異常時の自然言語説明になっていない |
| Cyber成果物 | threatやsecurity controlはあるが、steering degraded stateやdiagnostic accessと結びついていない |
| Diagnostic成果物 | DTC、DID、freeze frame、extended dataはあるが、SbWの異常時状態や冗長低下をどう見せるかが見えにくい |
| Software update成果物 | software/calibration IDやupdate後確認はあるが、steering stateの安全確認とつながっていない |
| Customer interface | OEMからの公開RFQ/RFIや公開design review観点に対して、公開情報だけでどこまで答えられるかが見えにくい |

ここに価値がなければ、この方向は止める。

## 仮説

売れる可能性があるのは、汎用安全支援ではなく、次のような固定スコープの整理である。

> Steer-by-wireの部品境界について、既存の安全・サイバー・診断・ソフト更新成果物を読み、OEM説明や診断コンテンツ設計に使える「異常時状態と説明材料の対応表」にする。

この整理で見るもの:

- steering input path
- road wheel actuator path
- torque feedback / road feel path
- power supply / brownout / reset
- communication loss
- sensor disagreement
- actuator limitation
- software/calibration identity
- post-update basic steering state
- diagnostic access and security role
- degraded / fail-operational / fail-safe / low-speed override state

## 解決策

初期提供物は、以下の4点に絞る。

| 初期提供物 | 中身 | 使い道 |
|---|---|---|
| 異常時状態マップ | どの異常で、どの機能が残り、運転者に何が見え、診断に何が残るか | OEM設計レビュー、RFQ回答 |
| 既存成果物リンク表 | safety、cyber、diagnostic、software update成果物のどこから説明材料を取るか | 属人回答を減らす |
| 診断コンテンツ質問表 | DTC、DID、freeze frame、extended data、security accessで何を見せるか | SOVD / UDS整理への入力 |
| 禁止主張リスト | 何を断定してはいけないか | 過剰営業、責任境界超えを防ぐ |

この4点をまとめて、以後は狭い意味で `SbW component-boundary evidence map` と呼んでよい。
ただし、商品名ではなく、何を整理するかを示す作業名である。

## 買い手 / 利用者

最初の読者は、外部OEMではなく、EPS / steeringサプライヤ側で事業探索をする人である。

| 利用者 | 嬉しいこと |
|---|---|
| System engineering | SbWの異常時状態を車両側へ説明しやすくなる |
| Functional safety | 既存safety caseをOEM質問に転記しやすくなる |
| Cybersecurity | security abnormal conditionがsteering stateへどう効くかを説明しやすくなる |
| Diagnostic engineering | DTC / DID / freeze frame / security accessの公開範囲を決めやすくなる |
| Software / calibration | software ID、calibration ID、update後確認をsteering stateへ接続しやすくなる |
| Customer technical interface | RFQやdesign reviewで、どの資料から何を答えるかが揃う |

## EPSサプライヤとして持てる手札

EPSサプライヤが持てるのは、vehicle-level safety approvalではない。

持てる可能性があるもの:

- HWA / steering input sensor / torque feedback unitの仕様
- road wheel actuator / motor / inverter / ECUの仕様
- redundant sensor / power / communication pathの設計意図
- DTC / DID / freeze frame / extended data
- software / calibration ID
- diagnostic security access
- degraded / fail-operational / fail-safe stateのcomponent-level説明
- HILS / bench / vehicle evaluationで見た異常時挙動

持てないもの:

- OEMのvehicle-level safety case全体
- homologation判断
- driver HMI全体
- ADAS / automated driving全体
- fleet dataからの故障予測
- recall予測
- warranty cost削減の断定

## 既存業務との差分

ここが最重要である。

この方向の価値は、「新しい安全分析を作ること」ではない。
既存安全・サイバー・診断・ソフト更新成果物が分断されていて、OEM説明や診断コンテンツ設計へ転記しにくい場合にだけ価値がある。

| 既存業務 | 被るところ | 残る可能性 |
|---|---|---|
| ISO 26262 / safety case | hazard、safety goal、FMEA、ASIL、safety mechanism | OEM向け自然言語、component boundary、診断表示との対応 |
| SOTIF | 意図機能の安全、driver interaction | road feel / feedback / driver-visible behaviorの説明 |
| CSMS / TARA | threat、attack path、security control | cyber abnormal conditionがsteering degraded stateにどうつながるか |
| Diagnostic design | DTC、DID、freeze frame、UDS service | SbW状態を次世代診断で何を見せ、何を見せないか |
| Software update process | version、calibration、rollback、post-update check | update後のbasic steering state確認とOEM回答 |

この差分が出なければKillでよい。

## 最小デモ

次に作るべきデモは、大きな市場レポートではない。
1ケースでよい。

ケース:

> road wheel actuator側の冗長低下を検知したが、操舵はまだ可能で、車両はtorqueを制限しながらpull overを促す。

このケースに対して、以下を1ページで埋める。

| Field | 例 |
|---|---|
| abnormal condition | road wheel actuator redundancy degraded |
| driver-visible behavior | warning、chime、pull over request、torque reduction |
| remaining steering capability | normal / degraded / low-speed only / unavailable |
| supplier-owned evidence | actuator status、sensor agreement、power state、communication state、software/calibration ID |
| diagnostic content | DTC、DID、freeze frame、extended data、security access |
| safety/cyber source | safety mechanism ID、FMEA row、TARA row |
| OEM answer | 何が起き、何が残り、何を診断で読めるか |
| do-not-claim | root cause断定、field failure prediction、vehicle-level approval |

公開情報だけでこのsampleに独自価値が出せないなら、この方向はKillする。
現行方針では、既存safety caseや内部資料を要求して差分を確認しに行かない。

## Chain-of-Verification

| 検証質問 | Evidence | Confidence | 判断への影響 |
|---|---|---|---|
| SbWは量産に近づいているか | ZF / Mercedes-Benz / Tesla / Lexus-Toyotaの公開情報で、機械リンクなしまたはSbW採用が説明されている | High | 市場変化はある |
| SbWは従来EPSと違う説明責任を生むか | ZFとTeslaは機械接続なし、冗長系、異常時alert / torque reduction / pull overを説明している | High | driver-visible behaviorとdegraded stateが論点になる |
| 既存安全業務と被るか | NHTSA reportはSbWのpower supply、sensor、control module、actuator、communication、driver feedback等をFMEA対象にしている | High | 新規安全分析としては弱い |
| EPSサプライヤが主語になれるか | ZF、Nexteer、HELLAはsteering system、redundancy、sensor architectureをsupplier主語で説明している | Medium | component-levelなら可能 |
| 公開情報だけで売れる証明になるか | 対象supplierの既存safety/cyber/diagnostic成果物との差分は公開情報では見えない | High | 商品化はHold |
| SOVDと接続できるか | SbWの異常時状態をDTC / DID / freeze frame / access policyへ落とす必要がある場合のみ接続する | Medium | SOVDはextensionとして残す |

## 判定ルール

Proceed:

- 対象顧客またはサプライヤ内にSbW開発テーマがある
- 既存safety / cyber / diagnostic成果物はあるが、OEM設計レビューやRFQ回答へ横断的に転記しにくい
- degraded / fail-operational / fail-safe stateとdiagnostic contentの対応が未整理
- 公開情報だけで、diagnostic、safety、cyber、software update、customer interfaceの複数観点を1つの説明に接続できる

Hold:

- SbWテーマはあるが、既存成果物との差分が未確認
- 公開情報だけでsampleは作れるが、実program artifactがない
- 買い手候補は推定できるが、公開情報だけでは予算経路が見えない

Kill:

- 対象顧客またはサプライヤ内にSbW開発テーマがない
- 既存safety caseがdegraded / fail-operational / fail-safe state、driver-visible behavior、diagnostic content、OEM回答まで既に整理している
- OEMがvehicle-levelで全て指定し、サプライヤ側に提案余地がない
- 診断設計、software update、security accessと接続しない
- 成果物が汎用ISO 26262説明資料に見える

## EPSサプライヤとしての言い方

言えること:

> Steer-by-wireでは、機械リンクがない前提で、冗長低下、通信異常、電源異常、sensor disagreement、software update後状態を、部品境界で説明する必要がある。既存の安全・サイバー・診断成果物を、OEM説明と診断コンテンツ設計に転記できる形へ整理できるかを確認する。

まだ言ってはいけないこと:

- SbW故障を予測できる
- 保証費を下げられる
- root causeを断定できる
- vehicle-level safety approvalを代替できる
- 既存ISO 26262 / SOTIF / cyber成果物より優れている
- 公開recall / ODI / TSBだけで対象EPSの不足を断定できる

## 次アクション

次は、公開情報ベースの1ページsampleを作る。

sampleの目的は、商材デモではなく、次の判定である。

> これは既存safety caseの焼き直しか。それとも、EPSサプライヤのOEM説明・診断設計・software update確認に使える横断整理か。

このsampleが弱ければ、SbW方向もKillしてよい。

## 参照ソース

- ZF, Steer-by-Wire: Driving Innovation in a New Direction: https://press.zf.com/press/en/releases/release_89553.html
- ZF, Steer-by-Wire Systems: https://www.zf.com/products/en/cars/products_79944.html
- Mercedes-Benz Group, Steer-by-wire becomes reality in the new EQS: https://group.mercedes-benz.com/innovations/product-innovation/technology/steer-by-wire.html
- Tesla Cybertruck Owner's Manual, Steer-by-Wire / Emergency Operation: https://www.tesla.com/ownersmanual/cybertruck/en_ae/GUID-46420EE2-F6B0-4E95-88D5-E50CB3061101.html
- Lexus UK Magazine, Steer by wire: How does it work?: https://mag.lexus.co.uk/steer-by-wire-how-does-it-work/
- NHTSA / Volpe, Functional Safety Assessment of a Generic Steer-by-Wire Steering System: https://rosap.ntl.bts.gov/view/dot/37208
- Nexteer, Steer-by-Wire: https://www.nexteer.com/a-d-a-s-automated-driving/steer-by-wire/
- HELLA, Steering technology of the future: https://www.hella.com/hella-com/en/press/Technology-Products-24-05-2023-21065.html
