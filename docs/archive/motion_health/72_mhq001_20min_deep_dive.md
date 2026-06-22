# MHQ001 20分深掘り

## 結論

MHQ001の結論は、前回の `Proceed` から下げる。

自動運転車両や商用車両群で、車両停止、予定外入庫、診断時間、部品待ちが大きな業務痛みであることはかなり強い。
また、操舵系を含むchassis / motion healthとして見るなら、Nexteer、ZF、3rd Eyeの公開情報から、運行停止低減、点検計画、診断時間短縮へ接続する公開signalがある。

ただし、まだ「EPS単体」「steering-only」の予定外入庫が大きいとは言えない。
公開情報上で強いのは、steering単体ではなく、steering、chassis、tires、brake、body/equipmentを含む車両運動系・車両状態のhealth monitoringである。

したがってMHQ001は、**Hold / Continue Investigation** である。
旧テーマのように即Killではないが、まだ通過判定でもない。
続けるなら、EPS単体やsteering-onlyではなく、chassis / motion healthとして続ける。

## MHQ一覧

全MHQの作業面は [data/archive/motion_health/motion_health_mhq_work_surface.tsv](../../../data/archive/motion_health/motion_health_mhq_work_surface.tsv) に置いた。
今回の20分枠では、MHQ001だけ深掘りした。

| MHQ | 現在の結論 | Priority |
|---|---|---|
| MHQ001 | Fleet downtime一般とAV maintenanceの痛みは強い。steering単独では弱く、chassis/motion healthなら継続価値あり。ただし通過ではなく保留 | High |
| MHQ002 | 買い手はfleet/OEM service/remote diagnosticsが先。supplier directは弱い | Medium |
| MHQ003 | 最大Kill gate。DTC/DID/service outcomeへのアクセス未確認 | Highest |
| MHQ004 | 交換時期ではなく運行可否・入庫優先度・診断優先度が価値 | High |
| MHQ005 | raw DTCだけでは粗いが、既存remote diagnosticsとの差分が必要 | High |
| MHQ006 | SbW degraded stateを整備判断へ接続できるかは未検証 | Medium |
| MHQ007 | EPS単体よりmotion health bundleが有力 | High |
| MHQ008 | 実使用条件から品質・開発へ戻す価値は可能性あり | Medium |
| MHQ009 | 初期デモはsource分類表と1ケースsample | Medium |
| MHQ010 | まだKillではないが、data accessと既存診断との差分が門 | High |

## MHQ001で何を判断しているか

判断しているのは、EPS単体の故障予測を売れるかではない。

判断しているのは、自動運転車両、配送車、商用車、シャトルなどの車両群で、操舵系を含む車両運動系の状態が、運行停止、予定外入庫、診断時間、点検優先度の業務痛みとつながるかである。

## Evidence

詳細TSVは [data/archive/motion_health/motion_health_mhq001_deep_dive_evidence.tsv](../../../data/archive/motion_health/motion_health_mhq001_deep_dive_evidence.tsv) に置いた。

### 1. Fleet downtime一般は強い

Webfleetは、fleet車両が業務利用できない状態をdowntimeとし、planned / unplanned downtime、収益・評判・TCOへの影響、vehicle health tracking、maintenance scheduling、diagnostic trouble code通知を一連のfleet課題として説明している。

Boschも、logistics companiesとmobility service providersにとってfleet reliability / efficiencyが重要であり、vehicle issuesがoperationsへ影響する前に特定すること、risk / criticality assessment、workshop planning、operational readinessを価値として説明している。

このため、MHQ001のうち「運行停止や予定外入庫は痛いか」はHigh confidenceでYesである。

### 2. AV maintenanceも強い

Ameritは、robotaxi、shuttle、freight AVのmaintenanceを、sensor failure、software lag、ride disruption、revenue、deployment timeline、24/7 mission readiness、health dashboardと結びつけている。

PennDOTのAV shuttle reportも、運用時にはsystem monitoring、fleet maintenance、technology managementの常設役割が必要になると述べている。
Waymo / Ryder、Aurora / Ryderの公開情報も、autonomous truckでmaintenance practice、uptime、utilizationが重要になることを示している。

したがって「自動運転車両群ではmaintenanceとuptimeが運行価値に直結する」はHigh confidenceでよい。
ただし、ここでも操舵系固有ではなく、AV fleet maintenance全体の話である。

### 3. Steering / chassis固有はNexteerが一番強い

