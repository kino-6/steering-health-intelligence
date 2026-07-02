# Bosch Predictive Business Analysis

## 結論

Boschの予測ビジネスは、AIモデルだけを売る話ではない。
公開情報から見る限り、車両からデータを取り、クラウドで診断し、部品やシステムの状態を予測し、その結果を整備計画、部品手配、入庫判断、保証判断、品質改善へつなぐ事業である。

Boschが正面から使っている言葉は、`predictive diagnostics`、`predictive maintenance`、`vehicle health` である。
このブランチでは、この言葉を避けずに扱う。

EPSサプライヤ側の論点は、Bosch型のfleet platformを自社で作ることではない。
操舵系について、predictive diagnosticsの対象にできる状態、predictive maintenance actionへつなげられる条件、vehicle health outputとして説明できる範囲を定義できるかである。

現時点の判定は、`Proceed to steering predictive diagnostics screening` である。
売る商品を確定する段階ではないが、Boschが予測保全とvehicle healthを商材化していることは十分強い公開シグナルであり、操舵系でどこまで同じ土俵に乗れるかを調べる価値がある。

ソース別の整理表は [data/bosch_predictive_business_analysis.tsv](../data/bosch_predictive_business_analysis.tsv) に置く。

## 何を判断しているか

判断しているのは、Boschが「予測」と呼んでいる事業の中身である。

具体的には、次を見ている。

1. 誰が何に困っているから予測が必要なのか
2. Boschは何を入力にして、何を出力しているのか
3. 予測結果は、整備、入庫、部品、保証、品質のどの業務へ落ちているのか
4. そのうちEPSサプライヤが持てる手札はどこか
5. 操舵系で言ってよい `predictive diagnostics / predictive maintenance / vehicle health` と、言ってはいけない過剰主張は何か

## Rule Check

