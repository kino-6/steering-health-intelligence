# MHQ001 最終判断: 外販テーマとしてArchive

## 結論

現時点では、操舵系や車両運動系の状態からfleetの運行可否や点検優先度を判断するテーマは、EPS/SbWサプライヤの外販ビジネスとしては閉じる。

市場の痛みがないからではない。
商用車両群や自動運転車両群では、車両停止、予定外入庫、診断時間、部品準備を減らしたい需要はある。

閉じる理由は別である。
EPS/SbWサプライヤがこの需要を取るには、必要な車両データや整備結果へ触れ、さらに既存remote diagnosticsでは出せない操舵系固有の判断を出す必要がある。
公開情報だけでは、この2つを満たせない。

したがって、このテーマは **外販offerとしてはStop / Archive** とする。
残す価値があるのは、特定OEM programで、既存診断仕様、操舵系状態量、整備判断、顧客説明を短くつなぎ直す短期支援だけである。

## 何を判断しているか

判断しているのは、操舵系の故障予測を売るかではない。

判断しているのは、fleet / OEM service / remote diagnosticsの現場で、EPSやSbWの状態を次のような業務判断へ翻訳できるかである。

- 次の運行に出してよいか
- 先に入庫させるべきか
- 次回点検まで様子見でよいか
- 診断でどのDIDや状態量を先に読むべきか
- 部品や整備士を先に準備すべきか

この翻訳が有償テーマになるには、EPS/SbWサプライヤが既存remote diagnosticsより良い、または既存remote diagnosticsにはない判断を出せる必要がある。

## なぜ止めるか

### 1. データアクセスがOEM / fleet / platform依存である

車両データへアクセスする市場や制度は存在する。
EU Data Actのvehicle data guidance、GM FleetのOnStar API、Smartcar、High Mobilityのような公開情報から、DTCやvehicle health dataをAPIで扱う流れは確認できる。
ZFのvehicle health monitoringは、OEM cloudとsupplier cloudの連携例として強い。

ただし、EPS/SbWサプライヤが本当に必要とする細かいデータは、公開情報だけでは確認できない。

- EPS固有DID
- freeze frame / extended data
- assist state
- limit state
- thermal derate
- motor current
- software / calibration ID
- 整備履歴
- 交換結果
- 再発有無
- 作業時間

これらに触れないなら、サプライヤは「操舵系状態を運行判断へ翻訳する」ことができない。
この時点で、外販テーマとしてはかなり弱い。

### 2. 既存remote diagnosticsがすでに強い

DTCを読み、severityを付け、action planを出し、fleet platformへつなぐところは、既存playerがかなり押さえている。

Boschは、fault description、error code、risk / criticality assessment、recommended next step、fault grouping、component localizationを説明している。
Internationalは、fault code reporting、severity rating、action plan、dealer parts inventory、service center mapping、API connectionを出している。
Geotabは、大量のfault codeを理解し、repair priorityへ変換する必要を説明している。
Volvo、OnStar、Smartcarも、DTC、vehicle health、diagnostic time reduction、API接続を扱っている。

つまり、EPS/SbWサプライヤが「DTCを読んで優先度を付ける」と言うだけでは、既存remote diagnosticsとの差分にならない。

### 3. 1ケースsampleでも、差分は内部データ前提になった

最後のKill確認として、高負荷操舵でEPSがthermal limitまたはassist limitationに入った仮想ケースを置いた。
これは実EPSデータではなく、判断構造を見るためのproxyである。

| 見方 | 分かること | 限界 |
|---|---|---|
| DTCだけ | 警告灯や操舵系/シャシ系DTCから、故障系統やseverityが分かる可能性がある。 | 負荷履歴、assist state、thermal derate、motor current、再発有無、整備結果がないと運行可否は断定できない。 |
| 既存remote diagnostics | severity、action plan、service routing、parts preparation、API連携は扱える可能性がある。 | 操舵系固有のDID読み順やsoftware / calibration接続までは公開情報だけでは不明。 |
| EPS/SbWサプライヤのdomain knowledge | assist state、limit state、thermal state、motor current、HILS/bench知見を使えれば、過負荷一過性か再発懸念かを説明できる可能性がある。 | この価値は内部data field、OEM許可、service outcomeとの接続がある場合だけ成立する。 |

このsampleから分かることは、サプライヤ差分がありうるとしても、それは内部資料と契約がある特定program内でしか証明できないということである。
公開情報だけで外販offerにするには弱い。

詳細は [data/archive/motion_health/motion_health_mhq001_final_kill_check_sample.tsv](../../../data/archive/motion_health/motion_health_mhq001_final_kill_check_sample.tsv) に置いた。

## Market Demand First