Nexteer MotionIQ/Healthは、steering、chassis components、tiresを継続監視し、fleet downtime低減、maintenance scheduling、diagnostic time reductionへ接続している。
NexteerのSoftware pageでも、MotionIQはEPS、SbW、Brake-by-Wire、software-defined chassis、commercial vehicleを含むhealth-monitoring workflowとして説明されている。

これはMHQ001に対する最も強い公開signalである。
ただし、実顧客導入、停止件数、steering-only故障頻度、支払実績はまだ見えない。

### 4. Chassis / motion healthはNexteer以外にもある

ZFは、chassisまたはdrivetrainの重要system状態を監視・記録し、機能forecast、repair recommendation、downtime reduction、fleet/shared mobilityへのbenefitを説明している。

3rd Eyeは、chassis、body、equipmentを継続監視し、downtime reduction、diagnostic time improvement、severity / time-frame until failureを含むmaintenance判断へつなげている。

この2つは、steering-onlyではないが、chassis / motion healthとしてはMHQ001を補強する。

### 5. 反証: 既存remote diagnosticsはpowertrain中心に見える

反証側もある。
Volvo Remote Diagnosticsは、unexpected downtime低減とrepair迅速化を説明しているが、対象として前面に出るのはengine、I-Shift、aftertreatmentである。
GeotabもDTC理解とrepair prioritizationを扱うが、steering/chassis固有の痛みを示すものではない。

つまり、fleet downtime需要が強いことと、steering-onlyが主要購買対象になることは別である。
このため、MHQ001はsteering単独では進めない。
chassis / motion healthとしても、まだ「続けてよい」までであり、「通過」とは言わない。

### 6. 追加深掘り: steering固有は整備・安全・法規寄りに見える

OxmaintやHeavy Duty Truckingのような整備系情報では、steering systemはfleet inspection、DOT compliance、driver complaint、diagnostics、proactive maintenanceの対象として出てくる。
Garrettのdrive-by-wire steering記事でも、fleet/work routeではdowntimeを避けるために症状やscan code履歴を持って早めに診断する文脈がある。

これは、steeringがfleet maintenance対象であることを支持する。
しかし、まだ「steering health productが買われる」「EPS/SbWサプライヤが主語になる」「予定外入庫の大きなpainがsteeringに集中している」ことまでは支持しない。

## 市場需要から見た整理

| Field | 内容 |
|---|---|
| Market demand | FleetやAV運用では、車両が止まる、予定外入庫になる、診断に時間がかかる、部品準備が遅れることが運行効率を落とす。 |
| Unresolved pain | 操舵系単体の痛みはまだ薄いが、steering/chassis/tire/brakeを含むmotion healthでは、運行停止・点検計画・診断時間短縮との接続が見える。 |
| Hypothesis | EPS/SbWサプライヤは、EPS単体の寿命予測ではなく、chassis / motion healthの一部として、操舵系状態を運行可否や点検優先度に翻訳できる可能性がある。ただし、MHQ001だけではまだ仮説に留まる。 |
| Solution | 20-50 source分類で、fleet downtime general、AV maintenance、chassis/motion specific、steering specific、counterevidenceを分ける。 |
| Buyer / user | 初期利用者はfleet operations、OEM fleet service、remote diagnostics、EPS/SbW supplier diagnostics / service engineering。 |
| Initial artifact | MHQ001 evidence table、source分類表、steering/chassis operational pain map。 |
| Validation method | steering/chassis明示sourceが3-5件以上あり、運行可否・入庫優先度・診断時間短縮に接続できるかを見る。加えて、既存remote diagnosticsが扱うengine / aftertreatment / transmission / brake / tireとの差分を確認する。 |
| Kill criteria | 20-50 source分類でengine、battery、tire、brake、sensor、softwareだけが出て、steering/chassisが出ないならEPS/SbW単独方向はStop。steeringが出ても通常整備・点検・法規だけなら、外販商品としてはStop。 |

## EPSサプライヤ視点

EPS/SbWサプライヤとして売るか:

> まだ売らない。MHQ001だけでは買い手、データアクセス、既存remote diagnosticsとの差分が足りない。

EPS/SbWサプライヤとして実施できること:

> Steering-onlyではなく、chassis / motion healthとしてsource分類を続ける。自社が持つDTC、DID、assist state、limit state、thermal state、motor current、software/calibration ID、SbW degraded stateを、fleet側の運行可否や点検優先度へ翻訳できるかを見る。

