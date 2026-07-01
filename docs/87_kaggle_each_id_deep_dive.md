# Kaggle各ID深掘り

## 結論

Kaggleを工程検査だけで見ない。
今回の判断軸は、公開Kaggle課題やデータセットから、EPSサプライヤが評価scenario、診断質問、顧客説明質問、禁止主張へ転記できる「実使用条件の問い」を作れるかである。

この軸では、12件を3つに分ける。

| 区分 | ID | 判断 |
|---|---|---|
| 実使用条件familyの主材料 | KGL003, KGL005, KGL006, KGL007, KGL008 | 次に深掘りする。20〜50件の使用条件familyへ落とす |
| 通信異常と禁止主張の境界確認 | KGL004, KGL011 | 汎用cyber商品にはしない。診断通信、security access、禁止主張へ転記する |
| 別枝または補助 | KGL001, KGL002, KGL009, KGL010, KGL012 | KGL001/002は製造・評価効率の別枝。KGL009/010はschema only。KGL012はthermal context only |

次に進めるなら、最初の成果物はモデルではなく、**使用条件family表**である。
KGL003/005/006/007/008を束ね、低速高操舵、急操舵、stop-start、荒れた路面、連続振動、運転荒さ、路面凹凸といったfamilyを20〜50件作る。
その各行を、EPS評価scenario、診断質問、顧客説明質問、禁止主張に対応付ける。

## 何を判断しているか

EPS内部の故障、DTC不足、assist state、limit state、thermal stateを公開Kaggleから断定する話ではない。
公開Kaggleから読めるのは、実使用に近い外部条件や操作条件である。

したがって、各IDでは次を判断した。

- 目的変数や分類対象は何か。
- EPSサプライヤのどの業務に転記できるか。
- 次に作るfamilyや質問は何か。
- 何を言ってはいけないか。
- どの条件なら止めるか。

## ID別深掘り

### KGL001: Bosch Production Line Performance

Boschの課題は、製造ライン上の測定・試験データから内部不良を予測するものである。
Kaggle説明では、assembly lineで各componentに対して行われる大量のmeasurement / testからinternal failureを予測する問題として置かれている。
別資料でも、line、station、test numberのような工程構造や、品質管理上のfail判定が読み取れる。

EPSサプライヤへの読み替え:

- 製造・EOL検査で、再検査、保留、工程確認候補を早く出す。
- ただし今回の主目的は工程検査ではないため、実使用条件familyの主材料にはしない。

次アクション:

- 製造・EOL検査の枝を再開する場合だけ、上位リスク個体、工程グループ、再検査/保留/工程確認の1枚を作る。

言ってはいけないこと:

- Bosch型があるのでEPS故障予測ができる。
- EOL検査を省ける。
- root causeを断定できる。

判断:

> Separate branch。今回の主線ではないが、製造・EOL検査の別枝として保存する。

### KGL002: Mercedes-Benz Greener Manufacturing

Mercedes-Benzの課題は、車両構成からテストベンチ時間を予測するものである。
Kaggle説明では、異なるfeature permutationを持つ車両がtestingを通過する時間を予測する問題として置かれている。
これは品質不良ではなく、評価時間や試験順序の問題である。

EPSサプライヤへの読み替え:

- EPSのvariant、software、calibration、診断設定、試験セットから、bench/HILS/EOL評価時間を見積もる。
- 評価時間のばらつきが大きい場合は、評価計画やrelease gateに効く可能性がある。

次アクション:

- KGL001と同じく別枝扱い。
- 評価時間短縮を再開する場合だけ、構成情報と試験時間のproxy表を作る。

言ってはいけないこと:

- 試験時間を当てられるので品質判断ができる。
- 実使用条件や操舵要求が分かる。

判断:

> Separate branch。評価時間短縮の別枝として保存する。

### KGL003: OBD-II / CAN driving behavior

KGL003は主材料である。
Kaggle説明では、OBD-II経由のCAN protocolから、複数driver / vehicleのdriving behavior dataを収集したものとされる。
ここで読めるのは、EPS内部ではなく、運転行動と車両の使われ方である。

EPSサプライヤへの読み替え:

- 速度帯、加減速、stop-start、急操作に近い使用条件を作る。
- 低速高操舵や急操舵に相当するfamilyを作るための入口にする。

次アクション:

- speed、acceleration、engine load、brake/throttle相当の項目がある場合、使用条件familyへ分解する。
- KGL005の操舵角、KGL006/007/008の路面・環境と組み合わせる。

言ってはいけないこと:

- CAN/OBDだけでEPS内部故障やDTC不足が分かる。
- driver behavior分類がそのままEPS劣化兆候になる。

判断:

> Keep / High。次の使用条件family作成に使う。

### KGL004: Car-Hacking Dataset

KGL004は、通信異常の境界確認に使う。
CAN trafficからnormal/attackを分けるデータであり、DoS、fuzzy、gear/RPM spoofingのような攻撃を扱う。

EPSサプライヤへの読み替え:

- 診断通信、異常通信、security access、禁止主張の境界確認に使う。
- EPS状態説明や診断コンテンツで、通信異常をどこまで扱えるかを見る。

次アクション:

- KGL011と束ねて、通信異常/攻撃type、EPSサプライヤが言えること、言ってはいけないことの表を作る。

言ってはいけないこと:

- 汎用IDS商品にする。
- SbW安全証明に使う。
- EPS品質証拠として扱う。

判断:

> Keep with boundary。商品候補ではなく、境界確認材料。

### KGL005: Steering angle / behavioral cloning

KGL005は主材料である。
behavioral cloning系データは、画像などからsteering angleを推定する問題であり、自動運転寄りではある。
しかし、EPSサプライヤから見ると、操舵要求そのものを公開proxyとして扱える点が重要である。

EPSサプライヤへの読み替え:

- 操舵角、操舵角変化、連続操舵、急操舵のfamilyを作る。
- 速度条件や路面条件と組み合わせ、EPS評価scenarioへ転記する。

次アクション:

- 角度の大きさ、角速度、継続時間、頻度という4列で操舵要求familyを作る。
- KGL003の速度/加減速、KGL006/007/008の路面・振動と組み合わせる。

言ってはいけないこと:

- ADAS制御モデルを作る。
- 公開steering angleからEPS内部状態を推定できる。

判断:

> Keep / High。操舵要求familyの中核にする。

### KGL006: PVS Passive Vehicular Sensors

KGL006は主材料である。
PVSは、accelerometer、gyroscope、magnetometer、GPS、camera dataのような受動的な車両センサを使い、road surface type classificationに使われる。

EPSサプライヤへの読み替え:

- 路面、振動、走行環境をEPS負荷条件や評価scenarioの外部条件へ変換する。
- 連続振動、荒れた路面、速度帯との組み合わせを作る。

次アクション:

- road surface、gyro、acceleration、GPS速度を、路面・振動familyへ変換する。
- KGL005の操舵要求と組み合わせ、「荒れた路面 + 操舵変化」のような複合familyを作る。

言ってはいけないこと:

- 路面分類がEPS内部状態を示す。
- road surface productとして売れる。

判断:

> Keep / High。路面・環境familyの中核にする。

### KGL007: Traffic, Driving Style and Road Surface Condition

KGL007は追加IDの中で最も強い。
Kaggle説明では、traffic、driving style、road surface conditionを扱い、smartphone accelerometer由来のlongitudinal acceleration、engine loadなどの車両・加速度情報が示される。
外部論文でも、このKaggle datasetがOBD-IIとaccelerometerからtraffic / driving style / road surface conditionを予測する用途で使われている。

EPSサプライヤへの読み替え:

- 運転スタイル、路面状態、交通状態を同時に持つため、実使用条件familyにしやすい。
- 「荒れた路面 + aggressive driving + 低速/高負荷」のような複合条件を作れる可能性がある。

次アクション:

- traffic、driving style、road surface conditionを掛け合わせ、20〜50件のusage family候補を作る。
- 各familyに、EPS評価scenarioと顧客説明質問を付ける。

言ってはいけないこと:

- 運転荒さからEPS故障原因を断定できる。
- 路面状態からEPS内部stressを直接見たと言える。

判断:

> Keep / Highest priority。KGL003/005/006を束ねるハブとして使う。

### KGL008: Road Quality Dataset

KGL008は中優先度で残す。
Kaggle説明では、都市部を車両で走行したrunから、road surface imperfectionsを検出する基盤データとされる。

EPSサプライヤへの読み替え:

- 路面凹凸、段差、荒れた路面、連続振動を評価scenarioの外乱条件にする。
- 異音、振動、driver perceptionの顧客説明質問に転記する。

