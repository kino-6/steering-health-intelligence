# MHQ003 / MHQ005 深掘りによるMHQ001判定更新

## 結論

MHQ001は、前回の **Hold / Continue Investigation** から、少し **Stop寄りのHold** に修正する。

自動運転車両や商用車両群では、車両停止、予定外入庫、診断時間、部品準備を減らしたい需要はある。
ただし、その需要をEPS/SbWサプライヤが取れるかは、2つの門でかなり絞られる。

1つ目は、EPS/SbWサプライヤが必要なデータに触れるかである。
公開情報では、車両データAPI、DTC API、OEM cloud、supplier cloud連携、EU Data Actの流れは見える。
しかし、EPS固有DID、freeze frame、extended data、整備履歴、交換結果、再発有無、作業時間へ触れるとはまだ言えない。

2つ目は、既存remote diagnosticsで足りてしまわないかである。
Bosch、International、Geotab、Volvo、OnStar、Smartcarは、fault code、severity、risk / criticality、action plan、API、diagnostic time reductionをすでに扱っている。
そのため、単にDTCを読んで優先度を付けるだけでは、新しい外販価値になりにくい。

したがってMHQ001は、まだKillではないが、次の1ケースsampleで差分が出なければ止める。
続ける場合も、steering-onlyではなく、chassis / motion healthのうちEPS/SbWサプライヤが説明できる状態量だけに絞る。

## 何を判断しているか

判断しているのは、操舵系の故障予測を売れるかではない。

判断しているのは、fleet / OEM service / remote diagnosticsの現場で、EPSやSbWの状態を「次の運行に出す」「先に入庫する」「次回点検まで様子を見る」「診断でこのDIDを先に読む」といった判断へ翻訳できるかである。

この翻訳が成立するには、次の2条件が要る。

- 必要なデータに触れること
- 既存remote diagnosticsでは説明しきれない操舵系固有の差分があること

MHQ003とMHQ005を深掘りした結果、この2条件はどちらも未確認であり、MHQ001をProceedに上げる材料にはならなかった。

## MHQ003: データアクセス

### 現時点で言えること

車両データにアクセスする市場や制度は存在する。

EUはData Actに関連してvehicle data guidanceを出しており、対象stakeholderにはOEM、suppliers、aftermarket service providers、insurersが含まれる。
GM FleetのOnStar APIは、fleet向けにDTCやcomprehensive diagnostic dataを含むvehicle health dataを提供する。
Smartcarも、DTC、system status、odometerのようなdiagnostics APIを、user authorizationを前提に提供している。
High Mobilityも、brandごとのscopeやupdate frequencyに依存しながら、diagnostics、maintenance、dashboard lights、tire pressure、odometerなどの車両データを扱っている。

また、ZFはvehicle health monitoringで、OEM cloudとZF cloudのデータ交換を説明している。
これは、Tier-1 supplierがOEM連携の中でfield dataを使う公開例として強い。

### まだ言えないこと

EPS/SbWサプライヤが、必要な細かい診断データと整備結果へ自由に触れるとは言えない。

公開APIで見えるのは、DTC、vehicle health、odometer、tire pressure、dashboard lightsのような比較的上位のデータが中心である。
EPS固有DID、assist state、limit state、thermal derate、motor current、software / calibration ID、freeze frame、extended data、整備履歴、交換結果、再発有無、作業時間は、公開情報だけでは確認できない。

つまり、データアクセスは「市場インフラがある」では足りない。
EPS/SbWサプライヤに必要なのは、OEMやfleetから許可される具体的なdata fieldと、利用目的の契約である。

## MHQ005: 既存remote diagnosticsとの差分

### 現時点で言えること

raw DTCだけでは、fleetの運行判断には粗い。

Geotabは、商用車が大量のfault codeを出すため、remote diagnosticsでfaultを理解しrepair priorityへ変換する必要があると説明している。
Bosch cloud diagnosticsは、故障内容、error code、risk / criticality assessment、推奨next step、関連faultのgrouping、component localizationを扱う。
International Advanced Remote Diagnosticsは、fault code、severity rating、action plan、dealer parts inventory、service center mapping、fleet platformへのAPI接続を扱う。
Volvo Remote Diagnosticsは、engine、I-Shift、aftertreatmentを監視し、diagnostic time reductionを説明している。
OnStarやSmartcarも、DTCやvehicle health APIを提供している。

### 反証として強い点

これは同時に、MHQ001への強い反証でもある。

DTCを読み、severityを付け、action planを出し、fleet platformへつなぐところまでは、既存remote diagnosticsがかなり押さえている。
したがって、EPS/SbWサプライヤが「DTCを分かりやすくする」「優先度を付ける」と言うだけでは、既存領域に飲まれる。

残る可能性は、操舵系のdomain knowledgeがないと切れない判断だけである。

- assist state、limit state、thermal derate、motor current、voltage、communication stateの意味づけ
- software / calibration IDと症状・診断判断の接続
- SbW redundancy degraded / fallback stateを運行可否へ翻訳すること
- どのDIDを先に読むべきかのsteering domain triage
- bench / HILS / durability knowledgeから、fleet側に言ってよいことと言ってはいけないことを切ること

この差分を1ケースsampleで自然言語にできなければ、MHQ001は止めるべきである。

## MHQ001への戻し込み

