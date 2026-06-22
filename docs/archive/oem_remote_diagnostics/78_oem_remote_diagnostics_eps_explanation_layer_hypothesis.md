# OEM遠隔診断に組み込む操舵系状態説明レイヤー仮説

## 結論

次に作業するなら、EPS/SbWサプライヤ単独のfleet監視サービスではなく、OEMの遠隔診断やfleet serviceに組み込まれる操舵系の説明レイヤーとして検証する。

End userやfleet運用者が欲しいのは、EPSの交換時期そのものではない。
操舵系に警告や制限状態が出たときに、次の運行に出してよいのか、先に入庫すべきなのか、どの診断情報を追加で読むべきなのか、整備側やOEM service側にどう説明すべきなのかである。

EPS/SbWサプライヤが持つ付加価値は、車両全体を監視することではない。
EPS内部データ、診断仕様、制御状態、software / calibration情報、HILS / bench知見から、DTCだけでは分からない操舵系の状態説明を作れることである。

したがって新しい仮説はこう置く。

> OEMの遠隔診断networkに、EPS/SbWサプライヤが操舵系の説明ロジックを提供する。  
> 価値は、EPS内部データから、DTCだけでは分からない状態説明、追加で読むべきDID、運行・入庫・診断判断の入力、言ってよいことと言ってはいけないことを作ることにある。

これは安全制御のリアルタイム判断ではない。
OEM fleet service / remote diagnostics上で、近リアルタイムまたはイベント後に、整備・診断・入庫優先度判断を支援する説明である。

## 何を判断しているか

判断しているのは、EPS/SbWサプライヤがfleetを直接監視して外販SaaSを売るかではない。

判断しているのは、OEM remote diagnosticsやfleet serviceの既存networkに、EPS/SbWサプライヤが操舵系の説明コンテンツを組み込めるかである。

具体的には、次の判断である。

- OEM remote diagnosticsでEPS/SbW関連のDTCやDIDが上がったとき、サプライヤ固有の意味づけが必要か
- assist state、limit state、thermal state、motor current、voltage、communication state、software / calibration IDから、DTCだけでは分からない説明を作れるか
- その説明が、運行可否、入庫優先度、診断読み順、部品準備、顧客説明、field-to-engineering feedbackへ転記できるか
- 既存remote diagnosticsのseverity / action planと何が違うか
- EPS/SbWサプライヤが言ってよい範囲と、OEMやfleet serviceが判断すべき範囲を分けられるか

## なぜ旧テーマと違うか

旧テーマでは、EPS/SbWサプライヤが単独でfleet向けhealth monitoringや故障予測を売れるかを見た。
これはStopした。
理由は、必要データがOEM/fleet/platform側にあり、既存remote diagnosticsもDTC severity、action plan、API連携、診断時間短縮をすでに扱っているためである。

新仮説では、主語を変える。

| 旧テーマ | 新仮説 |
|---|---|
| EPS/SbWサプライヤがfleetを直接監視する | OEM remote diagnostics networkに説明ロジックを組み込む |
| 故障予測や交換時期を売る | DTCだけでは分からない操舵系状態説明を作る |
| fleet向け単独SaaS | OEM program内の診断・service content |
| サプライヤが運行可否を断定する | OEM / fleet serviceの判断材料を提供する |
| 公開情報だけで外販化する | 特定OEM programと内部data fieldを前提に検証する |

## Market Demand First

| Field | 内容 |
|---|---|
| Market demand | OEM fleet serviceやremote diagnosticsでは、DTCを受けた後に、severity、action plan、service routing、parts preparation、diagnostic time reductionへつなげる需要がある。 |
| Evidence signal | Bosch、International、Geotab、Volvo、OnStar、Smartcar、Platform Scienceはremote diagnostics、risk / criticality、action plan、API連携を扱う。NexteerとZFはmotion / chassis / vehicle healthやactual lifecycle dataを扱う。 |
| Hypothesis | EPS/SbWサプライヤは、OEM remote diagnostics networkに参加し、EPS内部データから操舵系状態説明を生成することで、既存remote diagnosticsに不足するcomponent-specific explanationを補える可能性がある。 |
| Solution | 外販fleet監視ではなく、OEM program向けに、DTC/DID意味づけ、状態説明、診断読み順、禁止主張、field-to-engineering feedbackをまとめた説明コンテンツを作る。 |
| Buyer / user | OEM fleet service、OEM remote diagnostics、service engineering、dealer diagnostic support、EPS/SbWサプライヤのdiagnostic engineering / field quality / product engineering。 |
| Initial artifact | 1ケースの説明レイヤーsample、必要data field list、OEM network参加条件、既存remote diagnosticsとの差分表、禁止主張リスト。 |
| Validation method | 実または仮のEPS/SbW DTCイベントを使い、既存remote diagnosticsのaction planだけでは足りない説明が作れるかを見る。 |
| Kill criteria | EPS内部data fieldがnetworkに上がらない、既存remote diagnosticsで十分、service outcomeが戻らない、説明が安全保証や原因断定になる、OEM serviceの成果物へ転記できない。 |

## 初期成果物

最初に作るべきものは、商品名ではない。
1ケースの説明sampleである。

例:

> 高負荷操舵後にassist limitationまたはthermal limitに入ったケース。

このケースについて、次の4列で比較する。