EPS/SbWサプライヤとして言ってはいけないこと:

> EPS交換時期を正確に予測できる、操舵故障を未然に防ぐ、保証費を削減できる、root causeを断定できる、とは言わない。

初期対象外:

> Fleet platform全体、汎用remote diagnostics、sensor cleaning、software update運用、service network運営は初期対象外に置く。

次に見せる部署:

> diagnostic engineering、service engineering、field quality、customer technical interface。Business developmentには、steering-onlyではなくmotion health bundleとして見せる。

## CoVe

| 検証質問 | 回答 | Confidence | 反映 |
|---|---|---|---|
| Fleet downtimeは痛いか | Webfleet、Bosch、3rd Eyeで強く支持 | High | 市場需要はある |
| AV maintenanceは痛いか | Amerit、PennDOT、Waymo/Ryder、Aurora/Ryderで支持 | High | AV fleetは対象に残す |
| Steering-specific painはあるか | Nexteerが直接支持。ただし実停止頻度や顧客導入は不明 | Medium | steering-only商品にはしない |
| Chassis/motion healthなら支持されるか | Nexteer、ZF、3rd Eyeで支持 | Medium-High | Killはしないが、通過ではなくHold |
| 反証はあるか | Volvoや既存remote diagnosticsはengine、aftertreatment、transmission中心に見える | High | steering-onlyではProceedしない |
| steering固有の追加証拠はあるか | Oxmaint、HDT、Garrettで整備・点検・安全・downtime文脈はある | Medium | 需要はあるが商品価値の証明には弱い |
| EPSサプライヤが主語になれるか | Nexteerは可能性を示すが、一般化はまだ危険 | Medium | MHQ003 data accessへ送る |

## Stop / Continue Judgment

MHQ001はStopしない。
ただし、Proceedとも呼ばない。
正しい判定は **Hold / Continue Investigation** である。

ただし、続け方を変える。

悪い続け方:

> EPS単体の故障予測や交換時期予測へ戻る。

良い続け方:

> Steering、SbW、brake-by-wire、chassis actuator、tiresなどを含むmotion healthとして、運行可否、入庫優先度、診断時間短縮へ接続できるかを見る。

次は、MHQ001を広げるより、`MHQ003 data-rights map` と `MHQ005 existing remote diagnosticsとの差分` を潰す方が判断が進む。

## Sources

- Nexteer MotionIQ/Health release: https://www.nexteer.com/release/nexteer-unveils-its-motioniq-software-suite-for-intelligent-motion-control/
- Nexteer Software: https://www.nexteer.com/software/
- Nexteer MotionIQ blog: https://www.nexteer.com/blog/motioniq-software-suite-precision-speed-and-quality-for-software-defined-chassis-development/
- ZF Vehicle Health Monitoring: https://press.zf.com/press/en/releases/release_92162.html
- 3rd Eye Fleet Maintenance: https://www.3rdeyecam.com/solution/fleet-maintenance/
- Bosch Cloud and Predictive Diagnostics: https://www.bosch-mobility.com/en/solutions/software-and-services/cloud-and-predictive-diagnostics/
- Webfleet Vehicle Downtime: https://www.webfleet.com/en_us/webfleet/fleet-management/fleet-maintenance/vehicle-downtime/
- Amerit Autonomous Fleet Maintenance: https://www.ameritfleetsolutions.com/industries/autonomous-vehicles/
- PennDOT AV Shuttle Detailed Analysis: https://www.pa.gov/content/dam/copapwp-pagov/en/penndot/documents/programs-and-doing-business/p3forpa/documents/acaa-av-shuttle-detailed-analysis-final-report.pdf
- Waymo Via / Ryder: https://waymo.com/blog/2021/08/expanding-our-waymo-via-operations/
- Ryder / Aurora: https://newsroom.ryder.com/news/news-details/2022/Aurora-and-Ryder-to-Pilot-On-Site-Fleet-Maintenance-for-Autonomous-Trucking/default.aspx
- Volvo Remote Diagnostics: https://www.volvotrucks.us/our-difference/uptime-and-connectivity/remote-diagnostics/
- Volvo expanded diagnostics news: https://www.volvogroup.com/en/news-and-media/news/2015/sep/news-150893.html
- Geotab remote diagnostics: https://www.geotab.com/blog/remote-diagnostics/
- Fleet preventive maintenance checklist: https://attrix.ca/en/blog/fleet-preventive-maintenance
