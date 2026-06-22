# MHQ004 / MHQ007 / MHQ008 追加深掘り

## 結論

MHQ004、MHQ007、MHQ008は、外販テーマとしては残さない。
ただし、Archive時に捨てる知見でもない。

この3つは、将来、特定OEM programで内部データや整備結果を見られる場合にだけ、再開条件として使える。

- MHQ004は、何を出力すべきかを決める判断軸として残す
- MHQ007は、操舵系を単独で見ないための市場理解として残す
- MHQ008は、EPS/SbWサプライヤ内の品質・開発への戻しとして残す

ただし、いずれも公開情報だけで外販商品にするには足りない。
理由は、価値ある出力やbundleの方向性は既存remote diagnostics、OEM service、広いTier1、fleet platformの領域にすでに入っているためである。

## Item Conclusions

| Item | 判断 | Confidence | 残す価値 | 外販にしない理由 |
|---|---|---|---|---|
| MHQ004 | Hold as output rubric / Archive | High for workflow, Low for standalone supplier offer | 運行可否、入庫優先度、診断読み順、部品準備、品質feedbackの出力型 | Bosch、International、Platform Science、ZFがrisk、action plan、parts、service alertsを既に扱う |
| MHQ007 | Hold as market architecture / Archive | High for bundle direction, Low for EPS-only offer | steering単独ではなくmotion/chassis bundleで見る市場理解 | bundle化するとOEM、広いTier1、fleet platformの主語になり、EPS単独価値が薄まる |
| MHQ008 | Hold as internal value / Archive | Medium-High for internal value, Low for external offer | 実使用条件を品質・開発・評価条件へ戻すPDCA | service outcome、設計変更、品質会議体に接続しないと価値証明できない |

## MHQ004: 出力は正しい。ただし既存診断が強い

価値ある出力は、EPS交換時期ではない。

現場で使える出力は、次のような判断である。

- 次の運行に出してよいか
- 先に入庫させるべきか
- 次回点検まで様子見でよいか
- どのDIDや状態量を先に読むべきか
- 部品や整備士を先に準備すべきか
- 品質・設計側に戻すべき実使用条件は何か

ここまでは正しい。
Bosch、International、Geotab、Platform Science、ZFの公開情報でも、risk / criticality、severity、action plan、parts inventory、effect on vehicle、service alerts、fleet uptimeが繰り返し出る。

しかし、これは同時に反証でもある。
既存remote diagnosticsが、すでにかなり近い出力を持っている。

EPS/SbWサプライヤが残れるのは、一般的なDTC優先度付けではない。
操舵系固有のDID読み順、assist state、thermal derate、software / calibration ID、SbW degraded stateが、既存remote diagnosticsでは出せない判断に変わる場合だけである。

### MHQ004の再開条件

再開してよいのは、次が確認できる場合だけである。

- 既存remote diagnosticsのaction planでは運行可否や診断読み順を決められない
- EPS/SbW固有のDTC、DID、freeze frame、assist state、thermal state、software / calibration IDが見られる
- その情報から、運行可否、入庫優先度、診断読み順、品質feedbackのどれかに落とせる
- 出力が「交換時期予測」に戻らない

## MHQ007: bundle方向は正しい。ただしEPS単独ではない

操舵系だけを見るより、ブレーキ、足回り、タイヤ、駆動系、通信と一緒に見る方が市場文脈に合う。

Nexteer MotionIQ/Healthは、steering、chassis components、tiresをまとめてfleet downtimeやmaintenance schedulingへつないでいる。
NexteerのVehicle Health ManagementやTire Health Detectionも、fleet downtimeやtire lifecycle dataを扱っている。
ZFのVehicle Health Monitoringは、chassisやdrive trainのtechnical conditionを見て、breakdown予測やrepair recommendationへつなげる。
ZFのVehicle Healthも、engine、braking systems、tire pressureなどをまとめて見ている。

したがって、MHQ007の答えはYesである。
しかし、このYesはEPS/SbWサプライヤ外販テーマを救わない。

束ねるほど、主語はOEM、広いTier1、fleet platform、remote diagnostics platformになる。
EPS/SbWサプライヤは、bundle ownerではなく、操舵系signalのcontributorになる。

### MHQ007の再開条件

再開してよいのは、次が確認できる場合だけである。

- OEMまたはfleet側に、すでにmotion / chassis health bundleがある
- その中で、EPS/SbWサプライヤに操舵系signalの意味づけが求められている
- supplier-owned signal、OEM-owned signal、fleet/platform-owned signalを分けられる
- EPS/SbWサプライヤが言えることと言ってはいけないことを整理できる

## MHQ008: 3つの中では最も内部価値が残る

MHQ004、MHQ007、MHQ008の中で、EPS/SbWサプライヤ内に最も価値が残りそうなのはMHQ008である。

Nexteerは、actual lifecycle conditionsからOEMやsupplierのproduct quality / development insightを得ると説明している。
ZFも、non-personalized dataを使い、OEM cloudとZF cloudのデータ交換を行い、厳しい使われ方によるstress peaksを早期検知する文脈を示している。

これは外販商品ではない。
しかし、supplier内部のquality、product engineering、validation、field qualityには価値がある。

使い方は、たとえば次のようなものになる。

- 実使用条件からstress profileを作る
- bench / HILS / durability条件へ戻す
- software / calibration変更の影響を見る
- field quality会議で、原因断定ではなく確認済み事実として使う
- 次programの設計レビュー質問へ戻す

