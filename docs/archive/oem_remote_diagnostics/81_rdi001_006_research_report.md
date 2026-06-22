# RDI001〜RDI006 調査レポート

## 結論

OEM遠隔診断に組み込む操舵系状態説明レイヤーは、まだProceedではない。
ただし、すぐKillでもない。

最も重要な結論は次である。

> Network参加の経路はある。  
> ただし、EPS/SbWサプライヤが自由に入れるopen networkではない。  
> 特定OEM program、approved provider、OEM API、supplier cloud-to-cloud、SOVD/API layerのどれかに乗る必要がある。

その上で、公開情報だけではEPS/SbW固有のDID、freeze frame、assist state、thermal state、motor current、software / calibration ID、service outcome feedbackまでは確認できない。
したがって、仮説の次の進め方は、広い市場調査ではなく、1ケースsampleで既存remote diagnosticsとの差分を作れるかを見ることである。

## Item Conclusions

詳細TSVは [data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi_research_findings.tsv](../../../data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi_research_findings.tsv) に置く。

| Item | Conclusion | Confidence | Evidence | Weak point | Next action |
|---|---|---|---|---|---|
| RDI001 | Network参加経路はあるがopenではない。OEM program / approved provider / cloud-to-cloud / SOVD/API layerのいずれかが必要 | Medium | GM OnStar API、Smartcar、High Mobility、ZF VHM、ASAM SOVD | EPS/SbW supplier-specific contentを入れる公開経路は未確認 | Network participation mapを作る |
| RDI002 | 公開APIはDTC / system status / vehicle health中心。EPS/SbW固有data fieldは未確認 | Medium-High for insufficiency | Smartcar DTC/System Status、OnStar API、High Mobility | DID、freeze frame、assist/thermal/software IDが見えない | Required data field listを作る |
| RDI003 | 既存remote diagnosticsはかなり強い。差分は内部状態量がaction planを変える場合だけ | High for counter-signal | Bosch、International、Platform Science、Geotab | steering-specific差分は未証明 | Difference tableを作る |
| RDI004 | service workflowはあるが、service outcome feedbackは未確認 | Low to Medium | Volvo Uptime/ASIST、International dealer/action plan、Geotab fault history | 整備結果や再発有無がsupplierへ戻る証拠が弱い | Service outcome feedback mapを作る |
| RDI005 | 責任境界は切れる可能性があるが、診断・整備判断支援に限定する必要がある | Medium | ASAM SOVD、repo docs/75 | 契約上の責任分担は公開情報では不明 | Responsibility boundary mapを作る |
| RDI006 | 最初のsampleはassist limitation / thermal limitがよい | Medium | docs/75 kill-check sample、既存remote diagnostics sources | 実dataではなく概念sampleになる | 4列sampleを作る |

## RDI001: Network参加経路

Network参加は、完全に否定されない。

GM FleetのOnStar APIは、fleet vehicle dataをAPI plansで提供し、DTCやcomprehensive diagnostic dataを含む。
またGM-approved third-party providersという枠がある。
Smartcarは、user authorizationを前提にDTCやsystem statusを取得するAPIを提供している。
High Mobilityも、diagnostics、maintenance、dashboard lightsなどのdata categoryと、brandごとのscope / update frequencyを示している。
ZFはVehicle Health Monitoringで、OEM cloudとZF cloudのデータ交換を説明している。
ASAM SOVDは、remote、proximity、in-vehicleのdiagnostic communicationと、classic ECUを含むdiagnostic contentへのAPI方向を示している。

ただし、これらは「誰でも入れるopen network」を意味しない。

Network参加の候補は4つに分かれる。

| Route | 評価 |
|---|---|
| OEM direct program | 最も現実的。OEMのremote diagnostics / fleet service成果物へ入る |
| approved provider / API | DTCやvehicle healthには届く可能性。ただしEPS/SbW内部data fieldは不明 |
| supplier cloud-to-cloud | ZF型の参考例あり。ただしOEM partnership前提 |
| SOVD / API layer | 診断APIの技術方向として有力。ただしplatform自体は既存標準領域 |

RDI001の判断:

