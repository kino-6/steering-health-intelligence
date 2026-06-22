# 操舵系の運行可否 / 点検優先度判断 MHQ001-MHQ005探索レポート

## 結論

現時点では、すぐに外販商品として売る段階ではない。
ただし、旧テーマのように閉じる段階でもない。

自動運転車両や商用車両群では、車両を止めないこと、予定外入庫を減らすこと、診断時間を短くすること、部品や整備士を先に準備することに明確な需要がある。
この需要は、乗用車EPS単体の寿命予測ではなく、車両群の運行・整備判断の問題である。

操舵系については、Nexteerがsteering、chassis components、tiresを含むhealth monitoringをfleet downtime、maintenance scheduling、diagnostic time reductionに結びつけており、最も直接的な公開signalである。
BoschやZFの公開情報からも、EPS / steer-by-wireは自動運転・高可用操舵で重要になることは確認できる。
一方で、「操舵系理由の予定外入庫がどれほど痛いか」「EPS / SbWサプライヤが運行データ、DTC、DID、整備履歴、交換結果へ触れるか」は、まだ公開情報だけでは確定できない。

したがって判断は、**新テーマとして探索継続。ただし商品化ではなく、買い手・データアクセス・既存診断との差分を確認する次スプリントへ進む** である。

## 市場需要から見た整理

| Field | 内容 |
|---|---|
| Market demand | 自動運転車両や商用車両群では、車両を止めないこと、予定外入庫を減らすこと、診断時間を短くすること、部品や整備士を先に準備することが業務上の痛みである。 |
| Evidence signal | Nexteerはsteering/chassis/tire healthをfleet downtime、maintenance scheduling、diagnostic time reductionに接続している。Bosch、Geotab、Verizon、Volvo、Internationalもfleet maintenance、remote diagnostics、repair priorityを業務価値として説明している。 |
| Hypothesis | EPS単体の寿命予測ではなく、EPS / SbWを含む操舵系状態を、運行可否、入庫優先度、診断優先度、部品準備へ翻訳できれば価値がある可能性がある。 |
| Solution | 最初は予測モデルではなく、20〜50件の公開sourceを使い、fleet maintenance pain、操舵系接点、既存remote diagnosticsとの差分、サプライヤ境界、Kill signalを分類する判断表を作る。 |
| Buyer / user | fleet operations、OEM fleet service、remote diagnostics、EPS / SbWサプライヤのdiagnostics / quality / service engineering、customer technical interface。 |
| Why supplier can play | EPS / SbWサプライヤは、DTC、DID、freeze frame、extended data、motor current、assist state、limit state、thermal state、voltage、communication state、software/calibration ID、degraded stateを理解している可能性がある。 |
| EPS supplier conclusion | まだ売らない。次に実施するのは、買い手、データアクセス、既存remote diagnosticsとの差分を確認する検証である。 |
| Demo | 20〜50件のsource分類表と、1ケースの運行可否/入庫優先度/診断優先度sample。 |
| What not to claim | EPS交換時期の正確予測、保証費削減、root cause断定、安全機能の代替、サプライヤ単独fleet監視。 |
| Kill criteria | 操舵系またはchassis系のdowntime / unplanned service / diagnostic time painが出ない、データアクセス不可、既存remote diagnosticsで十分、買い手がfleet platform側に固定、出力が交換時期予測だけになる。 |

## 何を判断しているか

判断しているのは、EPS単体の故障予測を復活させるかではない。

判断しているのは、自動運転車両、配送車、商用車、シャトルなどの車両群で、操舵系を含む重要部品の状態から、次の運行に出すか、先に入庫させるか、次回点検まで様子見するか、診断で何を先に読むかを決める需要があるかである。

この判断は、fleet operations、OEM fleet service、remote diagnostics、EPS / SbWサプライヤのdiagnostics / quality / service engineeringに関係する。

## 検証質問1〜5の回答