ただし、ここでも制約は強い。
service outcome、整備履歴、交換結果、再発有無、内部品質課題に接続しなければ、価値を証明できない。
保証費削減やroot cause断定を言うと、旧テーマに戻る。

### MHQ008の再開条件

再開してよいのは、次が確認できる場合だけである。

- 実使用条件を、対象EPS/SbWの設計・評価・品質会議体へ戻す場がある
- service outcomeまたはfield quality eventと接続できる
- 出力が、保証費削減ではなく、stress profile、retest condition、validation feedback、design review inputになる
- 既存品質・評価業務に同じ成果物がない、または不足欄が明確である

## Market Demand First

| Field | 内容 |
|---|---|
| Market demand | Fleet / OEM service / remote diagnosticsでは、運行可否、入庫優先度、部品準備、車両状態の統合把握、実使用条件からの改善が求められる。 |
| Evidence signal | Bosch、International、Platform Science、ZF、Nexteerがremote diagnostics、action plan、service alerts、motion/chassis health、actual lifecycle dataを説明している。 |
| Hypothesis | EPS/SbWサプライヤが価値を持てるのは、操舵系状態量を既存diagnosticsでは出せない判断、または内部品質・開発feedbackへ翻訳できる場合だけである。 |
| Solution | 外販商品化はしない。MHQ004をoutput rubric、MHQ007をbundle boundary map、MHQ008をfield-to-engineering feedback条件として保存する。 |
| Buyer / user | 外販では置かない。再開時だけ、OEM service、remote diagnostics、supplier diagnostic engineering、service engineering、field quality、product engineering。 |
| Initial artifact | 3-item reopening checklist、supplier-owned contribution map、field-to-engineering feedback template。 |
| Validation method | 実DTC/DID/freeze frame/service outcomeと既存remote diagnostics出力を比較し、supplierにしか出せない判断があるかを見る。 |
| Kill criteria | 既存remote diagnosticsで十分、bundle ownerがOEM/platform、service outcomeがない、品質・評価会議体へ転記できない、交換時期予測や保証費削減に戻る。 |

## EPS Supplier Lens

EPS/SbWサプライヤとして売るか:

> 売らない。

EPS/SbWサプライヤとして実施できること:

> 特定OEM programで、操舵系状態量を運行・診断・品質feedbackへ翻訳する短期支援だけである。

EPS/SbWサプライヤとして言えること:

> 運行可否や入庫優先度の出力型、motion/chassis bundle内での操舵系contribution、実使用条件からの品質・開発feedbackは、再開時の評価軸として有用である。

まだ言ってはいけないこと:

> 既存remote diagnosticsを置き換えられる、fleet downtimeを削減できる、EPS交換時期が分かる、保証費を削減できる、root causeを断定できる、とは言わない。

## Chain Of Verification

| Verification question | Evidence | Confidence | Impact |
|---|---|---|---|
| MHQ004の出力型は市場で支持されるか | Bosch、International、Platform Science、ZFがrisk/action plan/parts/service alertsを扱う | High | 出力型は残す |
| MHQ004は外販価値になるか | 既存remote diagnosticsが近い出力を持つ | Low | 外販にはしない |
| MHQ007のbundle方向は妥当か | Nexteer MotionIQ/Health、Nexteer VHM、ZF VHM、ZF Vehicle Health | High | 市場理解として残す |
| MHQ007はEPS単独offerになるか | bundle ownerはOEM/Tier1/platformに寄る | Low | supplier contributionに限定 |
| MHQ008は内部価値があるか | Nexteer actual lifecycle conditions、ZF non-personalized data / cloud exchange | Medium-High | internal quality/product engineering用途として残す |
| MHQ008は外販価値になるか | service outcomeや内部品質課題なしでは証明できない | Low | 外販にはしない |

## Stop / Continue Judgment

MHQ004、MHQ007、MHQ008は、外販テーマとしては閉じる。

ただし、再開条件としては保存する。
次にこの方向を開くなら、新しい市場調査ではなく、特定OEM programの内部資料を前提に、次の3点だけを見る。

1. 既存remote diagnosticsでは出せない操舵系判断があるか
2. motion/chassis bundle内でEPS/SbWサプライヤが持つべきsignal contributionがあるか
3. 実使用条件を品質・開発・評価へ戻す会議体や成果物があるか

この3点がなければ、再開しない。

## Sources

- Bosch Cloud and Predictive Diagnostics: https://www.bosch-mobility.com/en/solutions/software-and-services/cloud-and-predictive-diagnostics/
- International Advanced Remote Diagnostics: https://www.international.com/services/my-international/advanced-remote-diagnostics
- Platform Science Remote Diagnostics: https://www.platformscience.com/blog/the-power-of-remote-diagnostics-for-fleet-maintenance
- ZF Fleet Management Solutions / uptime: https://www.zf.com/products/en/cv/ind/news/maximize_profitability__minimize_tco_with_zf_s_connectivity_solutions/uptime_fms.html
- Nexteer MotionIQ software suite: https://www.nexteer.com/release/nexteer-unveils-its-motioniq-software-suite-for-intelligent-motion-control/
- Nexteer Vehicle Health Management: https://www.nexteer.com/software/vehicle-health-management/
- Nexteer Tire Health Detection: https://www.nexteer.com/software/tire-health-detection/
- ZF Vehicle Health Monitoring: https://press.zf.com/press/en/releases/release_92162.html
- ZF Vehicle Health: https://www.zf.com/products/en/cv/campaigns/bus_connect/stories/vehicle_health/vehicle_health.html
