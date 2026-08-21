# Steer-by-wire判断材料

## 結論

ここで集めた判断材料から言えることは、次の通りである。

Steer-by-wireは、公開情報上は量産に近づいており、従来EPSよりも説明しなければならない範囲が広い。
機械リンクがない、または機械リンクへの依存が薄くなるため、冗長構成、異常時の残存操舵能力、運転者への警告、診断で読める状態、ソフト更新後の確認を説明する必要がある。

ただし、これを「新しい安全分析サービス」として売るのは危険である。
NHTSAのSbW functional safety assessmentや英国VCAのR79説明を見ると、SbWの安全分析、故障戦略、文書パッケージ、FMEA/FTA、故障時試験、電子制御システムの監査は既に既存業務として扱われる領域である。

したがって、EPSサプライヤとして残せる可能性があるのは、既存の安全・サイバー・診断・ソフト更新成果物を、OEM説明、RFQ回答、診断コンテンツ設計へ転記しやすくする整理だけである。

現時点の判断は **Hold / evidence-gathering continue**。

公開情報だけでは埋まらない判断材料は、以下の8点である。

1. SbW対象architecture
2. degraded / fail-operational / fail-safe state list
3. actuator / feedback pathのFMEAまたはsafety mechanism table
4. DTC / DID / freeze frame / extended data
5. software/calibration IDとpost-update check
6. security access / diagnostic role policy
7. OEM RFQまたはdesign review question
8. 既存customer answer template

現行方針では、この8点を内部資料要求で埋めに行かない。
したがって、この8点が公開情報で埋まらない限り、外販Proceedには進めない。

## 判断材料の読み方

この資料は、SbWを売るための材料ではない。
むしろ、売ってはいけない範囲を切るための材料である。

見るべき問いは3つだけでよい。

1. 市場側で、SbWに固有の説明負荷は増えているか
2. その説明負荷は、既存安全・認証・診断業務で既に処理されているか
3. EPSサプライヤが部品境界で整理し直す余地が残るか

## 公開ソースから見えること

| Source | 公開情報から見える事実 | 判断への使い方 |
|---|---|---|
| ZF press release | ZFはMercedes-Benz向けに2026年からSbW技術を供給し、機械的な固定伝達をソフトウェア接続に置き換えると説明している | 市場変化はある。supplierがSbWの主語になっている |
| ZF product page | SbWはhand wheel actuatorとfront axle actuatorを持ち、driver inputまたはautomated driving / vehicle motion controlからの要求を電子的に伝える | EPSサプライヤが説明すべきcomponent boundaryがある |
| Mercedes-Benz EQS | 新EQSはSbW採用、冗長architecture、2つのsignal path、rear-axle steeringやESPによるlateral controlまで説明している | SbWはsteering単体で閉じず、車両側fallbackやpassive safetyまで波及する |
| Tesla Cybertruck manual | 機械接続なし、複数の冗長sensor/actuator、異常時alert、chime、drive torque reduction、pull over、low-speed maneuvering overrideが説明されている | driver-visible behaviorとdegraded operationが製品説明に出ている |
| Lexus One Motion Grip | steering wheelとrackの機械リンクなし、electronic transfer、可変ratio、fail-safe processor、emergency power supplyが説明されている | driver feel、feedback、power fallbackが論点になる |
| HELLA press release | SbW向けsteering sensorのseries production、torque/angleの電気信号送信、redundant sensor architectureを説明している | sensor redundancyはサプライヤ境界で説明しやすい |
| NHTSA / Volpe report | ISO 26262 concept phase、HAZOP、functional FMEA、STPAを使い、5 safety goals、81 safety requirements、test scenarios、DTC coverage候補を扱っている | 安全分析とDTC coverageは既に公的研究で扱われる。新規安全分析として売るのは弱い |
| UK VCA | SbWはR79 Annex 6の文書、fault strategy、verification、安全concept、故障時試験、FMEA/FTA等の証拠が必要と説明している | 文書パッケージ需要はあるが、認証・型式承認・車両メーカー/システム開発者領域と被る |

## 判断に効く材料

### 1. 市場変化はある

ZF、Mercedes-Benz、Tesla、Lexus、HELLAの公開情報から、SbWは単なる研究テーマではなく量産文脈に入っていると見てよい。

EPSサプライヤ視点では、これは「市場が広い」という意味ではなく、対象顧客やサプライヤ内programにSbWがある場合、説明業務が発生しうるという意味で使う。

### 2. 説明範囲は従来EPSより広い

従来EPSでは、assistが落ちても機械的操舵が残る前提で説明できることが多い。
SbWでは、steering input、road wheel actuator、feedback、power、communication、software、diagnostic、driver alertが連鎖する。

Tesla manualのように、異常時に警告、chime、drive torque reduction、pull over、low-speed overrideまで製品説明に出ると、サプライヤ側も「自分の部品がどこまで関与するか」を整理する必要がある。

### 3. 既存業務との重複は強い

NHTSA / Volpe reportは、SbWについてISO 26262 concept phase、HAZOP、functional FMEA、STPA、safety requirements、test scenarios、DTC coverage候補まで扱っている。
VCAも、R79 Annex 6ではsystem explanation、architecture / wiring diagram、failure provisions、failed-condition testing、安全concept audit、FMEA/FTAなどが必要と説明している。