> Hold / Critical gate。可能性はあるが、open参加ではない。特定OEM programまたは契約経路が必要。

## RDI002: EPS/SbW固有data field

ここは厳しい。

SmartcarのDTC APIは、active diagnostic trouble codesとtimestampを返す。
System Status APIは、systemId、status、descriptionを返す。
GM OnStar APIは、DTCとcomprehensive diagnostic dataを含むplanを示す。
High Mobilityは、diagnostics、maintenance、dashboard lights、tire pressure、odometerなどのdata categoryを示し、brandごとにscopeやupdate frequencyが変わることを示す。

しかし、公開情報だけでは次のdata fieldは確認できない。

- EPS/SbW固有DID
- freeze frame / extended data
- assist state
- limit state
- thermal state
- motor current
- software / calibration ID
- SbW degraded state

RDI002の判断:

> Stop-leaning / Data gate。公開APIだけでは差分の核になるdata fieldに届かない。特定OEM programが必要。

## RDI003: 既存remote diagnosticsとの差分

ここも厳しい。

Bosch cloud diagnosticsは、fault description、error code、risk / criticality assessment、recommended further steps、component localizationを扱う。
International Advanced Remote Diagnosticsは、fault code、severity rating、action plan、dealer parts inventory、service center mapping、API connectionを扱う。
Platform Science / Noregon TripVisionは、effect-on-vehicle descriptions、action plans、fault history、configurable reportsを扱う。
Geotabも、fault descriptions、severity、recommendations、nearest dealer / repair shop / towing provider mappingを扱う。

つまり、DTCを読んでseverityやaction planに変換するだけでは差分にならない。

差分が出るのは、EPS/SbW内部データが既存action planを変える場合だけである。
たとえば、同じDTCでもassist state、thermal state、motor current、software / calibration IDにより、追加で読むべきDIDや注意文が変わる場合である。

RDI003の判断:

> Hold but harsh。差分はあり得るが、公開情報では未証明。1ケースsampleで確認する。

## RDI004: service outcome feedback

Service workflowは存在する。

Volvo Remote Diagnosticsは、Uptime Center、ASIST、dealer network、電子見積、修理承認、dealer communicationを示している。
Internationalは、dealer parts inventory、service center mapping、API connectionを示している。
Geotabは、fault historyやreportsを示している。

ただし、これはservice outcome feedbackがEPS/SbWサプライヤへ戻ることの証明ではない。

説明ロジックを改善するには、次が必要である。

- 整備結果
- 交換結果
- 再発有無
- 作業時間
- parts usage
- dealer comment

公開情報では、このfeedback loopは確認できない。

RDI004の判断:

> Weak / OEM-program dependent。OEM service network内なら可能性はあるが、公開APIでは弱い。

## RDI005: 責任境界

責任境界は切れる可能性がある。
ただし、診断・整備判断支援に限定する必要がある。

EPS/SbWサプライヤが持てる範囲:

- 操舵系状態説明
- 追加DID読み順
- 注意文
- 禁止主張
- field-to-engineering feedback

OEMやfleet serviceが持つ範囲:

- severity統合
- action plan
- 顧客通知
- 運行可否の最終判断
- service workflow
- 保証判断

ASAM SOVDはdiagnostic APIとfault information、data access、internal software function controlの方向を示すが、運行判断や安全保証をサプライヤへ渡すものではない。

RDI005の判断:

> Proceed as guardrail。責任境界を切る条件として残す。ここを切れない場合はKill。

## RDI006: 1ケースsample

最初のsampleは、高負荷操舵後のassist limitation / thermal limitがよい。

理由は3つある。

- 旧Kill sampleを再利用できる
- RDI002のdata field不足を具体化できる
- RDI003の既存remote diagnosticsとの差分を比較できる

sampleは4列にする。

| Column | 内容 |
|---|---|
| DTCだけ | fault code、timestamp、system status |
| Existing remote diagnostics | severity、action plan、service routing、parts preparation |
| EPS/SbW internal explanation | assist state、thermal state、motor current、software / calibration ID、追加DID読み順 |
| OEM service note | 入庫優先度、追加診断、注意文、禁止主張 |

RDI006の判断:

> Proceed to sample。次は4列sampleを作る。

## What Changed

調査前:

> Network参加できるかが気になる。

調査後:

> Network参加の入口はある。ただし、openに入れるわけではない。一般APIはDTC / vehicle health中心で、EPS/SbW固有data fieldやservice outcomeは特定OEM program前提になる。

このため、新仮説は残すが、次の門はかなり明確になった。

## Market Demand First

| Field | 内容 |
|---|---|
| Market demand | OEM fleet service / remote diagnosticsでは、DTC後のseverity判断、action plan、service routing、diagnostic time reduction、uptime改善の需要がある。 |
| Evidence signal | GM OnStar API、Smartcar、High Mobilityはvehicle data APIを示す。Bosch、International、Platform Science、Geotabはremote diagnostics workflowを示す。ZFとASAM SOVDはsupplier cloud / diagnostic API方向を示す。 |
| Hypothesis | EPS/SbWサプライヤは、OEM networkに参加し、公開APIではなくprogram-level data fieldを使える場合だけ、component-specific explanationを出せる。 |
| Solution | RDI001〜RDI006のうち、次はRDI006の4列sampleを作り、RDI002/RDI003/RDI005を同時に検証する。 |
| Buyer / user | OEM remote diagnostics、OEM fleet service、service engineering、dealer diagnostic support、EPS/SbW supplier diagnostic engineering / field quality。 |
| Initial artifact | Network participation map、required data field list、difference table、responsibility boundary map、4-column case sample。 |
| Validation method | thermal limit / assist limitation caseで、既存remote diagnosticsとEPS/SbW内部説明の差分を見る。 |
| Kill criteria | open APIのDTCだけ、既存action planと同じ、service outcomeが戻らない、責任境界が切れない。 |

## EPS Supplier Lens

EPS/SbWサプライヤとして売るか:

> まだ売らない。OEM program内contentとして成立するか検証する段階。

EPS/SbWサプライヤとして実施できること:

> EPS/SbW内部データから、既存remote diagnosticsでは出せない状態説明、追加DID読み順、注意文、field-to-engineering feedbackを作る。

EPS/SbWサプライヤとして言ってはいけないこと:

> fleetを直接監視する、走行安全を保証する、交換時期を予測する、root causeを断定する、既存remote diagnosticsを置き換える、とは言わない。

次に見る最小項目:

> thermal limit / assist limitationの4列sample。

## Stop / Continue Judgment

Continue。ただし条件付きである。

RDI001は完全Killではない。
RDI002とRDI004は弱い。
RDI003は既存remote diagnosticsが強く、差分証明が難しい。

したがって、次は広い調査ではなく、RDI006の1ケースsampleを作る。
ここでEPS/SbW内部データにより既存action planと違う説明が出ないなら、この仮説も止める。

## Sources

- GM Fleet OnStar API Services: https://www.gmfleet.com/software/onstar/api-services
- Smartcar real-time vehicle diagnostics: https://smartcar.com/docs/getting-started/guides/real-time-vehicle-diagnostics
- Smartcar Diagnostic Trouble Codes API: https://smartcar.com/docs/api-reference/get-dtcs
- Smartcar System Status API: https://smartcar.com/docs/api-reference/get-system-status
- High Mobility Car Data API: https://www.high-mobility.com/car-data
- Bosch Cloud and Predictive Diagnostics: https://www.bosch-mobility.com/en/solutions/software-and-services/cloud-and-predictive-diagnostics/
- International Advanced Remote Diagnostics: https://www.international.com/services/my-international/advanced-remote-diagnostics
- Platform Science Remote Diagnostics: https://www.platformscience.com/blog/the-power-of-remote-diagnostics-for-fleet-maintenance
- Geotab Remote Diagnostics: https://www.geotab.com/blog/remote-diagnostics/
- Volvo Trucks Remote Diagnostics: https://www.volvotrucks.us/our-difference/uptime-and-connectivity/remote-diagnostics/
- ZF Vehicle Health Monitoring: https://press.zf.com/press/en/releases/release_92162.html
- ASAM SOVD: https://www.asam.net/standards/detail/sovd/