| 検証質問 | 現時点の回答 | Confidence | 判断 |
|---|---|---|---|
| MHQ001: 操舵系理由の運行停止や予定外入庫は本当に痛いか | fleet一般では痛い。AV truckでもmaintenanceとuptimeが明示される。操舵系に絞ると、Nexteerのsteering/chassis healthが最も直接的な証拠 | Medium | 継続。ただし「fleet downtime一般」から「steering/chassis起因」へ絞る追加調査が必要 |
| MHQ002: 買い手は誰か | fleet operator、mobility/logistics provider、OEM fleet service、remote diagnostics platformが見える。EPSサプライヤが直接買い手になるより、OEM/fleet service経由が自然 | Medium | buyer仮説を「OEM/fleet service + supplier diagnostics支援」に寄せる |
| MHQ003: EPS/SbWサプライヤは必要データにアクセスできるか | Nexteerは匿名化された実使用条件データを品質・開発に使うと説明している。Boschもconnected vehicle dataを使うfleet maintenance基盤を出している。ただしEPS固有DTC/DID、整備履歴、交換結果へのアクセスは不明 | Low to Medium | 最大Kill gate。データアクセスが確認できなければ止める |
| MHQ004: 価値ある出力は交換時期ではなく運行/入庫判断か | はい。公開情報では、repair prioritization、dynamic maintenance scheduling、garageへ戻すかの判断、parts preparation、diagnostic time reductionが繰り返し出る | High | 出力は「残寿命」ではなく「運行可否 / 先に入庫 / 部品準備 / 診断優先度」に固定する |
| MHQ005: DTCや通常診断だけでは粗いか | raw DTCだけでは粗い可能性が高い。Geotabは大量のfault codeを理解しrepair priorityへ変換する必要を説明し、Torc/AutoSensはAVでは従来OBDがreactiveで不足すると述べる。ただし既存remote diagnosticsが一般層を既に押さえている | Medium | EPS/SbWサプライヤの差分は「汎用DTC解釈」ではなく、操舵系状態・冗長低下・DID読み順・整備判断への翻訳に限定する |

## Evidence Signal

詳細は [data/archive/motion_health/motion_health_mhq001_005_evidence.tsv](../../../data/archive/motion_health/motion_health_mhq001_005_evidence.tsv) に置いた。

重要なsignal:

- Nexteer MotionIQ/Healthは、steering、chassis components、tiresのhealth monitoringを、fleet downtime低減、maintenance scheduling、diagnostic time reductionに結びつけている。
- Nexteer Prognosticsは、fleet uptime、scheduled maintenance、chassis component failure detection、actual lifecycle conditionsからのquality insightを説明している。
- Bosch cloud and predictive diagnosticsは、logistics companiesとmobility service providersに対して、vehicle issuesがoperationsへ影響する前に特定する価値を説明している。
- Bosch FleetMEは、vehicle data、diagnostics、OEM maintenance schedules、repair guidance、partsをつないでdynamic maintenance schedulingへ使う。
- Waymo / Ryder、Aurora / Ryderは、自動運転truckでmaintenance practice、on-site maintenance、uptime / utilizationが重要になることを示している。
- Geotab、Verizon Connect、Volvo Trucks、Internationalは、remote diagnostics、fault code prioritization、garage return判断、parts preparation、diagnostic time reductionをfleet workflowとして説明している。
- Torc / AutoSensは、AVでは従来OBDがreactiveであり、よりproactiveなmaintenanceと高品質データ、standards、supplier collaborationが必要だと説明している。
- Bosch Engineering、Bosch fail-operational EPS、ZF、NHTSA SbW reportは、EPS / SbWが自動運転・高可用操舵で重要な部品であることを示す。ただし、これは整備商品需要の証明ではなく、対象部品として見る理由である。

## 仮説の修正

最初の仮説:

> EPSやSbWの交換時期がリアルタイムで分かれば需要がありそう。

検証後の仮説:

> 自動運転・商用車両群では、操舵系を含むchassis/motion systemについて、交換時期を当てるよりも、次の運行に出せるか、先に入庫させるか、どの診断情報を優先して読むか、部品を準備すべきかを判断する需要がある可能性がある。

ここでEPS / SbWサプライヤが主語になれるのは、fleet platform全体を持つことではない。
操舵系のDTC、DID、freeze frame、extended data、motor current、assist state、limit state、thermal state、voltage、communication state、software/calibration ID、冗長低下、degraded stateを、運行・整備判断へ翻訳する部分である。

## 初期提供物