今回の判断では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Kaggle / Public Proxy Predictive Value Rule`
5. `Mandatory Rule Check Before Stop / Kill / Archive`

この文書では、Stop / Kill / Archiveを主結論にしていない。
ただし、旧テーマへ戻らないように次を確認する。

- 市場需要から始める
- Boschの予測語を、EPS交換時期予測だけへ狭めない
- EPS内部状態が公開されていないことを主Kill理由にしない
- EPSサプライヤとして売る、実施する、言ってはいけないことへ戻す
- 故障予測、交換時期、保証費削減、root cause断定を未確認のまま言わない
- 次の検証質問を具体的に残す

## 市場需要

fleet operator、mobility provider、OEMは、予期しない車両停止を減らしたい。
車両が止まると、代替車両、緊急整備、部品手配、作業待ち、顧客対応が発生する。
そのため、異常が起きた後にDTCを読むだけではなく、車両や部品の状態を先に把握し、整備や入庫を計画したい需要がある。

Boschはこの需要を、fleet uptime、maintenance cost、vehicle health services、predictive maintenanceとして説明している。
2026年3月19日のUptake買収計画では、AI-driven predictive maintenanceをfleet managementの競争要因と位置づけ、UptakeのAI予測分析、Bosch Connectivity Hub、FleetME ecosystemを組み合わせる意図を示している。

出典:

- Bosch Media Service US, `Bosch strengthens U.S. mobility services portfolio`, 2026-03-19
  <https://us.bosch-press.com/pressportal/us/en/press-release-30080.html>

## Boschの予測ビジネスの構造

### 1. 車両を接続し、必要なデータを取る

Boschのcommercial vehicle向けconnectivity servicesは、remote diagnostics、data acquisition、OTA update、vehicle appsを含む。
公開情報では、車両メーカーが遠隔で車両データや機能へアクセスでき、データ取得はイベント条件やfleet単位で柔軟に構成できると説明されている。

意味:

予測ビジネスの入口は、予測モデルではなく、車両から必要なデータを継続的に取り、クラウドへ渡す仕組みである。
EPSサプライヤが見るべき点は、操舵系でpredictive diagnosticsに必要な信号、DTC、snapshot、発生頻度、制限状態、温度、電源、通信contextを、どの粒度で取得対象にできるかである。

出典:

- Bosch Mobility, `Vehicle connectivity services for commercial vehicle`
  <https://www.bosch-mobility.com/en/solutions/connectivity/vehicle-connectivity-services-cv/>

### 2. 起きた異常をクラウド診断で読める形にする

Boschのcloud diagnosticsは、車両の診断データをクラウドで処理し、fault description、error code、risk and criticality assessment、recommended next stepsを出す。
さらに、faultをvehicle systemやfaulty componentへ割り当て、smallest removable partまでlocalizeする方向で説明されている。

意味:

これは、単なるDTC一覧ではなく、サービス現場が次に何をすべきかへ落とす診断業務である。
EPSサプライヤに置き換えると、操舵系DTC、freeze frame、extended data、limit state、software / calibration IDが、サービス側の読み順や説明にどう使えるかが論点になる。

出典:

- Bosch Mobility, `Cloud and predictive diagnostics`
  <https://www.bosch-mobility.com/en/solutions/software-and-services/cloud-and-predictive-diagnostics/>

### 3. 起きる前の異常、摩耗、状態変化を予測する

Boschのcloud and predictive diagnosticsでは、potential failures and problems before they occur、deep component levelのanomalies and wear、health status、behavior-based failure prediction、component-specific load and diagnostic featuresが出ている。
アルゴリズムは、domain expertise、data science、multiple data sourcesを使うと説明されている。

意味:

ここがこのRepoにとって最も重要である。
Boschは「予測」を、運転行動や負荷、診断特徴、部品知識、複数データ源を組み合わせたvehicle health / predictive maintenanceの業務として扱っている。
操舵系でも同じ構造に乗るなら、まず定義すべきものはsteering predictive stateである。

出典:

- Bosch Mobility, `Cloud and predictive diagnostics`
  <https://www.bosch-mobility.com/en/solutions/software-and-services/cloud-and-predictive-diagnostics/>

### 4. 予測結果を整備計画へ落とす

Boschの`Predictive Diagnostics`ページでは、component and system conditionを監視、評価、報告し、connected vehicle dataとcloud informationに基づいてfaultsを予測すると説明している。
さらに、probable remaining lifetime、maintenance forecast for OEM、driver notification、workshop appointment planningが出ている。

意味:

Boschの予測は、状態スコアで止まらない。
OEMへmaintenance forecastを送り、driverへ通知し、workshop appointmentへつなげる。
EPSサプライヤが同じ言葉を使うなら、操舵系の予測結果が、どの整備行動、入庫優先度、診断読み順、部品手配、顧客説明へつながるのかを示す必要がある。

出典:

- Bosch Mobility, `Predictive Diagnostics`
  <https://www.bosch-mobility.com/en/solutions/diagnostics/predictive-diagnostics/>

### 5. OEM向けには保証・品質・platform影響へ広がる

Boschのdata-driven intelligenceでは、engineering、manufacturing、operationのlife cycle dataを、domain knowledge、semantics、digital twins、AIと組み合わせる。
公開情報では、early warning、warranty indication、remote state of health、myFleetが説明されている。
myFleetでは、vehicle health monitoring and predictive maintenance、remaining lifetime、recommended date to replace the componentまで出ている。

意味:

Boschの予測ビジネスは、fleet整備だけでなく、OEMの保証判断、field quality issue、platform影響把握にも接続している。
EPSサプライヤにとっては、操舵系のvehicle health outputが、品質改善、保証判断、field-to-engineering feedbackへ転記できるかが論点になる。
ただし、公開情報だけで操舵系のremaining lifetimeや交換推奨日をBoschが明示しているとは言えない。

出典:

- Bosch Mobility, `Data-driven intelligence`
  <https://www.bosch-mobility.com/en/solutions/software-and-services/data-driven-intelligence/>

### 6. Uptake買収計画は、予測保全を実ビジネスとして強めるシグナル

Boschは2026年3月、Uptake Technologiesの買収計画を発表した。
Uptakeはcommercial fleets向けのAI-based predictive analyticsを扱う会社として説明されている。
Boschは、UptakeのAI-driven predictive maintenance、Bosch Connectivity Hub、FleetME ecosystemを組み合わせ、end-to-end solutionを目指すと説明している。

意味:

これは、Boschが予測保全を実ビジネスとして強めているシグナルである。
EPSサプライヤにとっては、platformを自前で再現するよりも、操舵系のdomain content、predictive state、diagnostic meaning、maintenance action mappingを準備する方が現実的である。

出典:

- Bosch Media Service US, `Bosch strengthens U.S. mobility services portfolio`, 2026-03-19
  <https://us.bosch-press.com/pressportal/us/en/press-release-30080.html>

### 7. 縦型事例では、battery、brake、powertrainが先に見える

Boschのbattery in the cloudは、battery state of health、stress factors、long-term forecast、anomaly detection、maintenance decisionsを扱う。
brake pad wear sensorは、remaining pad lifeとreplacement timingを扱う。
lifecycle powertrain servicesは、powertrainのremote state of health、remaining service life、diagnostics / maintenance / repair recommendationを扱う。

意味:

Boschは、部品やsystemごとに、測れる状態、劣化モデル、診断特徴、整備行動を組み合わせている。
操舵系で同じことを言うには、batteryやbrake padのように「摩耗量が直接分かる」部品と同じ扱いにしてはいけない。
操舵系では、まずpredictive stateとmaintenance actionの関係を慎重に切る必要がある。

出典:

- Bosch Mobility, `Battery in the cloud insights`
  <https://www.bosch-mobility.com/en/solutions/software-and-services/battery-in-the-cloud/battery-in-the-cloud-insights/>
- Bosch Mobility, `Brake pad wear sensor`
  <https://www.bosch-mobility.com/en/solutions/sensors/brake-pad-wear-sensor/>
- Bosch Mobility, `Lifecycle powertrain services`
  <https://www.bosch-mobility.com/en/solutions/software-and-services/lifecycle-powertrain-services/>

## Bosch型予測ビジネスの層

| 層 | 自然言語での意味 | Bosch公開情報で見えるもの | EPSサプライヤ側の論点 |
|---|---|---|---|
| 接続 | 車両から必要なデータを取る | connectivity services、remote diagnostics、data acquisition | 操舵系でどの信号とevent snapshotが必要か |
| 診断 | 起きた異常をサービス行動へ変える | fault description、criticality、next steps、component localization | DTC / freeze frame / extended dataをどう読ませるか |
| 予測 | 起きる前の状態変化を読む | anomalies、wear、behavior-based failure prediction、remaining lifetime | steering predictive stateを定義できるか |
| 業務化 | 予測を整備・入庫・部品へ落とす | maintenance forecast、driver notification、workshop appointment | どのpredictive maintenance actionへつなげるか |
| 品質・保証 | field dataを保証判断や品質改善へ返す | warranty indication、early warning、digital twins、myFleet | vehicle health outputを品質改善へ転記できるか |
| ecosystem | fleet/OEM向けに販売・運用する | C-Hub、FleetME、Uptake AI | EPSサプライヤ単独platformではなくdomain contentを持てるか |

## EPSサプライヤとしての結論

EPSサプライヤが初期に売る候補は、Bosch型platformそのものではない。
初期候補は、操舵系をpredictive diagnostics / predictive maintenance / vehicle healthの対象として扱えるかを確認する短期assessmentである。

自然言語で言うと、次の仕事である。

> 操舵系について、どの状態なら予測診断の対象にでき、どの整備行動へつながり、どこから先は残寿命・交換時期・安全保証・原因断定と言ってはいけないかを整理する。

この仕事を `Steering predictive diagnostics screening` と呼ぶなら、初期成果物は次になる。

1. 操舵系predictive state候補表
2. 各stateに必要なDTC、freeze frame、extended data、制御制限、温度、電源、通信context
3. predictive maintenance actionへの接続表
4. vehicle health outputとして説明できる文言
5. remaining lifetime、replacement date、failure predictionを言ってよい条件と言ってはいけない条件
6. repair feedback loopが必要な項目と、feedbackなしでも言える項目の切り分け

## まだ分からないこと

公開情報だけでは、次は分からない。

1. Bosch Predictive Diagnosticsが、steering / EPS / SbWを対象componentとして明示しているか
2. Boschが操舵系のremaining lifetimeやreplacement dateを公開情報で語っているか
3. EPSサプライヤが、OEM/fleetのrepair feedback loopへどの条件で接続できるか
4. 操舵系predictive stateが、既存DTCやservice manualを超える価値を持つか
5. OEMやfleetが、操舵系のvehicle health outputに独立した価値を感じるか

## 判定

現時点では、`Proceed to steering predictive diagnostics screening` とする。

理由は次である。

1. Boschは、predictive diagnostics / predictive maintenance / vehicle healthを公開商材として明確に扱っている
2. 予測の入力として、component-specific load and diagnostic features、domain expertise、multiple data sourcesが出ている
3. 出力は、remaining lifetime、maintenance forecast、workshop appointment、warranty indication、field qualityへ広がっている
4. Uptake買収計画により、fleet/OEM向けAI予測保全を実ビジネスとして強化する方向が見える
5. EPSサプライヤはplatformを持たなくても、操舵系のdomain contentと説明境界を持てる可能性がある

ただし、これは外販商品Proceedではない。
次に見るべきは、操舵系で本当にpredictive stateが切れるかである。

## CoVe

| Verification question | Evidence | Confidence | Impact |
|---|---|---|---|
| Boschは予測保全を本当に商材として出しているか | Predictive Diagnostics、Cloud and predictive diagnostics、Data-driven intelligence、Uptake買収計画 | High | 予測語を正面から扱う |
| 出力は業務actionへ落ちているか | maintenance forecast、driver notification、workshop appointment、warranty indication、myFleet | High | AIモデル単体ではなく業務パッケージとして整理する |
| remaining lifetimeやreplacement dateまで言っているか | Predictive DiagnosticsとData-driven intelligenceで明記 | High | Boschレベルの予測範囲として扱う |
| steering / EPS / SbWが対象と明示されているか | 今回見た公開情報では確認できない | Unknown | EPS固有のRULや交換推奨日は主張しない |
| EPSサプライヤが単独platformを売れるか | Boschはconnectivity、cloud、FleetME、Uptakeを束ねている | Low | platform外販ではなくdomain content / screeningへ絞る |
| battery / brake padのRULを操舵へ転用できるか | batteryやbrakeは測れる劣化状態が比較的明確 | Medium | 操舵では同じ強さのRUL主張を避ける |

## EPSサプライヤとして言えること

Boschは、接続、クラウド診断、component-specific load and diagnostic features、domain expertise、AI、digital twin、fleet/OEM workflowを組み合わせ、predictive diagnostics / predictive maintenance / vehicle healthを商材化している。

EPSサプライヤは、操舵系について次を準備する価値がある。

1. steering predictive state
2. steering predictive diagnosticsで使う診断・制御・環境context
3. predictive maintenance actionへの接続
4. vehicle health outputとしての説明文
5. remaining lifetime / replacement date / failure predictionと言ってよい条件と言ってはいけない条件

## まだ言ってはいけないこと

次は言ってはいけない。

1. Boschが操舵系EPSのremaining lifetimeやreplacement dateを公開情報で確認済みである
2. EPSサプライヤがBosch型fleet platformを単独で売れる
3. steering predictive stateだけで安全保証、root cause、保証費削減を断定できる
4. batteryやbrake padのRUL事例を、そのままEPSへ転用できる
5. 公開proxyだけでEPS交換時期予測ができる

## 次の検証質問

次に見るべき最小質問は、次である。

1. 操舵系で、predictive diagnosticsの対象にできるstateは何か
2. 各stateは、DTC、freeze frame、extended data、limit state、温度、電源、通信contextのどれで説明できるか
3. 各stateは、どのpredictive maintenance actionへつながるか
4. vehicle health outputとして、サービス現場やOEMに何を言えるか
5. remaining lifetime、replacement date、failure predictionと言うには何が追加で必要か
6. repair feedback loopがないと成立しないstateはどれか
