# RDI006 program gap 穴埋めPDCA

## 結論

穴埋めは完了した。
ただし、これは「事業としてProceedできる」ではない。

分かったことは、EPS/SbWサプライヤの差分はかなり狭いということだ。
DTC、severity、action plan、service routingだけなら、既存の遠隔診断サービスがすでに強い。
差分が出るのは、特定OEM programでEPS/SbW固有のDID、freeze frame、assist / limit state、thermal indicators、software / calibration IDが読めて、さらにservice noteや修理結果へつながる場合だけである。

したがって最終判断は、**Conditional Continue / not offer** である。
外販商品としてはまだ出さない。
次に進めるなら、公開調査ではなく、実programまたは想定programの診断仕様とservice workflowに対してsource-of-truth確認をする。

## 何を判断しているか

ここで判断しているのは、thermal limit / assist limitationの1ケースで、EPS/SbWサプライヤがOEM遠隔診断へ追加できる説明があるかである。

これは次の話ではない。

- fleetを直接監視する
- EPSの交換時期を当てる
- 走行安全を保証する
- root causeを断定する
- 既存remote diagnosticsを置き換える

判断しているのは、OEM remote diagnostics、service engineering、dealer diagnostic supportが既に持つDTC、severity、action planに対して、EPS/SbW側から「追加で読むべき項目」「状態の意味」「言ってはいけないこと」を足せるかである。

## Item Conclusions

詳細TSVは [data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_program_gap_filled.tsv](../../../data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_program_gap_filled.tsv) に置く。

| Item | Conclusion | Confidence | Evidence / assumption | Weak point | Next action |
|---|---|---|---|---|---|
| Readable EPS/SbW DTC | Program-required。操舵系DTCがremote caseまたはservice toolへ出ることが最低条件 | Medium | DTC/APIの存在は公開情報で確認。ただしEPS/SbW固有DTC名はprogram依存 | 汎用system statusしか出ないとStop | 対象programのDTC export項目を確認 |
| Freeze frame / extended data | 最重要Gate。DTC発生時の速度、電圧、温度、電流、操舵負荷がないと差分が弱い | Medium | 公開APIだけでは未確認 | DTC名とtimestampだけならStop | freeze frame / extended dataの読み出し可否を確認 |
| Assist / limit state | 差分の核。limit解除済みか再発ありかで読み順を変えられる | Medium | assist / limit stateは公開情報では未確認 | stateが読めないと既存diagnosticsと同じ | assist / limit state DID候補を確認 |
| Motor current / thermal indicators | thermal caseではCritical寄り。温度と電流がないと過負荷説明が弱い | Medium | 内部値はprogram依存 | 温度・電流が読めない | thermal関連DIDと表示範囲を確認 |
| Software / calibration ID | 補助Gate。状態説明とcalibration確認をつなげられる可能性 | Low to Medium | service workflowへの露出は未確認 | IDがservice workflowへ出ない | software / calibration IDの露出を確認 |
| Existing remote diagnostics action plan | 反証側として強い。既存はseverity/action plan/service routingを扱う | High for public counter-signal | Bosch、International、Platform Science、Geotab等 | 既存action planを見ないと差分比較できない | 既存action plan例を入手 |
| Supplier additional explanation | 条件付きで成立。価値はDTC言い換えではなく、追加DID読み順と禁止主張 | Medium | RDI006 sampleで出力形を作成済み | 説明がDTC descriptionの言い換えならStop | service note文面を作る |
| Service note destination | 事業化Gate。転記先がないと説明が使われない | Low to Medium | 公開workflowはあるが、supplier説明の転記先は未確認 | PDFや内部メモで止まる | service case / worksheet項目を確認 |
| Service outcome feedback | 最強のKill Gate。結果が戻らないと改善loopにならない | Low | fault historyやreportsはあるがsupplierへのfeedbackは未確認 | alertを出すだけで修理結果が戻らない | outcome fieldを確認 |
| Responsibility boundary | Guardrailとして固定。ここを切れないなら即Stop | High | 過去調査とRDI005に基づく | サプライヤが安全保証や交換時期を言う必要が出る | responsibility matrixを作る |

## PDCA

PDCAログは [data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_pdca_log.tsv](../../../data/archive/oem_remote_diagnostics/oem_remote_diagnostics_rdi006_pdca_log.tsv) に置く。

### P1: Unknownを露出する

最初にtemplateをそのまま見た時点では、10項目の多くがUnknownだった。
公開情報で支えられるのは、vehicle data APIや既存remote diagnostics workflowの存在までである。
EPS/SbW固有のDID、freeze frame、assist state、service outcome feedbackは公開情報では埋まらない。

この時点で、仮説は単純なContinueではなくStop寄りに修正した。

### P2: Unknownを必要artifactへ変換する

次に、Unknownを空欄のまま残さず、実programで確認すべきartifactへ変換した。

