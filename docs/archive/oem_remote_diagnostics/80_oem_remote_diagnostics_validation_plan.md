# OEM遠隔診断に組み込む操舵系状態説明レイヤー 検証計画

## 結論

次は、仮説を6つの調査アイテムに分けて検証する。

最初に見るべきは、EPS/SbWサプライヤがOEM remote diagnostics networkに参加できるかである。
ここでいう参加とは、サプライヤがfleetを直接監視することではない。
OEMの遠隔診断、fleet service、service engineeringの既存導線に、EPS/SbW内部データ由来の説明コンテンツを流せるかという意味である。

現時点の見立ては、**可能性はあるが、openに参加できるものではない** である。
GM FleetのOnStar API、Smartcar、High Mobilityのようなvehicle data APIは存在する。
InternationalやBoschのように、fault code、severity、action plan、API連携をfleet workflowへつなぐ例もある。
ZFのVehicle Health Monitoringは、OEM cloudとsupplier cloudの連携例として参考になる。

ただし、公開APIで見えるのはDTC、system status、vehicle health、odometer、tire pressureのような上位データが中心である。
EPS/SbW固有のDID、freeze frame、assist state、thermal state、motor current、software / calibration ID、service outcomeが扱えるかは未確認である。

したがって、検証の最初の門はこれである。

> OEM programまたはapproved provider経路で、EPS/SbW固有データと説明コンテンツをremote diagnostics workflowへ流せるか。

## 調査アイテム

詳細TSVは [data/archive/oem_remote_diagnostics/oem_remote_diagnostics_validation_items.tsv](../../../data/archive/oem_remote_diagnostics/oem_remote_diagnostics_validation_items.tsv) に置く。

| Item | 何を確認するか | 現時点の見立て | 判断への影響 |
|---|---|---|---|
| RDI001 | Network参加経路 | 可能性はあるが、OEM program、approved provider、cloud-to-cloud契約依存 | 最初のKill gate |
| RDI002 | EPS/SbW固有data field | 公開APIはDTC/system status中心で、DIDや内部状態量は未確認 | 差分の源泉 |
| RDI003 | 既存remote diagnosticsとの差分 | 既存はseverity/action planが強い。差分は操舵系内部状態説明に限定 | value proposition |
| RDI004 | service outcome feedback | 公開APIでは弱い。OEM service networkやprogram内なら可能性 | 改善loopと品質feedback |
| RDI005 | 責任境界 | 診断・整備判断支援なら可能。安全保証や走行可否断定は不可 | 禁止主張 |
| RDI006 | 1ケースsample | thermal limit / assist limitationから始める | 仮説を具体化 |

## RDI001: Network参加経路

### 確認すること

EPS/SbWサプライヤがOEM remote diagnostics networkへ入る経路を、次の4つに分ける。

| 経路 | 内容 | 可能性 | 注意点 |
|---|---|---|---|
| OEM direct program | OEMのremote diagnostics / fleet service programに、サプライヤ説明contentを入れる | 最も現実的 | 特定programが必要 |
| approved provider / API | OnStar、Smartcar、High MobilityのようなAPI経由でvehicle health / DTCを扱う | 一般dataには可能性 | EPS/SbW固有data fieldは未確認 |
| supplier cloud-to-cloud | ZF VHMのようにOEM cloudとsupplier cloudでデータ交換する | supplier側の参考例あり | OEM partnership前提 |
| standard/API layer | SOVDのような診断API標準に説明contentを載せる | 技術方向として参考 | platform自体は既存標準領域 |

### 初期判断

Network参加は不可能ではない。
ただし、誰でも入れるopen networkではない。

成立するのは、次のいずれかである。

- OEM programでEPS/SbWサプライヤの説明contentが必要になる
- OEM APIやapproved provider経由で必要data fieldを扱える
- OEM cloudとsupplier cloudの契約連携がある
- SOVDなどの診断APIに、EPS/SbW診断コンテンツを載せる役割がある

逆に、一般的なDTC APIだけなら不足である。

## RDI002: 必要data field

### 確認すること

説明レイヤーに必要なdata fieldを、3段階に分ける。

| Level | Data | 判断 |
|---|---|---|
| Minimum | EPS/SbW DTC、system status | 既存remote diagnosticsでも扱いやすい。差分は弱い |
| Useful | DID、freeze frame、extended data、software / calibration ID | 説明差分が出始める |
| Strong | assist state、limit state、thermal state、motor current、voltage、communication state、service outcome | EPS/SbWサプライヤ固有価値の核 |

### 初期判断

公開APIではMinimumが中心に見える。
Useful / Strongに届くかは、特定OEM programで確認する必要がある。

## RDI003: 既存remote diagnosticsとの差分

### 確認すること

既存remote diagnosticsがすでに持つ出力と、EPS/SbWサプライヤが追加できる出力を分ける。

| 既存remote diagnosticsで見えるもの | EPS/SbW説明レイヤーで追加したいもの |
|---|---|
| DTC description | DTC発生時のassist / thermal / limit stateの意味 |
| severity | EPS/SbW固有の注意文 |
| action plan | 追加で読むべきDID順 |
| service routing | 入庫前に確認すべきsoftware / calibration ID |
| parts preparation | 過負荷一過性か再発懸念かの切り分け材料 |

