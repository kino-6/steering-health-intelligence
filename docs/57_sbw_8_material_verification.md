# SbW 8項目の公開情報ベース検証

## 結論

8項目を公開情報だけで検証した結果、**外販Proceedには進めない**。

ただし、何が分かり、何が分からないかはかなり明確になった。

公開情報で確認できたのは、次の4つである。

1. Steer-by-wireでは、HWA、road wheel / front axle actuator、sensor、feedback、power、communicationのような部品境界が論点になる。
2. 異常時に、警告、chime、drive torque reduction、pull over、low-speed overrideのようなdriver-visible behaviorが出る。
3. SbWの安全分析、FMEA、fault strategy、故障時試験、DTC coverage候補は、既にNHTSA/VCAの公的資料で扱われている。
4. したがって、汎用安全分析や認証資料作成として売るのは弱い。

公開情報で確認できなかったのは、次の4つである。

1. 対象EPS / steering supplierの実architecture
2. 対象製品のDTC、DID、freeze frame、extended data
3. software/calibration IDとpost-update steering stateの接続
4. OEM RFQ、design review質問、既存customer answer templateの有無

したがって、現時点の判断は **Public-only Hold / do not sell**。

重要な修正:

> 現行方針では内部資料を要求しない。したがって、この不足を非公開項目の確認で埋めに行かない。

次に進めるとすれば、公開情報だけで作った1ケースsampleが、EPSサプライヤの公開営業資料、RFQ一般論、診断標準動向に対して独自の判断を出せるかを見る。
それができないなら、SbW方向もStopする。

## 何を検証したか

検証したのは、SbW方向が「市場にはありそう」から「EPSサプライヤが具体的に提供できる価値」へ進めるかである。

悪い進め方:

> SbWは量産化している。だから安全Evidence Packを売れる。

良い進め方:

> SbWは量産化している。ただし安全分析や認証資料は既存業務と被る。公開情報で分かる範囲と、公開情報では分からない範囲を分け、内部資料を要求せずに、公開情報だけで価値が示せるかを見る。

## 8項目の検証結果

| ID | 検証項目 | 公開情報で分かること | 公開情報で分からないこと | 判定 |
|---|---|---|---|---|
| 1 | SbW target architecture | ZFはHWAとfront axle actuator、HELLAはsteering sensor、Lexusはsteering torque actuator / control actuatorを説明している | 対象サプライヤの実architecture、どこまでがsupplier-ownedか | Partial |
| 2 | degraded / fail-operational / fail-safe state list | Mercedes-Benzは冗長architectureと2つのsignal path、Teslaはalert / chime / torque reduction / pull over / low-speed overrideを説明している | 対象製品のstate名、遷移条件、診断status、driver-visible behavior | Partial |
| 3 | FMEA / safety mechanism table | NHTSA/VolpeはISO 26262 concept phase、HAZOP、functional FMEA、STPA、safety requirements、test scenario、DTC coverage候補を扱っている | 対象製品のFMEA row、safety mechanism ID、OEM回答にそのまま使えるか | Partial / overlap risk high |
| 4 | DTC / DID / freeze frame / extended data | NHTSA/VolpeはDTC coverage候補に触れている。Teslaはdriver alertを説明している | 実DTC、DID、freeze frame、extended data、reader可否、security role | Mostly unknown |
| 5 | software/calibration ID and post-update check | ZFはSbWがsoftware-definedであることを説明している | 対象製品のsoftware ID、calibration ID、post-update steering state check | Unknown |
| 6 | security access / diagnostic role policy | VCAはR79 Annex 6でdocumentation / fault strategy / verificationが必要と説明しているが、diagnostic role policyまでは見えない | service / factory / engineering / OEM cloudのaccess boundary | Unknown |
| 7 | OEM RFQ / design review question | VCAはsystem developer / vehicle manufacturerが文書や故障時証拠を出す必要を説明している | 実OEMがsupplierへどんなRFQ / design review質問を出しているか | Unknown |
| 8 | Existing customer answer template | 公開情報では確認できない | 既に横断回答templateがあるか | Unknown |

## Chain-of-Verification

| 検証質問 | Evidence | Confidence | 判断への影響 |
|---|---|---|---|
| SbW architectureは公開情報で確認できるか | ZFはHWA/FAA、Lexusはsteering torque actuator/control actuator、HELLAはsteering sensorを説明 | High for generic architecture | 対象architectureではないのでPartial |
| degraded stateは公開情報で確認できるか | Mercedes-Benzは冗長architecture、Teslaはalert/chime/torque reduction/pull-over/low-speed overrideを説明 | Medium | driver-visible behaviorの論点は確認。ただし対象state listではない |
| FMEAや安全mechanismは既存業務か | NHTSA/VolpeはISO 26262 concept phase、HAZOP、functional FMEA、STPAを扱う | High | 汎用安全分析サービスはKill寄り |
| DTC coverageは既存論点か | NHTSA/VolpeはDTC coverage候補に言及 | Medium | 診断コンテンツ設計は論点だが、対象DTCは公開情報では分からない |
| R79/認証文書は既存業務か | VCAはR79 Annex 6でdocumentation、fault strategy、verification、failure provisions、test、audit、FMEA/FTAを説明 | High | 認証資料パッケージ代替はKill |
| OEM質問や既存回答templateは公開情報で分かるか | 公開ソースでは実RFQやcustomer answer templateは見えない | High | 現行方針ではここを非公開確認で埋めない。外販Proceed不可 |

## 項目別の意味

### 1. SbW target architecture