| Field | 内容 |
|---|---|
| Market demand | Fleet / AV運用では、車両停止、予定外入庫、診断時間、部品準備が運行効率を落とす。 |
| Evidence signal | Bosch、International、Geotab、Volvo、OnStar、Smartcarはremote diagnosticsをfleet workflowへつないでいる。NexteerとZFはchassis / motion healthをsupplier側の公開signalとして出している。 |
| Hypothesis | EPS/SbWサプライヤは、操舵系状態量を運行可否・点検優先度・診断読み順へ翻訳できる場合だけ価値がある。 |
| Solution | 外販商品化はしない。特定OEM programで再開する場合だけ、DTC、DID、freeze frame、service outcome、既存remote diagnosticsとの差分を1ケースで確認する。 |
| Buyer / user | 外販では明確な初期買い手を置かない。再開時の利用者はOEM fleet service、remote diagnostics、supplier diagnostic engineering / service engineering / field quality。 |
| Why supplier can play | EPS/SbWサプライヤは、assist state、limit state、motor current、thermal state、software/calibration ID、SbW degraded state、bench/HILS知見を理解している可能性がある。 |
| EPS supplier conclusion | 外販テーマとしてはStop / Archive。特定OEM programで内部データと既存診断との差分を確認できる場合だけ短期支援として再開。 |
| Demo | Kill確認sampleとして、DTCだけ、既存remote diagnostics、supplier domain triageの3列比較を作成。 |
| What not to claim | EPS交換時期の予測、保証費削減、root cause断定、安全機能の代替、supplier単独fleet監視、既存remote diagnostics置換、fleet downtime削減断定。 |
| Kill criteria | 必要data fieldに触れない、service outcomeが取れない、既存remote diagnosticsと同じ説明になる、操舵系domain knowledgeなしで判断できる、出力が交換時期予測に戻る。 |

## 判定

| 判定レベル | 結論 |
|---|---|
| 市場需要 | ある。fleet downtime、予定外入庫、診断時間短縮は強い。 |
| 操舵系単独需要 | 弱い。整備・法規・安全の対象ではあるが、独立購買painは未確認。 |
| サプライヤ制御範囲 | 部分的。状態量や設計知見は持てるが、field dataとservice outcomeはOEM/fleet依存。 |
| 既存診断との差分 | 弱い。汎用DTC優先度付けは既存remote diagnosticsが強い。 |
| 外販offer | Stop。 |
| 残す用途 | 特定OEM program内の短期説明支援、診断仕様レビュー、service engineering向け整理。 |

## 再開条件

このテーマを再開してよいのは、以下が同時に見える場合だけである。

- 対象programでEPS/SbWのDTC、DID、freeze frame、extended data、assist state、limit state、software / calibration IDを見られる
- 整備履歴、交換結果、再発有無、作業時間の少なくとも一部へ接続できる
- 既存remote diagnosticsが出すseverity / action planでは足りない操舵系固有の判断がある
- EPS/SbWサプライヤの説明が、OEM fleet serviceまたはservice engineeringの既存成果物へ転記できる
- 「交換時期予測」ではなく、運行可否、入庫優先度、診断読み順、顧客説明のどれかへ落ちる

## EPSサプライヤとしての言い方

EPS/SbWサプライヤとして言えること:

> Fleet downtimeやremote diagnosticsの市場はある。ただし、公開情報だけでは、当社が外販商品として取れる差分は確認できない。価値が残るのは、特定OEM programで、操舵系状態量と既存診断・整備判断をつなぐ短期支援に限られる。

まだ言ってはいけないこと:

> EPSの交換時期が分かる、既存remote diagnosticsを置き換えられる、fleet downtimeを削減できる、root causeを断定できる、安全機能を代替できる、とは言わない。

初期対象外に置くもの:

> OEM fleet platform、汎用remote diagnostics、service network運営、insurance、driver behavior、engine diagnostics、tire-only analytics、fleet全体監視。

次に見せる部署:

> business developmentには見せず、diagnostic engineering、service engineering、field quality、customer technical interfaceへ「外販Stop、特定program内の再開条件」として共有する。

## Chain Of Verification

| Verification question | Evidence | Confidence | Decision impact |
|---|---|---|---|
| fleet downtimeや診断時間短縮の市場需要はあるか | Bosch、International、Geotab、Volvo、OnStar、Smartcar | High | 市場需要は残す |
| EPS/SbWサプライヤが必要データに触れるか | EU Data Act、OnStar API、Smartcar、High Mobility、ZF cloud連携 | Low to Medium | 外販Proceed不可 |
| 既存remote diagnosticsとの差分はあるか | Bosch、International、Geotabがseverity/action plan/APIを扱う | Low to Medium | 汎用DTC優先度付けはStop |
| 1ケースsampleで差分は出たか | thermal limit / assist limitation proxy | Low to Medium | 差分は内部dataとservice outcome前提。公開情報では証明不可 |
| 旧テーマへ戻っていないか | 出力を交換時期予測ではなく運行可否/入庫優先度へ置いた | High | 旧テーマ再提案は回避。ただし外販価値も不足 |

## Sources

- Nexteer, MotionIQ software suite: https://www.nexteer.com/release/nexteer-unveils-its-motioniq-software-suite-for-intelligent-motion-control/
- ZF, Vehicle Health Monitoring: https://press.zf.com/press/en/releases/release_92162.html
- Bosch, Cloud and predictive diagnostics: https://www.bosch-mobility.com/en/solutions/software-and-services/cloud-and-predictive-diagnostics/
- International, Advanced Remote Diagnostics: https://www.international.com/services/my-international/advanced-remote-diagnostics
- Geotab, Remote diagnostics for commercial trucks: https://www.geotab.com/blog/remote-diagnostics/
- Volvo Trucks, Remote Diagnostics: https://www.volvotrucks.us/our-difference/uptime-and-connectivity/remote-diagnostics/
- GM Fleet, OnStar API Services: https://www.gmfleet.com/software/onstar/api-services
- Smartcar, real-time vehicle diagnostics: https://smartcar.com/docs/getting-started/guides/real-time-vehicle-diagnostics
- High Mobility, Car Data API: https://www.high-mobility.com/car-data
- European Commission, Guidance on vehicle data, accompanying the Data Act: https://digital-strategy.ec.europa.eu/en/library/guidance-vehicle-data-accompanying-data-act
- ASAM, SOVD: https://www.asam.net/standards/detail/sovd/