次アクション:

- road imperfectionを、段差、連続凹凸、荒れた舗装、低速市街地の4類型に仮分類する。
- 操舵角familyと組み合わせ、「低速操舵 + 路面凹凸」の質問を作る。

言ってはいけないこと:

- road quality datasetからEPS故障や部品劣化を断定する。
- road quality productをEPSサプライヤ商品にする。

判断:

> Keep / Medium。路面外乱familyの補強に使う。

### KGL009: Driver Behavior KPI Dataset from CARLA

KGL009は実証には使わない。
CARLA由来のdatasetで、speed、acceleration、jerk、throttle/brake variability、steering behavior、lane deviation、collision indicatorsのようなKPIを扱う。

EPSサプライヤへの読み替え:

- 実使用条件familyの列設計に使う。
- speed、jerk、brake、steering、lane deviationのようなfeatureを、評価scenario表の列候補として借りる。

次アクション:

- 使用条件family表のschemaに、speed range、jerk、brake/throttle variability、steering behavior、lane deviationを入れるか検討する。

言ってはいけないこと:

- CARLA結果を市場実態として扱う。
- シミュレーションでEPSの実使用負荷を証明したと言う。

判断:

> Schema only。使うが、証拠にはしない。

### KGL010: Vehicle Telemetry for Driver Behavior Analysis

KGL010も実証には使わない。
Kaggle説明では、synthetically generated driver behavior datasetであり、safe driver / aggressive driverのような分類、smooth acceleration、stable steering、low braking intensityなどの特徴が示される。

EPSサプライヤへの読み替え:

- driver behavior分類の列設計に使う。
- aggressive / safeというラベルではなく、steering stability、braking intensity、acceleration smoothnessのような特徴量名を借りる。

次アクション:

- KGL009と合わせ、使用条件family表のfeature候補を整理する。

言ってはいけないこと:

- 合成データを市場証拠として扱う。
- safe/aggressive分類をEPSリスク判断として使う。

判断:

> Schema only。KGL009と同じく、列設計に限る。

### KGL011: CICIoV2024 / CICIoV2024DecimalCSV

KGL011は通信異常の重要材料である。
UNBの説明では、2019 Ford車両のECU構造に対して、CAN-BUS上でDoSとspoofing攻撃を実施したdatasetである。
公開GitHubには、decimal_DoS、decimal_spoofing-GAS、decimal_spoofing-RPM、decimal_spoofing-SPEED、decimal_spoofing-STEERING_WHEELなどのファイルが見える。

EPSサプライヤへの読み替え:

- steering wheel spoofingやDoSを、EPS診断質問、security access質問、禁止主張へ転記する。
- 「通信異常時にEPS状態説明として何を言えるか」を考える材料にする。

次アクション:

- KGL004と束ね、通信異常type、EPSサプライヤが言えること、言ってはいけないこと、既存cyber領域との境界を表にする。

言ってはいけないこと:

- EPS/SbW cyber商品を作れる。
- 通信異常検出で安全証明ができる。
- steering wheel spoofing datasetがEPS固有診断の証拠になる。

判断:

> Keep with boundary / High。境界確認として重要。

### KGL012: Battery and Heating Data in Real Driving Cycles

KGL012は弱いが、補助contextとして残す。
Kaggle説明では、BMW i3の72 real driving tripsを記録し、battery、heating、real driving cycleの検証に使うデータである。
操舵信号は主題ではない。

EPSサプライヤへの読み替え:

- EV実走行、外気、熱条件、trip contextを評価scenarioの外部条件として使う。
- 過去に見たthermal limit / assist limitationの公開proxy補助にできる可能性がある。

次アクション:

- external temperature、trip duration、urban/highway、heating loadのような外部条件を、使用条件familyの補助列として持つ。

言ってはいけないこと:

- EPS thermal stateを見た。
- assist limitationを推定できる。

判断:

> Context only / Low。操舵や路面の主材料ではないが、熱・EV実走行contextとして残す。

## 次に作る表

次に作るべき表は、Kaggle datasetの精度表ではない。
EPSサプライヤがレビューに使える、使用条件family表である。
実際に30件へ展開した表は、[docs/88_kaggle_usage_condition_family_table.md](88_kaggle_usage_condition_family_table.md) と [data/kaggle_usage_condition_families.tsv](../data/kaggle_usage_condition_families.tsv) に置く。