| 列 | 目的 |
|---|---|
| DTCだけで分かること | 既存診断の最低限の情報を確認する |
| 既存remote diagnosticsで分かること | severity、action plan、service routingなど既存playerが出せる範囲を確認する |
| EPS/SbW内部データで追加説明できること | assist state、thermal state、motor current、software / calibration ID、DID読み順から説明できる差分を見る |
| OEM serviceに出す説明 | 入庫優先度、追加診断、言ってよいこと、言ってはいけないことへ落とす |

このsampleで差分が出なければ、仮説は止める。

## 必要データ

この仮説に必要なデータは、公開情報ではなく、特定OEM programの中で確認する。

| Data | なぜ必要か | 所有/依存 |
|---|---|---|
| EPS/SbW DTC | 既存remote diagnosticsの起点 | OEM diagnostics / supplier diagnostics |
| DID / freeze frame / extended data | DTCだけでは分からない状態説明を作る | OEM診断仕様 / EPS supplier |
| assist state / limit state | 操舵支援や制限状態の説明 | EPS/SbW supplier |
| thermal state / motor current / voltage | 過負荷一過性か再発懸念かの切り分け | EPS/SbW supplier |
| software / calibration ID | version差分や既知制限の説明 | EPS/SbW supplier / OEM release |
| service action / replacement result | 説明の妥当性確認 | OEM service / dealer / fleet |
| recurrence / work time | feedback loopと改善 | OEM service / fleet |

## EPSサプライヤとしての言い方

EPS/SbWサプライヤとして売るか:

> 単独のfleet監視サービスとしては売らない。OEM remote diagnostics networkに組み込まれる説明コンテンツとして検証する。

EPS/SbWサプライヤとして実施できること:

> EPS内部データと診断仕様から、DTCだけでは分からない操舵系状態説明、追加DID読み順、service側に出す注意文、field-to-engineering feedbackを作る。

EPS/SbWサプライヤとして言ってはいけないこと:

> 走行安全を保証する、故障時期を予測する、交換時期を断定する、root causeを断定する、OEM remote diagnosticsを置き換える、fleet downtime削減を保証する、とは言わない。

OEM / fleet / platform領域:

> 運行可否の最終判断、driver / fleetへの通知、service network運営、保証判断、fleet dashboard、法規・安全責任はOEM / fleet / platform側に置く。

次に見せる部署:

> EPS/SbW supplier側では、diagnostic engineering、service engineering、field quality、software/calibration、product engineering、customer technical interfaceに見せる。Business developmentには、単独外販ではなくOEM program内contentとして見せる。

## 検証質問

| ID | Question | Proceed signal | Kill signal |
|---|---|---|---|
| RDQ001 | OEM remote diagnostics networkにEPS/SbW DTC / DID / 状態量が上がるか | DTCに加えてDID、freeze frame、assist/thermal/software IDの一部が扱える | DTCだけで、追加data fieldが上がらない |
| RDQ002 | 既存remote diagnosticsのaction planでは足りない操舵系説明があるか | EPS内部データで、追加診断、入庫優先度、注意文が変わる | 既存severity / action planと同じ |
| RDQ003 | service outcomeが戻るか | 整備結果、交換結果、再発有無、作業時間の一部が戻る | feedbackがなく説明改善できない |
| RDQ004 | 安全保証や原因断定に踏み込まず説明できるか | 言ってよいこと / 言ってはいけないことを分けられる | 走行可否保証やroot cause断定が必要になる |
| RDQ005 | OEM service成果物へ転記できるか | service bulletin、remote diagnostics note、dealer support、customer explanationへ入る | 説明が社内メモで終わる |

## Archiveとの関係

これまでのmotion health調査は、この新仮説の直接証明ではない。
ただし、以下の知見として使える。

- fleet downtimeやdiagnostic time reductionの需要はある
- 既存remote diagnosticsはseverity、action plan、API連携をすでに扱う
- EPS/SbWサプライヤ単独のfleet監視は弱い
- 価値が残るなら、EPS内部データに基づくcomponent-specific explanationである
- 再開にはOEM network参加、data field、service outcomeが必要である

詳細なArchive indexは [docs/archive/motion_health/79_motion_health_archive_index.md](docs/archive/motion_health/79_motion_health_archive_index.md) に置く。

## Sources

- Bosch Cloud and Predictive Diagnostics: https://www.bosch-mobility.com/en/solutions/software-and-services/cloud-and-predictive-diagnostics/
- International Advanced Remote Diagnostics: https://www.international.com/services/my-international/advanced-remote-diagnostics
- Geotab Remote Diagnostics: https://www.geotab.com/blog/remote-diagnostics/
- Volvo Trucks Remote Diagnostics: https://www.volvotrucks.us/our-difference/uptime-and-connectivity/remote-diagnostics/
- GM Fleet OnStar API Services: https://www.gmfleet.com/software/onstar/api-services
- Smartcar real-time vehicle diagnostics: https://smartcar.com/docs/getting-started/guides/real-time-vehicle-diagnostics
- Platform Science Remote Diagnostics: https://www.platformscience.com/blog/the-power-of-remote-diagnostics-for-fleet-maintenance
- Nexteer MotionIQ software suite: https://www.nexteer.com/release/nexteer-unveils-its-motioniq-software-suite-for-intelligent-motion-control/
- ZF Vehicle Health Monitoring: https://press.zf.com/press/en/releases/release_92162.html