すぐ作るべきものは予測モデルではない。

最初に作るなら、20〜50件の公開sourceから、次のような判断表を作る。

| 項目 | 内容 |
|---|---|
| 車両/業務場面 | AV truck terminal、delivery fleet、bus/shuttle、commercial OEM service |
| 痛み | downtime、scheduled maintenance、diagnostic time、parts preparation、return-to-garage判断 |
| 操舵系との接点 | steering/chassis health、SbW redundancy、HAD EPS、DTC/DID、chassis actuator |
| 既存診断との関係 | raw DTCで足りるか、remote diagnosticsで足りるか、操舵系domain knowledgeが必要か |
| 出力 | next operation OK、early service、wait until scheduled inspection、prepare part、read DID first |
| サプライヤ境界 | EPS / SbW supplierが言えること、OEM/fleet/serviceに依存すること |
| Kill signal | engine/tire/brakeだけで操舵系が出ない、data access不可、既存remote diagnosticsで十分 |

## EPSサプライヤとしての結論

EPSサプライヤとして売るか:

> まだ売らない。公開情報だけでは、買い手、データアクセス、既存remote diagnosticsとの差分が不足している。

EPSサプライヤとして実施できること:

> 次の検証として、fleet/AV maintenanceの公開sourceを20〜50件集め、操舵系・chassis系が運行停止、予定外入庫、診断時間、入庫優先度に出てくるかを分類する。並行して、EPS / SbWサプライヤが持てるDTC/DID/状態量が、remote diagnosticsのrepair priorityへ変換できる余地を整理する。

EPSサプライヤとして言ってはいけないこと:

> EPS交換時期を正確に予測できる、保証費を削減できる、root causeを断定できる、安全機能を予測で代替できる、fleet全体をサプライヤ単独で監視できる、とは言わない。

初期対象外:

> OEM fleet platformの構築、汎用remote diagnostics、保険、driver behavior、engine diagnostics、tire-only analytics、service network運営は初期対象外に置く。

次に見せる部署:

> EPS / SbWサプライヤ内では、diagnostic engineering、service engineering、quality / field quality、customer technical interface、business developmentに見せる。functional safetyには、SbW degraded stateを整備判断へ接続する場合だけ見せる。

## 追加テーマ候補

時間が余る場合に見るべき追加テーマは2つある。

1. SbWや高可用操舵で、冗長系の一部低下を「次の運行に出してよいか」へつなげられるか  
   これは安全設計支援ではなく、degraded stateを整備・運行判断へ翻訳できるかの確認である。

2. EPS単体ではなく、brake、chassis actuator、tires、power、communicationと一緒にmotion healthとして扱うべきか  
   Nexteerの公開情報はこの方向に近い。EPS単体に閉じると旧テーマへ戻る危険がある。

## Kill条件

以下が確認されたら、この新テーマも止める。

- fleet/AV maintenance sourceを20〜50件見ても、操舵系またはchassis系のdowntime / unplanned service / diagnostic time painが出ない
- 買い手がfleet platformやOEM serviceに固定され、EPS / SbWサプライヤが成果物を持てない
- EPS / SbWサプライヤが、運行データ、DTC、DID、整備履歴、交換結果へアクセスできない
- 既存remote diagnosticsやDTC severity分類で十分で、操舵系domain knowledgeの差分がない
- 出力が「交換時期予測」だけになり、運行可否、入庫優先度、診断時間短縮へ転記できない
- 故障予測、保証費削減、root cause断定に戻る

## CoVe