| usage_family | source_ids | proxy_signals | eps_evaluation_question | diagnostic_question | customer_explanation_question | forbidden_claim |
|---|---|---|---|---|---|---|
| 低速高操舵 | KGL003, KGL005 | speed, steering angle, steering change | 低速で大きな操舵が繰り返される条件を既存評価で見ているか | DTC/freeze frameだけで使われ方を説明できるか | 顧客に「通常使用範囲」か「高負荷使用」か説明できるか | 故障原因や残寿命を断定しない |
| 荒れた路面での操舵 | KGL005, KGL006, KGL008 | steering angle, gyro, acceleration, road imperfection | 路面外乱と操舵入力の組み合わせを見ているか | 異音/振動とEPS異常を混同しない説明があるか | 路面由来の体感とEPS異常の違いを説明できるか | EPS内部不良を断定しない |
| 通信異常中の操舵関連signal | KGL004, KGL011 | CAN ID, data bytes, spoofing class | 異常通信時にEPSが何を無視/制限するか説明できるか | security accessや診断読み順の注意があるか | 通信異常をEPS故障とどう切り分けるか | 安全証明やcyber商品化を主張しない |

## EPSサプライヤとしての結論

EPSサプライヤとして、Kaggleから売れる商品をすぐ作る段階ではない。
しかし、公開proxyから評価・診断・説明の問いを作る材料としては、KGL003/005/006/007/008が使える。
KGL011/KGL004は通信異常の境界確認に使える。

次に見せる相手は、製造品質ではなく、まず評価企画、HILS/bench、診断コンテンツ、顧客技術説明の担当である。

## Sources

- Kaggle: Bosch Production Line Performance, https://www.kaggle.com/c/bosch-production-line-performance
- Mangal and Kumar: Using Big Data to Enhance the Bosch Production Line Performance, https://arxiv.org/abs/1701.00705
- Kaggle: Mercedes-Benz Greener Manufacturing, https://www.kaggle.com/competitions/mercedes-benz-greener-manufacturing
- Kaggle: OBD-II & CAN-Based Driving Behavior Dataset, https://www.kaggle.com/datasets/isaygerardozamora/obd-ii-and-can-based-driving-behavior-dataset
- Kaggle: Car-Hacking Dataset, https://www.kaggle.com/datasets/pranavjha24/car-hacking-dataset
- HCRL: Car-Hacking Dataset, https://ocslab.hksecurity.net/Datasets/CAN-intrusion-dataset
- Kaggle: Udacity Self Driving Car - Behavioural Cloning, https://www.kaggle.com/datasets/andy8744/udacity-self-driving-car-behavioural-cloning
- Kaggle: Self Driving Car, https://www.kaggle.com/datasets/aslanahmedov/self-driving-carbehavioural-cloning
- Kaggle: PVS - Passive Vehicular Sensors Datasets, https://www.kaggle.com/datasets/jefmenegazzo/pvs-passive-vehicular-sensors-datasets
- Kaggle: Traffic, Driving Style and Road Surface Condition, https://www.kaggle.com/datasets/gloseto/traffic-driving-style-road-surface-condition
- MDPI Applied Sciences: In-Vehicle Data for Predicting Road Conditions and Driving Style, https://www.mdpi.com/2076-3417/12/18/8928
- Kaggle: Road Quality Dataset, https://www.kaggle.com/datasets/nickkotarelas/road-quality-dataset
- Kaggle: Driver Behavior KPI Dataset from CARLA, https://www.kaggle.com/datasets/lahkimesara/driver-behavior-kpi-dataset-from-carla
- Kaggle: Vehicle Telemetry for Driver Behavior Analysis, https://www.kaggle.com/datasets/sonalshinde123/vehicle-telemetry-for-driver-behavior-analysis
- Kaggle: CICIoV2024DecimalCSV, https://www.kaggle.com/datasets/pushpakattarde/ciciov2024decimalcsv
- University of New Brunswick: CICIoV2024 dataset, https://www.unb.ca/cic/datasets/iov-dataset-2024.html
- GitHub: CICIoV2024 public files, https://github.com/sali446/CICIoV2024
- Kaggle: BATTERY AND HEATING DATA IN REAL DRIVING CYCLES, https://www.kaggle.com/datasets/atechnohazard/battery-and-heating-data-in-real-driving-cycles