| 判定項目 | 更新後の見方 |
|---|---|
| 市場需要 | Fleet downtime、予定外入庫、診断時間短縮の需要は強い。 |
| Steering-only需要 | まだ弱い。整備・法規・安全の対象ではあるが、独立購買painは未確認。 |
| Chassis / motion health需要 | NexteerとZFが強いsignal。ただしOEM連携やcloud契約前提に見える。 |
| データアクセス | 最大Kill gate。公開APIやData Actの流れはあるが、EPS固有data fieldとservice outcomeは未確認。 |
| 既存診断との差分 | かなり厳しい。remote diagnosticsはfault priority、action plan、API連携まで進んでいる。 |
| EPS/SbW supplierの残余余地 | 汎用DTC解釈ではなく、操舵系状態量、SbW degraded state、software/calibration接続、DID読み順の説明に限定。 |
| 更新後判断 | Hold / Stop-leaning。次の1ケースsampleで差分が出なければStop。 |

## Market Demand First

| Field | 内容 |
|---|---|
| Market demand | Fleet / AV運用では、車両停止、予定外入庫、診断時間、部品準備が運行効率を落とす。 |
| Evidence signal | Bosch、International、Geotab、Volvo、OnStar、Smartcarはremote diagnosticsやDTC/APIをfleet workflowへつないでいる。NexteerとZFはchassis / motion healthをsupplier側の公開signalとして出している。 |
| Hypothesis | EPS/SbWサプライヤは、汎用DTC解釈ではなく、操舵系状態量を運行可否・点検優先度・診断読み順へ翻訳できる場合だけ価値がある。 |
| Solution | 次は広いsource収集ではなく、1ケースsampleで既存remote diagnosticsとの差分を検証する。 |
| Buyer / user | OEM fleet service、remote diagnostics、fleet maintenance、EPS/SbWサプライヤのdiagnostic engineering / service engineering / field quality。 |
| Why supplier can play | EPS/SbWサプライヤは、assist state、limit state、motor current、thermal state、software/calibration ID、SbW degraded state、bench/HILS知見を理解している可能性がある。 |
| EPS supplier conclusion | まだ売らない。MHQ001はStop寄りのHold。1ケースで差分が出ないならArchiveする。 |
| Demo | 「車輪を動かす側の冗長系が一部落ちた」または「高負荷操舵でthermal limitに入った」ケースを、DTCだけ、既存remote diagnostics、supplier domain triageの3列で比較する。 |
| What not to claim | EPS交換時期の予測、保証費削減、root cause断定、安全機能の代替、supplier単独fleet監視、既存remote diagnostics置換。 |
| Kill criteria | 必要data fieldに触れない、service outcomeが取れない、既存remote diagnosticsと同じ説明になる、操舵系domain knowledgeなしで判断できる、出力が交換時期予測に戻る。 |

## Chain Of Verification

| Verification question | Evidence | Confidence | Impact |
|---|---|---|---|
| 車両データアクセスの制度・市場はあるか | EU vehicle data guidance、OnStar API、Smartcar、High Mobility | High | data accessを完全否定しない |
| EPS/SbWサプライヤが必要data fieldに触れるか | ZF cloud連携はsupplier pathwayを示すが、EPS固有DIDやservice outcomeは未確認 | Low to Medium | 最大Kill gateのまま |
| raw DTCだけでは粗いか | Geotab、Bosch、Internationalがpriority/action plan/risk assessmentを扱う | High | raw DTC不足は支持 |
| 既存remote diagnosticsで足りる可能性はあるか | Bosch、International、Volvo、OnStar、Smartcarが広くカバー | High | MHQ001をStop寄りに修正 |
| EPS/SbW supplier固有差分は公開情報で証明できたか | Nexteer/ZFはmotion health signalを出すが、顧客導入やdata fieldは不明 | Low to Medium | Proceedには上げない |

## EPSサプライヤとしての言い方

EPS/SbWサプライヤとして言えること:

> Fleet downtimeやremote diagnosticsの市場はある。ただし、当社が売れるかは、操舵系状態量を既存remote diagnosticsでは出せない運行・整備判断へ翻訳できるかで決まる。

まだ言ってはいけないこと:

> EPSの交換時期が分かる、既存remote diagnosticsを置き換えられる、fleet downtimeを削減できる、root causeを断定できる、とは言わない。

次に見る最小項目:

> 1ケースsampleで、DTCだけで分かること、既存remote diagnosticsで分かること、EPS/SbWサプライヤのdomain knowledgeがないと分からないことを3列で比較する。

## Sources

- European Commission, Guidance on vehicle data, accompanying the Data Act: https://digital-strategy.ec.europa.eu/en/library/guidance-vehicle-data-accompanying-data-act
- Auto Care, Access to and Control of Vehicle Data: https://www.autocare.org/government-relations/current-issues/access-to-and-control-of-vehicle-data
- GM Fleet, OnStar API Services: https://www.gmfleet.com/software/onstar/api-services
- Smartcar, real-time vehicle diagnostics: https://smartcar.com/docs/getting-started/guides/real-time-vehicle-diagnostics
- High Mobility, Car Data API: https://www.high-mobility.com/car-data
- ZF, Vehicle Health Monitoring: https://press.zf.com/press/en/releases/release_92162.html
- Bosch, Cloud and predictive diagnostics: https://www.bosch-mobility.com/en/solutions/software-and-services/cloud-and-predictive-diagnostics/
- International, Advanced Remote Diagnostics: https://www.international.com/services/my-international/advanced-remote-diagnostics
- Geotab, Remote diagnostics for commercial trucks: https://www.geotab.com/blog/remote-diagnostics/
- Volvo Trucks, Remote Diagnostics: https://www.volvotrucks.us/our-difference/uptime-and-connectivity/remote-diagnostics/
- OnStar Canada, API & Data Services: https://www.onstar.ca/en/business-solutions/api-data-services
- ASAM, SOVD: https://www.asam.net/standards/detail/sovd/
