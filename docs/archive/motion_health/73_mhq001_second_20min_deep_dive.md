# MHQ001 追加20分深掘りと判定修正

## 結論

MHQ001は、`Proceed` ではなく **Hold / Continue Investigation** と読むのが正しい。

Fleet downtime一般、AV maintenance、chassis / motion healthには需要signalがある。
しかし、steering / EPS / SbW固有の予定外入庫painが強いこと、EPS/SbWサプライヤが買い手または主語になれること、既存remote diagnosticsでは足りないことはまだ確認できていない。

したがって、MHQ001は「Killではない」までである。
次に進むなら、steering-onlyではなく、chassis / motion healthの一部として続ける。

## Item Conclusion

| Item | Conclusion | Confidence | Evidence | Weak point | Next action |
|---|---|---|---|---|---|
| MHQ001 | Hold / Continue Investigation。fleet downtimeとAV maintenanceは強いが、steering-onlyの購買painは未確認。chassis / motion healthとしてなら継続価値あり | Medium for motion health, Low-Medium for steering-only | Nexteer、ZF、3rd Eye、Bosch、Webfleet、Amerit、Oxmaint、HDT、Garrett、Volvo、Geotab | steering-onlyの予定外入庫頻度、顧客導入、既存remote diagnosticsとの差分 | MHQ003 data-rights mapとMHQ005 existing remote diagnostics差分へ進める |

## Deepened Points

### 1. Steering固有は「整備・安全・法規」までは出る

Oxmaintは、commercial vehicleのsteering failureをdowntime、regulatory penalties、DOT inspection、out-of-serviceに接続している。
Heavy Duty Truckingは、steering complaints、steering gear / pump診断、active steeringのerror notification、proactive maintenance concernsを扱っている。
Garrettは、drive-by-wire steeringの症状やscan code履歴を、fleet/work routeのdowntime回避と結びつけている。
FMCSA / eCFR / CVSA側でも、steering wheel systemsやout-of-service criteriaは商用車の運行可否に関わる安全・法規項目として確認できる。

これで言えること:

> Steeringはfleet maintenanceの対象であり、放置すると安全・法規・稼働に影響する。

まだ言えないこと:

> Steering health monitoringが独立した購買painになっている、EPS/SbWサプライヤが外販できる、とは言えない。

### 2. 既存remote diagnosticsの主戦場は別に見える

Volvo Remote Diagnosticsは、engine、I-Shift、aftertreatmentを前面に出している。
Geotabのpredictive maintenanceでも、brake、tire、engine malfunctionが目立つ。

これは、fleet downtime市場が強い一方で、steering-onlyが同じ優先度で買われるとは限らないことを示す。

### 3. Chassis / motion healthなら残る

Nexteer MotionIQ/Healthは、steering、chassis components、tiresをfleet downtime、maintenance scheduling、diagnostic time reductionへ直接つないでいる。
ZFもchassis / drivetrainのtechnical condition monitoring、repair recommendation、downtime reductionを説明している。
3rd Eyeもchassis、body、equipmentのmonitoringをfleet maintenance decisionへつなげている。

このため、探索軸は次のように修正する。

悪い軸:

> EPS / steering単体の故障予測。

良い軸:

> Steering / SbW / brake-by-wire / chassis actuator / tireを含むmotion healthのうち、EPS/SbWサプライヤが説明できる部分を運行可否・点検優先度へ翻訳できるか。

## What Changed

前回:

> Proceed。ただしEPS単体ではなくchassis / motion healthとしてProceed。

今回:

> Hold / Continue Investigation。Killではないが、まだ通過ではない。Chassis / motion healthとしてだけ継続。

変更理由:

- steering-onlyの公開証拠が、整備・点検・法規・安全には届くが、購買painや外販商品価値までは届かない
- 既存remote diagnosticsはengine / aftertreatment / transmission / brake / tireが強く、steeringが主戦場とは見えない
- Nexteerは強いsignalだが、単独sourceに依存している

