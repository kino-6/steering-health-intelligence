# Steer-by-wire方向のKill-first検証

## 結論

Steer-by-wire方向は、**次に掘る価値はあるが、まだ商品化には進めない**。

理由は2つある。

1つ目は、市場変化が公開情報で確認できること。
ZFはMercedes-Benz向けに2026年からsteer-by-wireを供給すると発表し、Nexteerもsteer-by-wireを量産技術として訴求し、HELLAもsteer-by-wire向け冗長センサを量産文脈で発表している。

2つ目は、従来EPSとの差分が大きいこと。
従来EPSではassistが落ちても機械的操舵が残る前提があった。
steer-by-wireでは、操舵指令、road wheel actuator、feedback、電源、通信、センサ、ソフトウェア、異常時状態を、電子制御と冗長設計で説明する必要がある。

ただし、ここも既存ISO 26262、SOTIF、cybersecurity、安全設計、safety caseと強く被る。
したがって、売り物を作る前に、**既存安全成果物との差分があるか**を確認する。

## 何を判断しているか

判断しているのは、steer-by-wireについて、EPS / steeringサプライヤが部品境界で説明できる新しい価値が残るかである。

悪い方向:

> Steer-by-wire safety evidence packを売る。

良い方向:

> 既存ISO 26262 / SOTIF / cyber / safety caseがある前提で、steer-by-wire特有の冗長系、fail-operational、driver feedback、software update後状態、cyber abnormal conditionを、OEM設計レビューやRFQ回答に使える部品境界の説明へ落とせるか確認する。

## 市場需要

公開情報では、steer-by-wireは量産に近づいている。

| Source | 公開情報から見えること | このRepoへの示唆 |
|---|---|---|
| ZF | 2026年からMercedes-Benzにsteer-by-wire技術を供給。冗長設計や速度/状況に応じた可変ステアリング比を訴求 | 量産移行が進む。steering supplierの説明責任が増える |
| Nexteer | Steer-by-wireでdual hardware、multi-path software、高可用性、冗長性を訴求 | 冗長構成と可用性説明はsupplier主語で語れる |
| HELLA | Steer-by-wire向けセンサで冗長かつ高信頼なsensor architectureを訴求 | sensor redundancyはsteering component側の強い論点 |
| SAE papers / public technical papers | fail-operational、controllability、comfortability、ISO 26262に沿ったfunctional safety conceptが扱われている | 既存安全設計と被るリスクが高い |

## 残る価値候補

残る可能性があるのは、汎用安全設計ではなく、steering system固有の説明である。

| 論点 | 既存安全成果物だけだと弱いかもしれない点 | steeringサプライヤが説明できる可能性 |
|---|---|---|
| Steering command path | steering wheel inputからroad wheel actuatorまでの電気的経路 | sensor、ECU、actuator、communication、fallbackのcomponent boundary |
| Redundancy | dual sensor / dual ECU / dual power / dual communicationのどれが何を吸収するか | 冗長構成とdegraded/fail-operational stateの説明 |
| Driver feedback | mechanical linkがない時のroad feel / feedback actuator | feedback loss時のdriver-visible behaviorとsafe state |
| Software update | update後のsteering stateやcalibration identity | update後のbasic steering state check |
| Cyber abnormal condition | spoofed command、sensor manipulation、diagnostic abuse | assist/fail-operational/fail-safe stateへの遷移説明 |
| OEM boundary | vehicle-level設計とcomponent-level設計の責任分界 | supplierが説明できる境界、OEMへ渡す前提 |

## Kill-first確認

次に見るべきは、商品名ではなく、以下の存在確認である。

| ID | 確認すること | Kill条件 |
|---|---|---|
| SBW-KQ1 | 対象顧客またはサプライヤ内にsteer-by-wire開発テーマがあるか | Noなら短期Kill |
| SBW-KQ2 | 既存ISO 26262 / safety caseにredundancy、degraded state、fail-operational stateが既に整理されているか | Yesなら汎用safety支援はKill |
| SBW-KQ3 | cyber abnormal conditionとsteering stateが紐づいているか | Yesならcyber-safety mappingはKill |
| SBW-KQ4 | software update後のsteering state / calibration identity確認が既にあるか | Yesならupdate evidence支援はKill |
| SBW-KQ5 | OEM設計レビュー/RFQでcomponent boundaryの説明に困っているか | Noなら外販支援はKill |

判定:

- SBW-KQ1がNoなら短期Kill
- SBW-KQ2、KQ3、KQ4がすべてYesならKill
- SBW-KQ5がYesで、KQ2-KQ4のどれかがNoなら短期assessment候補として残す

## 現時点判断

現時点では **Hold / explore next**。

Cyber/SBOM方向よりは、EPS / steeringサプライヤの主語に戻しやすい。
ただし、既存安全設計に飲まれるリスクが強い。

次に作るなら、1ページのデモはこれでよい。

> 従来EPSとsteer-by-wireで、supplierが説明すべき冗長系、fault handling、software update後状態、cyber abnormal condition、driver feedbackがどう変わるか。

これが汎用ISO 26262資料にしか見えなければKillする。

## 参照ソース

- ZF, Steer-by-Wire: Driving Innovation in a New Direction: https://press.zf.com/press/en/releases/release_89553.html
- Nexteer, Steer-by-Wire: https://www.nexteer.com/electric-power-steering/steer-by-wire/
- HELLA, Steering technology of the future: https://www.hella.com/hella-com/en/press/Technology-Products-24-05-2023-21065.html
- SAE, A Fail-Operational Assessment for Controllability and Comfortability of Steer-by-Wire Systems: https://saemobilus.sae.org/papers/a-fail-operational-assessment-controllability-comfortability-steer-wire-systems-2021-01-0930
- SAE, Functional Safety Concept Design of Vehicle Steer-by-Wire System: https://saemobilus.sae.org/downloads/papers/2024-01-2792/Full%20Text%20PDF