- DTC list
- freeze frame / extended data record
- assist / limit state DID
- thermal indicator DID
- software / calibration ID
- existing action plan
- service note destination
- service outcome field
- responsibility matrix

これで「何が分かれば進むか」は明確になった。

### P3: 反証で絞る

既存remote diagnosticsはすでに強い。
DTC description、severity、action plan、service routing、parts preparationは既存サービスの主戦場である。

したがって、EPS/SbWサプライヤの追加価値は次に限定した。

- 追加DID読み順
- cool-down後確認
- 再発counter確認
- software / calibration確認
- 禁止主張
- service outcomeを使った診断content改善

この範囲を超えて、運行可否、安全保証、交換判断、root cause断定に踏み込むならStopである。

### P4: 完了判定

全項目について、filled answer、必要artifact、owner、Proceed signal、Kill signalを入れた。
残っているUnknownは、未記入ではなくprogram確認項目として明示した。

よって、穴埋め作業としては完了である。

## Verification Questions

| Question | Answer | Confidence | Impact |
|---|---|---|---|
| 既存remote diagnosticsと同じことを言っていないか | DTC説明、severity、action planだけなら同じ。差分は追加DID読み順と禁止主張に限定した | High | 商品範囲を縮小 |
| 公開APIだけで成立するか | 成立しない。公開APIはDTC / system status / vehicle health中心 | Medium-High | OEM program依存を明記 |
| EPS/SbWサプライヤだけで完結するか | 完結しない。service note、outcome feedback、action planはOEM/service側 | High | supplier boundaryを明記 |
| service outcomeなしで事業化できるか | 弱い。説明を改善できず単発資料になりやすい | Medium | outcome feedbackを最強Gateに設定 |
| 安全保証や交換時期予測に見えないか | 見える危険があるため、禁止主張と責任境界を固定した | High | Guardrailとして残す |

## Market Demand First

| Field | 内容 |
|---|---|
| Market demand | OEM remote diagnosticsやfleet serviceでは、DTC発生後にseverity、action plan、service routing、diagnostic time reductionへつなげる需要がある。 |
| Unresolved pain | 既存remote diagnosticsは強いが、同じDTCの裏にあるEPS/SbW固有のassist制限、温度制限、再発状態、calibration差分までservice noteへ転記できるかは未確認。 |
| Hypothesis | 特定OEM programでEPS/SbW内部data fieldとservice outcomeが使える場合だけ、サプライヤはcomponent-specific explanationを足せる。 |
| Solution | thermal limit / assist limitationケースで、DTC、freeze frame、assist/limit state、thermal indicators、calibration ID、service outcomeの穴埋め表を作る。 |
| Buyer / user | OEM remote diagnostics、service engineering、dealer diagnostic support、EPS/SbW supplier diagnostics、field quality、software/calibration、product engineering。 |
| Initial artifact | program gap filled table、PDCA log、service note sampleの前段確認表。 |
| Validation method | 実programまたは想定programの診断仕様とservice workflowに照らし、各fieldが読めるか、転記先があるか、outcomeが戻るかを見る。 |
| Kill criteria | DTCとsystem statusしかない、既存action planと同じ、service note転記先がない、service outcomeが戻らない、責任境界が切れない。 |

## EPSサプライヤとしての言い方

EPS/SbWサプライヤとして言えること:

> 対象programで操舵系内部data fieldとservice workflowが使える場合、DTC発生時の状態説明、追加DID読み順、注意文、禁止主張をOEM service noteへ渡せる可能性がある。

EPS/SbWサプライヤとして実施できること:

> DTC、freeze frame、assist / limit state、thermal indicators、software / calibration IDを、service engineeringやdealer diagnostic supportが読める確認項目へ整理する。

まだ言ってはいけないこと:

> fleetを直接監視できる、走行安全を保証できる、EPS交換時期を予測できる、root causeを断定できる、既存remote diagnosticsを置き換えられる、とは言わない。

OEM / service領域として残すもの:

> severity統合、action plan、顧客通知、運行可否、保証判断、parts preparation、campaign / OTA判断。

次に見せる部署:

> diagnostics engineering、service engineering、field quality、software/calibration、product engineering、customer technical interface。

## Stop / Continue Judgment

**Conditional Continue / not offer**。

続ける価値はあるが、公開調査を続ける段階ではない。
次に必要なのは、実programまたは想定programのsource-of-truth確認である。

最小確認項目は次の3つでよい。

1. DTC以外に、freeze frame、assist / limit state、thermal indicators、software / calibration IDのどれが読めるか。
2. 既存action planに対して、追加DID読み順や禁止主張を本当に足せるか。
3. service outcome、再発有無、作業時間、dealer commentの一部が戻るか。

この3つのうち2つ以上がNoなら、RDI006もStopでよい。

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
- ZF Vehicle Health Monitoring: https://press.zf.com/press/en/releases/release_92162.html
- ASAM SOVD: https://www.asam.net/standards/detail/sovd/