つまり、「SbWの安全性を分析します」は既存業務の焼き直しになりやすい。

### 4. 残るなら横断整理だけ

残る可能性は、以下が分断されている場合だけである。

- safety caseはあるが、OEM回答文になっていない
- cyber / TARAはあるが、steering degraded stateとつながっていない
- DTC / DIDはあるが、SbWの異常時状態とつながっていない
- software/calibration IDはあるが、post-update steering stateとつながっていない
- 公開情報上、customer interfaceがどの材料を必要としているかまでは見えない

この場合にだけ、component-boundary evidence mapとして価値が残る。

## 公開情報だけでは埋まらない判断材料

| ID | 見るもの | 何が分かるか | 公開情報で埋まる場合 | 公開情報で埋まらない場合 |
|---|---|---|---|---|
| SBW-MAT01 | SbW target architecture | supplier-owned component boundary | 公開サプライヤ資料でHWA/RWA/ECU/sensor/power/communicationの境界が分かる | 対象サプライヤ固有の境界は判断しない |
| SBW-MAT02 | degraded / fail-operational / fail-safe state list | 異常時に何が残るか | 公開manualや公開技術資料でstate、driver-visible behavior、diagnostic statusがつながる | 対象製品のstate不足は主張しない |
| SBW-MAT03 | FMEA / safety mechanism table | 既存安全成果物との差分 | 公開安全分析でOEM説明との差分まで見える | 汎用安全分析サービスはKill寄り |
| SBW-MAT04 | DTC / DID / freeze frame / extended data | 診断で何を見せるか | 公開診断資料でSbW stateとの対応が見える | DTC/DID不足は主張しない |
| SBW-MAT05 | software/calibration ID and post-update check | 更新後確認とsteering stateの接続 | 公開software update資料でsteering state確認が見える | 価値証明に使わない |
| SBW-MAT06 | security access / diagnostic role policy | 誰に何を読ませるか | 公開標準・公開ツール資料でaccess policyが見える | SOVD/security価値を主張しない |
| SBW-MAT07 | OEM RFQ / design review question | 実際に誰が困っているか | 公開RFQ/RFI/設計要求で質問が見える | 買い手の痛みは仮説止まり |
| SBW-MAT08 | existing customer answer template | 既に同じ成果物があるか | 公開templateが存在する | 公開情報では検証不能として扱う |

## 判断基準

公開情報だけで探索継続してよい条件:

- 公開資料だけで、SbWの異常時状態、診断表示、software/update、security/accessのうち複数が同じ1ケースsampleに接続できる
- 公開資料だけで、既存安全分析やR79説明との差分が自然言語で説明できる
- 公開資料だけで、EPSサプライヤが言えることと言ってはいけないことを分けられる

Killしてよい条件:

- 公開情報だけでは、既存安全分析やR79説明との差分が出ない
- 公開情報だけでは、診断、software/update、security/accessのどれにも接続できない
- vehicle-level認証、HMI、ADAS fallbackに依存し、EPSサプライヤが主語にならない
- 成果物が「R79/ISO 26262対応資料を作る」に見える

## EPSサプライヤとしての暫定判断

EPSサプライヤとしては、まだ外販商品ではない。
現行方針では内部資料を見ないため、固定スコープassessmentとも言わない。

売ると言ってよい可能性があるもの:

> SbW異常時状態について、既存の安全・サイバー・診断・software update成果物を横断し、OEM説明や診断コンテンツ設計に転記できる形へ整理する。

言ってはいけないもの:

- SbW安全分析そのものを代替する
- R79 / ISO 26262 / CSMS認証を代替する
- vehicle-level safety approvalを取れる
- 故障予測や保証費削減ができる
- 公開情報だけで対象EPSの不足を断定できる

## 参照ソース

- ZF, Steer-by-Wire: Driving Innovation in a New Direction: https://press.zf.com/press/en/releases/release_89553.html
- ZF, Steer-by-Wire Systems: https://www.zf.com/products/en/cars/products_79944.html
- Mercedes-Benz Group, Steer-by-wire becomes reality in the new EQS: https://group.mercedes-benz.com/technology/innovation/development/steer-by-wire.html
- Tesla Cybertruck Owner's Manual, Steering Wheel / Steer-by-Wire: https://www.tesla.com/ownersmanual/cybertruck/en_ae/GUID-46420EE2-F6B0-4E95-88D5-E50CB3061101.html
- Lexus UK Magazine, Steer by wire: How does it work?: https://mag.lexus.co.uk/steer-by-wire-how-does-it-work/
- HELLA, Steering technology of the future: https://www.hella.com/hella-com/en/press/Technology-Products-24-05-2023-21065.html
- NHTSA / Volpe, Functional Safety Assessment of a Generic Steer-by-Wire Steering System: https://rosap.ntl.bts.gov/view/dot/37208
- UK Vehicle Certification Agency, Assessing the compliance of Steer-by-Wire systems for Individual Vehicle Approval: https://www.vehicle-certification-agency.gov.uk/blog/assessing-the-compliance-of-steer-by-wire-systems-for-individual-vehicle-approval/
