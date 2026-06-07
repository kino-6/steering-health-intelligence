# SOVD / 次世代診断コンテンツ設計のKill-first検証

## 結論

SOVD方向は、**主商品にはしない**。
ただし、EPS診断コンテンツを次世代診断基盤に載せるための整理として、狭く残る可能性はある。

SOVD基盤、SOVD server、SOVD stack、ODX/UDS変換、診断APIそのものは、既存標準・既存プレイヤーがかなり厚い。
ASAM、Softing、DSA、ETAS、Sibros、Technvil、Eclipse OpenSOVDなどの公開情報から、SOVDはすでに標準・実装・ツールの領域に入っている。

したがって、EPSサプライヤが狙うなら、基盤ではなく **EPS診断コンテンツの意味、公開範囲、権限、software/calibration ID、freeze frame / extended dataのexposure policy** までである。

## 何を判断しているか

判断しているのは、SOVDという診断APIの波に対して、EPSサプライヤが独自に売れるものがあるかである。

悪い方向:

> SOVD対応サービスを売る。

良い方向:

> OEM診断基盤やSOVD stackはOEM/ツールベンダー領域に置き、EPSサプライヤは自社ECUのUDS、DTC、DID、freeze frame、extended data、software/calibration ID、security accessを、次世代診断に載せる前の診断コンテンツとして整理できるかを見る。

## 市場需要

SOVDの市場方向性は公開情報で確認できる。

| Source | 公開情報から見えること | このRepoへの示唆 |
|---|---|---|
| ASAM SOVD | software-based vehicle向け診断API。HPCやclassic ECUのdiagnostic contentへuniform accessを提供 | classic ECUであるEPSも診断コンテンツ対象に含まれる |
| Softing | SDV向け診断標準、SOVD実装、ECUから車両までの実装文脈 | 既存ツールが強い |
| DSA | ECU-centric UDSからservice-oriented/API-based diagnosticsへの移行を支援 | 変換・実装支援は既存プレイヤー領域 |
| ETAS | SOVDはstateless access、diagnostic independence、mutual authentication、role-based access、legacy UDS統合を扱う | security/access設計も既存領域 |
| Sibros / Technvil / Eclipse OpenSOVD | SOVD solution、ODX/PDX変換、capability description、open-source implementation | stackや変換ツールは既に多い |

## 残る価値候補

残るとすれば、EPS診断コンテンツの意味づけである。

| 論点 | 既存SOVD/ODX toolingだけだと弱いかもしれない点 | EPSサプライヤが説明できる可能性 |
|---|---|---|
| DTC | DTCがdriver symptomやassist stateとどうつながるか | EPS lamp、assist limitation、failsafe stateとの対応 |
| DID | どのDIDを外部診断へ見せるか | software/calibration ID、variant、sensor status、assist state |
| freeze frame / extended data | SOVD resourceとして何を公開し、何を制限するか | speed、voltage、temperature、assist state、security-sensitive dataの境界 |
| routine control | どのroutineを許可/禁止するか | steering actuatorやcalibrationに関わる安全影響 |
| security access | role-based accessで何を読ませ、何を拒否するか | service、factory、engineering、OEM cloudの権限差 |

## Kill-first確認

| ID | 確認すること | Kill条件 |
|---|---|---|
| SOVD-KQ1 | 対象OEMまたはprogramにSOVD採用/検討があるか | Noなら短期Kill |
| SOVD-KQ2 | OEMが診断コンテンツを完全指定しているか | Yesならサプライヤ提案はKill |
| SOVD-KQ3 | 既存ODX/diagnostic authoringでDTC/DID/freeze frame exposure policyが既に整理されているか | YesならKill |
| SOVD-KQ4 | EPS診断情報の公開/制限/権限で悩みがあるか | NoならKill |
| SOVD-KQ5 | SOVD化が現行UDS改善やsecurity access整理に接続するか | Noなら短期Kill |

判定:

- SOVD-KQ1がNoなら短期Kill
- KQ2とKQ3がYesならKill
- KQ4またはKQ5がYesなら、content mapだけ残す

## 現時点判断

現時点では **Hold as extension**。

SOVD基盤や変換ツールとして追うのは弱い。
残すなら、steer-by-wireや次世代EPSで必要になる診断コンテンツのexposure policyに限定する。

## 参照ソース

- ASAM SOVD: https://www.asam.net/standards/detail/sovd/
- Softing, SOVD: https://automotive.softing.com/standards/programming-interfaces/sovd-service-oriented-vehicle-diagnostics.html
- DSA, SOVD: https://dsa.de/en/competences/sovd.html
- ETAS, Service-Oriented Vehicle Diagnostics: https://www.etas.com/ww/en/topics/service-oriented-vehicle-diagnostics/
- Sibros, SOVD: https://sibros.tech/products/oems/sovd
- Technvil, i-RED SOVD: https://technvil.com/products/i-red/ired-sovd
- Eclipse OpenSOVD: https://projects.eclipse.org/projects/automotive.opensovd