## Market Demand First

| Field | 内容 |
|---|---|
| Market demand | Fleet / AV運用では、車両停止、予定外入庫、診断時間、部品待ちが運行効率を落とす。 |
| Unresolved pain | Steering単独の予定外入庫painは未確認。Chassis / motion healthならdowntimeや点検計画との接続が見える。 |
| Hypothesis | EPS/SbWサプライヤは、steering-onlyではなくmotion healthの一部として、操舵系状態を運行可否・点検優先度へ翻訳できる可能性がある。 |
| Solution | 次は20-50 source分類ではなく、MHQ003 data-rights mapとMHQ005 existing remote diagnostics差分を先に潰す。 |
| Buyer / user | OEM fleet service、remote diagnostics、fleet maintenance、supplier diagnostics / service engineering。 |
| Initial artifact | data-rights map、existing remote diagnostics comparison、steering domain triage sample。 |
| Validation method | EPS/SbWサプライヤが触れるデータ、既存remote diagnosticsが持たない操舵系状態、運行判断への転記先を確認する。 |
| Kill criteria | data access不可、既存remote diagnosticsで十分、steering/chassisが通常点検・法規対応で終わる、交換時期予測に戻る。 |

## EPS Supplier Lens

EPS/SbWサプライヤとして売るか:

> まだ売らない。

EPS/SbWサプライヤとして実施できること:

> Steering-specific pain探しを続けるより、データアクセスと既存remote diagnosticsとの差分を潰す。自社が持つDTC、DID、assist state、limit state、thermal state、motor current、software/calibration ID、SbW degraded stateが、fleet側の運行可否や点検優先度へ本当に翻訳できるかを見る。

言ってはいけないこと:

> EPS交換時期を正確に予測できる、steering-onlyで強い購買需要がある、保証費を削減できる、root causeを断定できる、とは言わない。

次に見せる部署:

> diagnostic engineering、service engineering、field quality、customer technical interface。Business developmentには、まだProceedではなくHoldとして見せる。

## Stop / Continue Judgment

MHQ001は、追加深掘り後もStopではない。
しかし、Proceedでもない。

次に深掘るなら、MHQ001をさらに広げるより、以下を優先する。

1. MHQ003: data-rights map  
   EPS/SbWサプライヤがDTC/DID、整備履歴、交換結果へ触れないなら、このテーマは止まる。

2. MHQ005: existing remote diagnostics差分  
   Bosch、Volvo、Geotab、Internationalで足りるなら、EPS/SbWサプライヤの外販価値は残らない。

## Sources

- Oxmaint steering inspection checklist: https://oxmaint.com/industries/fleet-management/steering-inspection-checklist
- Garrett drive-by-wire steering service: https://www.garrettauto.com/what-is-drive-by-wire-steering-and-how-to-maintain-it
- Heavy Duty Trucking steering maintenance: https://www.truckinginfo.com/articles/what-to-know-about-steering-system-maintenance
- Bosch steer-by-wire: https://www.bosch-mobility.com/en/solutions/steering/steer-by-wire/
- Geotab predictive maintenance: https://www.geotab.com/blog/predictive-maintenance/
- Volvo Remote Diagnostics: https://www.volvotrucks.us/our-difference/uptime-and-connectivity/remote-diagnostics/
- NHTSA generic steer-by-wire safety assessment: https://www.nhtsa.gov/sites/nhtsa.gov/files/documents/13502_812576_steerbywire.pdf
- FMCSA steering wheel systems: https://csa.fmcsa.dot.gov/safetyplanner/MyFiles/SubSections.aspx?ch=22&sec=64&sub=141
- CVSA out-of-service criteria: https://cvsa.org/inspections/out-of-service-criteria/
- eCFR 49 CFR 393.209: https://www.ecfr.gov/current/title-49/subtitle-B/chapter-III/subchapter-B/part-393/subpart-J/section-393.209
