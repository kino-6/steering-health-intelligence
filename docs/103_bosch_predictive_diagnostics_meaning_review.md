# Bosch Predictive Diagnostics Meaning Review

## 結論

Boschが2026年に強く出している「予測」は、EPS単体の故障予測ではない。
中心は、connected vehicle、cloud、fleet operation、component-specific load and diagnostic features、修理結果のfeedback loopを使い、車両や部品の状態、故障前兆、整備タイミング、部品手配、入庫計画を先に判断することである。

したがって、このRepoで戻すべき本線は、次である。

> EPSサプライヤが、自社の操舵系を「予測診断で扱える部品」として説明するには、何を予測価値として言えて、何を言ってはいけないかを定義する。

これは「公開proxyだけでEPS交換時期を当てる」話ではない。
また、EPSサプライヤがfleet predictive maintenance platformを単独で売る話でもない。

ビジネス候補は、`Steering Predictive Diagnostics Readiness Pack` と呼ぶ前に、自然言語では次の仕事である。

> 操舵系について、故障前に何を早く知れると価値があり、それを既存の制御・診断・品質・サービス情報でどこまで説明できるかを整理する短期assessment。

ソース別の作業表は [data/bosch_predictive_diagnostics_meaning_review.tsv](../data/bosch_predictive_diagnostics_meaning_review.tsv) に置く。

## 何を判断しているか

判断しているのは、Boschが言う「予測」が何を予測しているのかである。

今回見るべき予測は、3種類に分かれる。

1. fleetやOEMが、故障前に整備・部品・入庫を計画するための予測
2. connected vehicle dataとcloudを使い、component / system conditionを評価する予測
3. AI cockpitやADASのように、運転者の意図や運転戦略を先読みする予測

このRepoに関係が強いのは、1と2である。
3はBoschのAI公開情報として重要だが、EPSサプライヤの予測診断ビジネスに直結させない。

## Rule Check