### 初期判断

差分は「DTCを分かりやすくする」では出ない。
差分が出るのは、EPS内部状態量が既存action planの判断を変える場合だけである。

## RDI004: service outcome feedback

### 確認すること

説明が出しっぱなしでは、EPS/SbWサプライヤの品質・開発feedbackにならない。

必要なのは次である。

- 整備結果
- 交換結果
- 再発有無
- 作業時間
- parts usage
- dealer comment

### 初期判断

公開APIでは弱い。
OEM service networkまたは特定program内なら可能性がある。

このfeedbackがない場合、説明レイヤーは「それっぽい説明」から改善できない。

## RDI005: 責任境界

### 確認すること

EPS/SbWサプライヤが背負えるのは、操舵系状態説明と追加診断提案である。
背負えないのは、運行可否の最終判断、走行安全保証、root cause断定、交換時期断定である。

| 誰が持つか | 範囲 |
|---|---|
| EPS/SbWサプライヤ | 状態説明、追加DID読み順、注意文、禁止主張、field-to-engineering feedback |
| OEM remote diagnostics | severity統合、action plan、service workflow、顧客向け文言 |
| fleet / service network | 運行判断、入庫判断、作業実施 |

### 初期判断

ここを切れない場合は止める。
安全保証に見えると、EPS/SbWサプライヤの部品境界を超える。

## RDI006: 最初の1ケースsample

### 推奨ケース

最初は、次のケースがよい。

> 高負荷操舵後にEPS/SbWがassist limitationまたはthermal limitに入ったケース。

理由は、旧motion healthのKill sampleを流用でき、DTCだけ、既存remote diagnostics、EPS内部説明、OEM service noteの4列比較にしやすいためである。

### sampleで見ること

| 列 | 確認すること |
|---|---|
| DTCだけ | 最低限のfault情報 |
| 既存remote diagnostics | severity、action plan、service routing |
| EPS/SbW内部説明 | assist state、thermal state、motor current、software / calibration ID、追加DID読み順 |
| OEM service note | 入庫優先度、追加診断、注意文、言ってはいけないこと |

ここで差分が出なければ、この仮説も止める。

## Market Demand First

| Field | 内容 |
|---|---|
| Market demand | OEM fleet service / remote diagnosticsでは、DTCを受けた後に、severity、action plan、service routing、diagnostic time reductionへつなげる需要がある。 |
| Evidence signal | OnStar、Smartcar、High Mobilityはvehicle data APIを示し、Bosch、International、Geotab、Platform Scienceはremote diagnostics workflowを示し、ZFはOEM cloud / supplier cloud連携を示す。 |
| Hypothesis | EPS/SbWサプライヤは、OEM networkに参加し、EPS内部データからcomponent-specific explanationを生成できる場合だけ価値がある。 |
| Solution | RDI001〜RDI006を順に検証し、最初はthermal limit / assist limitationの1ケースsampleを作る。 |
| Buyer / user | OEM fleet service、OEM remote diagnostics、service engineering、dealer diagnostic support、EPS/SbW supplier diagnostics / field quality / product engineering。 |
| Initial artifact | Network participation map、required data field list、difference table、responsibility boundary map、1-case explanation sample。 |
| Validation method | 既存remote diagnosticsで出せる説明と、EPS/SbW内部データで追加できる説明を1ケースで比較する。 |
| Kill criteria | network参加経路なし、EPS/SbW固有data fieldなし、既存action planと同じ、service outcomeなし、責任境界が切れない。 |

## EPSサプライヤとしての言い方

EPS/SbWサプライヤとして売るか:

> まだ売らない。まずOEM program内contentとして成立するか検証する。

EPS/SbWサプライヤとして実施できること:

> EPS/SbW内部データから、既存remote diagnosticsでは出せない状態説明、追加DID読み順、注意文、field-to-engineering feedbackを作る。

EPS/SbWサプライヤとして言ってはいけないこと:

> fleetを直接監視する、走行安全を保証する、交換時期を予測する、root causeを断定する、既存remote diagnosticsを置き換える、とは言わない。

次に見せる部署:

> diagnostic engineering、service engineering、field quality、software/calibration、product engineering、customer technical interface。

## Sources

- GM Fleet OnStar API Services: https://www.gmfleet.com/software/onstar/api-services
- Smartcar real-time vehicle diagnostics: https://smartcar.com/docs/getting-started/guides/real-time-vehicle-diagnostics
- Smartcar Diagnostic Trouble Codes API: https://smartcar.com/docs/api-reference/get-dtcs
- Smartcar System Status API: https://smartcar.com/docs/api-reference/get-system-status
- High Mobility connected car data: https://www.high-mobility.com/
- Bosch Cloud and Predictive Diagnostics: https://www.bosch-mobility.com/en/solutions/software-and-services/cloud-and-predictive-diagnostics/
- International Advanced Remote Diagnostics: https://www.international.com/services/my-international/advanced-remote-diagnostics
- Platform Science Remote Diagnostics: https://www.platformscience.com/blog/the-power-of-remote-diagnostics-for-fleet-maintenance
- ZF Vehicle Health Monitoring: https://press.zf.com/press/en/releases/release_92162.html
- ASAM SOVD: https://www.asam.net/standards/detail/sovd/