| 検証質問 | Evidence | Confidence | 修正 |
|---|---|---|---|
| fleet/AVでmaintenanceとuptimeは痛いか | Waymo/Ryder、Aurora/Ryder、Bosch、Geotab、Volvoがmaintenance / uptime / utilizationを明示 | High | 市場需要は「安全」ではなく「運行・整備判断」と書く |
| 操舵系まで需要が見えるか | Nexteerがsteering/chassis/tire healthをfleet downtimeと診断時間に接続 | Medium | steering-specific painはPartial。追加分類が必要 |
| 買い手は見えるか | fleet operator、mobility/logistics service provider、OEM fleet service、remote diagnostics platformは見える | Medium | EPS supplier直接販売ではなく、OEM/fleet service経由の仮説へ修正 |
| サプライヤがデータに触れるか | Nexteerはactual lifecycle condition data、Boschはconnected vehicle dataを扱うが、EPS DTC/DID/交換結果のアクセスは不明 | Low to Medium | 最大Kill gateとして残す |
| DTCだけでは不足か | Torc/AutoSensはAVでOBDがreactive、Geotabは大量DTCをpriorityへ変換する必要を説明 | Medium | raw DTC不足は言えるが、既存remote diagnosticsとの差分は未確認 |
| 旧テーマに戻っていないか | 出力を交換時期ではなく運行可否/入庫優先度/診断優先度へ変えた | High | RULや保証費削減を禁止主張に残す |

## 次の最小アクション

次は、20〜50件のsourceを集める。
見る対象は、fleet predictive maintenance一般ではなく、以下に絞る。

- autonomous truck / shuttle / robotaxi maintenance
- commercial vehicle remote diagnostics
- chassis / steering / brake / tire health monitoring
- supplier software that uses actual lifecycle data
- repair prioritization、garage return、parts preparation、diagnostic time reduction

この分類で、操舵系またはchassis系が3〜5件以上、運行可否・入庫優先度・診断時間短縮へ明示的に接続できるなら、1ケースsampleへ進む。
出なければ、この新テーマもArchiveする。

## Sources

- Nexteer, MotionIQ software suite: https://www.nexteer.com/release/nexteer-unveils-its-motioniq-software-suite-for-intelligent-motion-control/
- Nexteer, Prognostics: https://www.nexteer.com/software/prognostics/
- Nexteer, MotionIQ one-pager: https://www.nexteer.com/wp-content/uploads/2025_MotionIQ-One-Pager.pdf
- Bosch, Cloud and predictive diagnostics: https://www.bosch-mobility.com/en/solutions/software-and-services/cloud-and-predictive-diagnostics/
- Bosch, FleetME press release: https://us.bosch-press.com/pressportal/us/en/press-release-27904.html
- Waymo, Expanding Waymo Via operations: https://waymo.com/blog/2021/08/expanding-our-waymo-via-operations/
- Ryder, Waymo autonomous truck maintenance partnership: https://newsroom.ryder.com/news/news-details/2021/Ryder-and-Waymo-Enter-PartnershipFocused-on-Autonomous-Truck-MaintenanceSights-Set-on-Scaling-Operations-Nationwide/default.aspx
- Ryder, Aurora on-site fleet maintenance: https://newsroom.ryder.com/news/news-details/2022/Aurora-and-Ryder-to-Pilot-On-Site-Fleet-Maintenance-for-Autonomous-Trucking/default.aspx
- Geotab, Remote diagnostics for commercial trucks: https://www.geotab.com/blog/remote-diagnostics/
- Geotab, Fleet maintenance software: https://www.geotab.com/fleet-management-solutions/fleet-maintenance/
- Verizon Connect, Connected fleet maintenance: https://www.verizonconnect.com/resources/article/how-connected-fleet-maintenance-management-software-helps-prevent-downtime/
- Volvo Trucks, Remote Diagnostics: https://www.volvotrucks.us/our-difference/uptime-and-connectivity/remote-diagnostics/
- International, Advanced Remote Diagnostics: https://www.international.com/services/my-international/advanced-remote-diagnostics
- AutoSens / Torc, Predictive maintenance for autonomous vehicles: https://auto-sens.com/blog/predictive-maintenance-for-autonomous-vehicles/
- Bosch Engineering, Steering systems: https://www.bosch-engineering.com/services/mobility-solutions/motion/steering-systems/
- Bosch, fail-operational EPS press release: https://us.bosch-press.com/pressportal/us/en/press-release-728.html
- Bosch Mobility, steer-by-wire: https://www.bosch-mobility.com/en/solutions/steering/steer-by-wire/
- ZF, steer-by-wire: https://www.zf.com/mobile/en/technologies/by_wire/stories/sbw.html
- NHTSA, Functional Safety Assessment of a Generic Steer-by-Wire Steering System: https://www.nhtsa.gov/sites/nhtsa.gov/files/documents/13502_812576_steerbywire.pdf