公開情報では、SbWの一般的な構成は確認できる。
ZFはhand wheel actuatorとfront axle actuatorを説明し、Lexusはsteering torque actuatorとsteering control actuatorを説明している。
HELLAはsteering sensorがtorqueとangleを電気信号として送ると説明している。

ただし、これは対象サプライヤのarchitectureではない。
EPSサプライヤとして事業判断するには、対象製品でHWA、RWA/FAA、ECU、sensor、power、communicationのどこを持っているかが必要である。

判定: **Partial**。

### 2. degraded / fail-operational / fail-safe state list

公開情報では、異常時に何が起きるかの例はある。
Mercedes-Benzは冗長architectureと2つのsignal pathを説明している。
TeslaはSbW異常時にalert、chime、drive torque reduction、pull over、low-speed overrideが出ると説明している。

ただし、対象製品のstate listではない。
state名、遷移条件、診断status、driver-visible behaviorが対象製品でどうつながるかは公開情報だけでは判断できない。

判定: **Partial**。

### 3. FMEA / safety mechanism table

NHTSA/VolpeはSbWをISO 26262 concept phaseで扱い、HAZOP、functional FMEA、STPA、安全要求、test scenario、DTC coverage候補まで示している。
つまり、FMEAや安全mechanismは既に標準的な安全業務の中にある。

この項目は、Proceed材料というよりKill材料である。
既存FMEAから1ケースsampleがそのまま出るなら、今回の方向はKillでよい。

判定: **Partial / overlap risk high**。

### 4. DTC / DID / freeze frame / extended data

公開情報では、DTC coverageが論点であることまでは確認できる。
しかし、実際のDTC、DID、freeze frame、extended dataは公開情報では分からない。

ここが未整理かどうかは公開情報だけでは判断できない。
現行方針では内部診断設計を要求しないため、この項目を価値証明に使わない。

判定: **Mostly unknown**。

### 5. software/calibration ID and post-update check

ZFはSbWがsoftware-definedであり、steering feelやratioをソフトウェアで調整できると説明している。
しかし、対象製品でsoftware ID、calibration ID、post-update steering state checkがどう定義されているかは公開情報では分からない。

判定: **Unknown**。

### 6. security access / diagnostic role policy

VCAはR79 Annex 6でdocumentation、fault strategy、verificationが必要と説明している。
しかし、diagnostic security accessやrole policyまでは公開情報では見えない。

SOVDやUDSの一般論に寄せることはできるが、それだけでは価値にならない。
対象EPSでservice、factory、engineering、OEM cloudに何を見せるかは公開情報だけでは判断できない。

判定: **Unknown**。

### 7. OEM RFQ / design review question

VCAは車両メーカーまたはsystem developerが文書や故障時証拠を出す必要があると説明している。
したがって、設計レビューや認証向けに説明材料が必要になることは推測できる。

ただし、実OEMがEPSサプライヤにどの質問を投げているかは公開情報では分からない。
ここがないと、買い手の痛みはまだ仮説である。

判定: **Unknown**。

### 8. existing customer answer template

これは公開情報では検証できない。
現行方針では顧客回答templateの提示を求めないため、この項目を次アクションにしない。

判定: **Unknown**。

## 現時点の総合判断

| レベル | 判断 |
|---|---|
| 市場変化 | Exists |
| Supplier control | Partly can act |
| Existing-work overlap | High |
| Public-only verification | Insufficient |
| Business offer | Do not sell |
| Next check | Public-only one-case value check |

## EPSサプライヤとしての結論

EPSサプライヤとして言えること:

> SbWでは、部品境界、異常時状態、診断で見せる情報、ソフト更新後確認、顧客説明が従来EPSより複雑になる可能性がある。公開情報からもその論点は確認できる。ただし、安全分析や認証文書は既存業務と強く被るため、売れる可能性があるのは既存成果物をOEM説明・診断設計へ横断転記する整理だけである。

まだ言ってはいけないこと:

- SbW向け安全分析サービスとして売れる
- 対象EPSの既存資料に不足がある
- DTCやfreeze frameが不足している
- OEMがこの整理に予算をつける
- R79 / ISO 26262 / CSMS / safety caseを代替できる

次にやること:

> road wheel actuator redundancy degradedの1ケースsampleを、公開情報だけで見直す。EPSサプライヤの公開営業資料、RFQ一般論、診断標準動向に対して独自の判断を出せないなら、SbW方向もStopする。

## 参照ソース

- ZF, Steer-by-Wire: Driving Innovation in a New Direction: https://press.zf.com/press/en/releases/release_89553.html
- ZF, Steer-by-Wire Systems: https://www.zf.com/products/en/cars/products_79944.html
- Mercedes-Benz Group, Steer-by-wire becomes reality in the new EQS: https://group.mercedes-benz.com/technology/innovation/development/steer-by-wire.html
- Tesla Cybertruck Owner's Manual, Steering Wheel / Steer-by-Wire: https://www.tesla.com/ownersmanual/cybertruck/en_ae/GUID-46420EE2-F6B0-4E95-88D5-E50CB3061101.html
- Lexus UK Magazine, Steer by wire: How does it work?: https://mag.lexus.co.uk/steer-by-wire-how-does-it-work/
- HELLA, Steering technology of the future: https://www.hella.com/hella-com/en/press/Technology-Products-24-05-2023-21065.html
- NHTSA / Volpe, Functional Safety Assessment of a Generic Steer-by-Wire Steering System: https://rosap.ntl.bts.gov/view/dot/37208
- UK Vehicle Certification Agency, Assessing the compliance of Steer-by-Wire systems for Individual Vehicle Approval: https://www.vehicle-certification-agency.gov.uk/blog/assessing-the-compliance-of-steer-by-wire-systems-for-individual-vehicle-approval/