今回の判断では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Kaggle / Public Proxy Predictive Value Rule`
5. `OEM Usage Translation Rule`
6. `Mandatory Rule Check Before Stop / Kill / Archive`

この文書では、StopやArchiveを出していない。
ただし、過去に禁止した旧ロジックへ戻らないため、次を確認する。

- 予測を、EPS単体の交換時期や残寿命を公開proxyだけで当てる話にしない
- Boschのfleet / cloud / predictive diagnosticsを、EPSサプライヤ単独の外販platformと混同しない
- 内部DTCやfreeze frameが見えないことを、この方向の主Kill理由にしない
- 代わりに、操舵系として予測価値に変えられる状態説明、注意状態、点検優先度、診断読み順を定義できるかを見る
- safety guarantee、root cause断定、保証費削減断定を言わない

## 市場需要

fleet operator、mobility provider、OEMは、車両が止まる前に整備を計画したい。
予期しない故障、緊急入庫、部品手配遅れ、車両稼働率低下は、運用コストに直結する。

Boschの2026年3月19日の発表では、Uptake Technologiesの買収計画について、AI-driven predictive maintenanceがfleet managementの競争要因になっていると説明している。
Boschは、UptakeのAI-based predictive analyticsを、自社のvehicle health servicesやfleet servicesへ取り込む意図を示している。

出典:

- Bosch Media Service US, `Bosch strengthens U.S. mobility services portfolio`, 2026-03-19
  <https://us.bosch-press.com/pressportal/us/en/press-release-30080.html>

## Boschが言う予測の中身

### 1. 故障前に整備行動を決める予測

Bosch / Uptakeの2026年発表では、fleetのdowntime、maintenance cost、vehicle uptimeが主語になっている。
予測の出力は、単なるスコアではない。
severity、cost impact、parts planning、maintenance workflowへつながるactionable insightとして説明されている。
また、completed repairsからのclosed feedback loopで精度を強化する、と説明されている。

意味:

これは、EPSサプライヤ単独のモデルではなく、fleet運用、修理結果、部品手配、整備workflowまで含む運用側の予測である。

### 2. 車両内のcomponent / system conditionを監視・評価・報告する予測

Bosch Mobilityの`Predictive Diagnostics`ページでは、connected vehicle dataとcloud informationを使い、component and system conditionを監視、評価、報告し、faultsを予測して整備につなげると説明している。
同ページでは、maintenance forecast for OEM、probable remaining lifetime、driver notification、workshop appointment planningが出ている。

出典:

- Bosch Mobility, `Predictive Diagnostics`
  <https://www.bosch-mobility.com/en/solutions/diagnostics/predictive-diagnostics/>

意味:

ここでいう予測は、部品やsystemの状態を推定し、故障前に整備計画へ落とすこと。
重要なのは、車両からの状態データ、cloud、OEMへの予測通知、driver notification、workshop appointmentが一連のflowになっていることである。

### 3. deep component levelの異常・摩耗・行動ベース故障予測

Bosch Mobilityの`Cloud and predictive diagnostics`ページでは、fleet向けに、vehicle issuesをoperationに影響する前に予測する、と説明している。
さらに、deep component levelでのanomalies and wear、behavior-based failure prediction、component-specific load and diagnostic features、domain expertise、data science、multiple data sourcesが出ている。

出典:

- Bosch Mobility, `Cloud and predictive diagnostics`
  <https://www.bosch-mobility.com/en/solutions/software-and-services/cloud-and-predictive-diagnostics/>

意味:

この記述は、Repoにとって重要である。
ただし、EPSサプライヤが問うべきことは、「自分たちもfleet platformを売れるか」でも、「外部基盤へfeatureを渡せるか」でもない。
操舵系として、故障前に何を早く説明できると価値になるか、そしてそれを言い過ぎずにどこまで整備行動や診断行動へつなげられるかである。

### 4. AI cockpitのproactiveは、今回の予測診断とは別物

CES 2026向けのBosch AI cockpitでは、AI-powered cockpit、driver routine、preference、context、proactive companionが出ている。
これはAI/SDVの大きな市場シグナルではある。
しかし、故障予測やvehicle healthの根拠としては使わない。

出典:

- Bosch Media Service US, `AI in the car: Bosch presents cockpit innovations at CES 2026 in Las Vegas`
  <https://us.bosch-press.com/pressportal/us/en/press-release-29312.html>

## EPSサプライヤに落とすと何が予測対象になるか

EPSサプライヤが初期に考えるべき予測対象は、個車のEPS交換日ではない。
次のような、操舵系として「早く分かると嬉しい状態」である。

| 予測または先読み対象 | EPSサプライヤ側の材料 | 使い道 | 言ってはいけないこと |
|---|---|---|---|
| 操舵系の負荷状態class | 操舵角、操舵速度、トルク要求、モータ電流、温度、電圧、路面外乱context | 通常使用、重い使用、注意して見る使用を分け、点検優先度や診断読み順の材料にする | EPS寿命や交換時期を断定する |
| limit / fallbackに近いcontext | assist limit、thermal limit、voltage drop、communication degradation、redundancy degraded | すぐ故障ではないが、次に注意して見るべき操舵系状態として扱う | 安全保証やroot cause断定をする |
| 診断値の意味づけ | DTC、freeze frame、extended data、software / calibration ID、発生頻度、再発間隔 | 既存診断値を、故障原因ではなく「どの状態を疑い、何を追加確認するか」へ変換する | DTCだけで故障時期が分かると言う |
| 使用条件に応じた注意状態 | 使用条件、操舵負荷、stop-start、低速高操舵、路面・振動exposure | 実使用で注意すべき状態や評価・診断の見方を先に分ける | 公開proxyだけで予測精度が出ると言う |
| 修理・再発からの学習条件 | 整備結果、交換有無、再発有無、作業時間 | どの注意状態が本当に整備行動に役立つかを後から検証する | EPSサプライヤ単独で閉じたloopがあると断定する |

## ビジネス仮説

Boschの2026年発表を踏まえると、Repoのビジネス仮説は次へ補正できる。

> EPSサプライヤは、操舵系について「故障前に何を早く知れると価値があるか」と「それをどの既存情報で説明できるか」を整理する短期assessmentを提供できる可能性がある。

これは、旧来の「EPS故障予測SaaS」ではない。
また、BoschのPredictive Diagnosticsと競合するplatformでもない。

初期提供物は次である。

1. 操舵系で「早く分かると嬉しい状態」の候補表
2. DTC / freeze frame / extended data / software IDを使って、その状態を説明する場合の意味と限界
3. limit / fallback / degradation contextを、故障断定ではなく注意状態として扱う説明境界
4. その注意状態が本当に整備行動に役立ったかを検証するfeedback loop条件
5. 言ってよい予測、言ってはいけない予測の表

## 買い手 / 利用者

初期利用者は、EPSサプライヤ内の次の部署である。

- 診断企画
- システム設計
- 製品企画
- 品質改善
- 顧客技術説明
- service / aftermarket連携担当
- OEM technical interface

外部の最終利用者はfleet operatorやOEM service部門かもしれない。
しかし、EPSサプライヤ単独の初期買い手として置くのは危険である。
最初は、操舵系として予測診断に乗せる価値がある状態説明を持てるかの社内確認として扱う。

## Why Supplier Can Play

EPSサプライヤが持てる手札は、fleet運用データや修理DBそのものではない。
持てるのは、操舵系の部品知識、診断知識、制御制限、limit / fallback条件、software / calibration差分、DTC / freeze frameの意味である。

Boschの`component-specific load and diagnostic features`という考え方は参考になる。
ただし、EPSサプライヤの主語で言い直すと、「操舵系として早く分かると価値がある状態は何か」「それを既存の制御・診断・品質情報で説明できるか」を定義することになる。

## まだ分からないこと

公開情報だけでは、次は分からない。

1. Bosch Predictive Diagnosticsの対象componentにsteering / EPS / SbWが明示的に含まれるか
2. OEMやfleet platformが、操舵系の注意状態や点検優先度を本当に欲しがるか
3. EPSサプライヤ内に、予測価値へ変えられる制御・診断・品質情報の候補が既にあるか
4. repair feedback loopにEPSサプライヤが触れる契約形態があるか
5. 既存診断企画、品質改善、service engineeringが同じ成果物を既に持っているか

これらが分からないことは、この方向を即Stopする理由ではない。
ただし、故障予測や交換時期予測を売り文句にしないための境界である。

## 判定

Proceed候補:

- 診断企画または品質改善が、操舵系で早く分かると嬉しい状態を3つ以上挙げられる
- DTC / freeze frame / extended data / software IDを、注意状態や点検優先度の説明材料として整理できる
- OEM / fleet / platform側の整備行動、点検優先度、診断読み順へつながる具体的な使い道がある
- repair feedback loopの少なくとも一部に接続できる可能性がある

Hold:

- Bosch公開情報は強いが、操舵系の注意状態に対する需要が未確認
- EPSサプライヤ内の既存診断・品質・service資料との重複が未確認
- OEMやfleet platformとの接続がまだ仮説

Stop候補:

- 操舵系の注意状態が汎用CAN/telematicsや一般DTC説明と区別できない
- 診断企画、品質改善、service engineeringの既存成果物と同じ表になる
- repair feedback loopやfleet / OEM platform接続を前提にしないと価値が出ない
- 売り文句が、EPS交換時期、残寿命、安全保証、保証費削減断定に戻る

Stop候補と書く場合も、最終Stopではない。
最終判断では、上位ルールに沿ったRule Checkを改めて書く。

## CoVe

| 検証質問 | 回答 | Confidence | 反映 |
|---|---|---:|---|
| Boschの2026年発表にpredictive maintenanceはあるか | Yes。Uptake買収計画でAI-driven predictive maintenance、vehicle health services、fleet downtime / maintenance costが明記されている。 | High | 市場需要、Boschが言う予測の中身に反映 |
| Bosch Predictive Diagnosticsはremaining lifetimeやmaintenance forecastを扱うか | Yes。公開ページにprobable remaining lifetime、maintenance forecast for OEM、workshop appointment planningが出ている。 | High | 予測の中身2に反映 |
| Cloud and predictive diagnosticsはcomponent-specific load and diagnostic featuresを扱うか | Yes。公開ページにdeep component level、behavior-based failure prediction、component-specific load and diagnostic featuresが出ている。 | High | 予測の中身3、Why Supplier Can Playに反映 |
| これをEPS単体の交換時期予測と言えるか | No。connected vehicle、cloud、fleet、multiple data sources、repair feedback loopを含むため、EPS単体公開proxyとは別物である。 | High | 禁止主張に反映 |
| EPSサプライヤのビジネスに転記できるか | 仮説としては可能。操舵系で早く分かると嬉しい状態、説明できる既存情報、言ってはいけない予測を分けるassessmentに落とす必要がある。 | Medium | ビジネス仮説、判定に反映 |

## EPSサプライヤとしての言い方

言ってよいこと:

> Boschは2026年に、fleet向けAI-driven predictive maintenanceとvehicle health servicesを強化する動きを公開している。Predictive Diagnosticsでは、connected vehicle data、cloud information、component-specific load and diagnostic features、domain expertise、multiple data sourcesを使い、部品やsystemの状態、故障前兆、整備タイミングを扱う。EPSサプライヤとしては、操舵系で早く分かると嬉しい状態は何か、それを既存の制御・診断・品質情報でどこまで説明できるか、どこから先は交換時期予測や原因断定になって危ないかを整理する価値がある。

まだ言ってはいけないこと:

> BoschがEPS単体の故障予測や交換時期予測を公開した。

> 公開proxyだけでEPSのremaining lifetimeを予測できる。

> EPSサプライヤ単独で、fleet predictive maintenance platformを外販できる。

> 操舵系の注意状態を示せば、安全保証、root cause断定、保証費削減ができる。

## 次アクション

次は、[docs/101_oem_usage_translation_review_questions.md](101_oem_usage_translation_review_questions.md) とは別に、predictive diagnostics向けの質問票を作る。
最初の質問は2つに絞る。

1. 操舵系で、故障前に早く分かると嬉しい状態は何か
2. DTC / freeze frame / extended data / software IDのうち、その状態説明に使ってよいものと、使うと誤解を生むものは何か
