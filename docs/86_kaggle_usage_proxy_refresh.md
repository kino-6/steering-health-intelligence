# Kaggle実使用条件proxy再調査

## 結論

Kaggleを見る目的は、工程検査の改善だけではない。
今回の主目的は、公開データから、EPSが実使用でどんな速度、操舵、路面、振動、通信状態に晒されるのかを読み、EPSサプライヤの評価scenario、診断質問、顧客説明質問、禁止主張へ変換できるかを見ることである。

この観点では、KGL003〜KGL006を切らない。
むしろ、KGL003、KGL005、KGL006が主線である。
追加調査では、KGL007〜KGL012を追加する。

| ID | 対象 | 判断 | 使い道 |
|---|---|---|---|
| KGL003 | OBD-II / CAN driving behavior | Keep | 速度帯、stop-start、急加減速、急操舵に近い使用条件family |
| KGL005 | Steering angle / behavioral cloning | Keep | 操舵角、操舵変化、操舵要求family |
| KGL006 | PVS passive vehicular sensors | Keep | 路面、振動、走行環境family |
| KGL007 | Traffic, Driving Style and Road Surface Condition | Add / High priority | 運転スタイルと路面状態を同時に見る使用条件family |
| KGL008 | Road Quality Dataset | Add / Medium priority | 路面凹凸、荒れ、都市走行の外乱条件 |
| KGL009 | Driver Behavior KPI Dataset from CARLA | Add / Schema only | speed、jerk、brake、steering、lane deviationを使ったscenario設計の型 |
| KGL010 | Vehicle Telemetry for Driver Behavior Analysis | Add / Schema only | steering、braking、accelerationを使うdriver behavior分類の型 |
| KGL011 | CICIoV2024 / CICIoV2024DecimalCSV | Add / Boundary check | CAN DoS / spoofing、特にsteering wheel spoofingを含む通信異常境界 |
| KGL012 | Battery and Heating Data in Real Driving Cycles | Add / Weak but useful context | 実走行サイクル、外気、熱条件、EV使用環境の補助proxy |

KGL001とKGL002は残すが、今回の主目的ではない。
KGL001は製造・EOL検査、KGL002は評価時間短縮の別枝である。

## 何を判断しているか

判断しているのは、KaggleでEPS内部状態や故障原因を当てられるかではない。
それはできない。
公開Kaggleデータには、対象EPSのDTC、freeze frame、assist state、limit state、thermal state、software/calibration ID、交換結果、返却品結果が基本的に見えないためである。

ここで判断しているのは、次である。

> 公開Kaggleデータから、EPSサプライヤが評価・診断・顧客説明で使う「実使用条件の問い」を作れるか。

具体的には、以下のような問いに落とせるかを見る。

- 低速で大きな操舵が繰り返される条件は、どの公開proxyから拾えるか。
- stop-start、急加減速、急操舵、荒れた路面は、どの組み合わせでfamily化できるか。
- 操舵角や操舵変化を、EPS評価scenarioの入力としてどう整理できるか。
- 通信異常やspoofingを、EPS状態説明や診断コンテンツでどこまで扱ってよいか。
- 公開proxyから言ってはいけない主張は何か。

## 追加ID

### KGL007: Traffic, Driving Style and Road Surface Condition

KGL007は追加候補として強い。
このデータは、交通状態、運転スタイル、路面状態を扱う。
スマートフォン加速度のような受動的な車両近傍データから、走行条件を分類する方向である。

EPSサプライヤへの読み替えは、工程検査ではない。
低速/高速、荒れた路面、急加減速、運転スタイルの違いを、EPS評価scenarioの外部条件へ変換することである。

Proceed条件:

- 路面状態、運転スタイル、速度/加速度の組み合わせを20〜50件の使用条件familyにできる。
- 各familyが、EPS評価scenarioまたは顧客説明質問へ転記できる。

Kill条件:

- 単なる運転スタイル分類で終わる。
- EPSサプライヤが次に何を評価すべきかに戻らない。

### KGL008: Road Quality Dataset

KGL008は、路面外乱を見るために残す。
都市走行で路面のimperfectionを検出する方向のデータである。

EPSサプライヤへの読み替えは、路面そのものを売ることではない。
荒れた路面、段差、連続振動のような外乱を、操舵系の評価scenarioや顧客説明の問いに変換することである。

Proceed条件:

- 路面外乱を、操舵負荷、振動、異音、driver perceptionの質問へ転記できる。

Kill条件:

- road quality productに流れる。
- EPS評価や診断質問へ戻らない。

### KGL009: Driver Behavior KPI Dataset from CARLA

KGL009は、実証データとしては弱い。
CARLA由来のシミュレーションデータで、speed、acceleration、jerk、throttle/brake、steering behavior、lane deviation、collision indicatorsのようなKPIを扱う。

ただし、schemaとしては使える。
EPSサプライヤが実使用条件familyを作るとき、どの特徴量を並べると評価scenarioへ落ちやすいかを考える材料になる。

Proceed条件:

- 実証ではなく、scenario schemaの型として使う。

Kill条件:

- シミュレーション結果を市場実態やEPS故障証拠として扱う。

### KGL010: Vehicle Telemetry for Driver Behavior Analysis

KGL010も、実証データとしては慎重に扱う。
Kaggle説明上はsynthetically generated driver behavior datasetであり、real-world vehicle telemetryに似せたものとされている。
safe/aggressive driving、smooth acceleration、stable steering、low braking intensityのような運転行動分類に使える。

EPSサプライヤへの読み替えは、実データ証拠ではなく、使用条件familyの列設計である。

Proceed条件:

- steering、braking、accelerationを、使用条件familyのfeature候補として整理する。

Kill条件:

- 合成データを実市場証拠として扱う。

### KGL011: CICIoV2024 / CICIoV2024DecimalCSV

KGL011は、KGL004の現代版として追加する。
CICIoV2024は、2019年Ford車両のECU構造を使い、CAN-BUS上でDoSとspoofing攻撃を扱うIoV security benchmarkである。
Kaggle上にもdecimal CSV版があり、IDS開発用として扱われている。

EPSサプライヤへの読み替えは、汎用cyber商品ではない。
診断通信、異常通信、security access、steering wheel spoofingのような事象を、EPS状態説明や診断コンテンツでどう扱うべきか、どこから先は言ってはいけないかを確認する材料である。

Proceed条件:

- 通信異常を、EPS診断質問、security access質問、禁止主張へ転記できる。

Kill条件:

- IDS商品、汎用cyberサービス、SbW安全証明に流れる。

### KGL012: Battery and Heating Data in Real Driving Cycles

KGL012は直接の操舵データではない。
BMW i3の実走行trip、battery、heating、thermal contextを扱うデータである。

EPSサプライヤへの読み替えは弱いが、実走行サイクル、外気、熱条件、EV使用環境のproxyとしては使える。
過去にthermal limitやassist limitationの話を見ていたため、実使用環境の補助材料として残す価値はある。

Proceed条件:

- thermal / real driving cycle contextを、EPS評価scenarioの外部条件として使える。

Kill条件:

- EPS thermal stateを直接見た扱いにする。

## 新しい優先順位

次に深掘りする順番は、以下がよい。

1. KGL003、KGL005、KGL006、KGL007、KGL008を束ね、実使用条件familyを作る。
2. KGL011とKGL004を束ね、通信異常と禁止主張の境界表を作る。
3. KGL009、KGL010は、feature schemaの参考として使う。
4. KGL012は、thermal / EV real driving contextの補助として使う。
5. KGL001、KGL002は、工程検査や評価時間短縮を再開するときだけ戻る。

## 初期成果物

最初に作るべきものは、Kaggle精度競争ではない。
20〜50件の使用条件family表である。

列は以下でよい。

| 列 | 内容 |
|---|---|
| usage_family | 低速高操舵、急操舵、stop-start、荒れた路面、連続振動など |
| source_id | KGL003、KGL005、KGL006、KGL007、KGL008など |
| public_proxy | speed、acceleration、steering angle、gyro、GPS、road surfaceなど |
| eps_question | EPS評価・診断・説明で確認すべき問い |
| possible_artifact | 評価scenario、診断質問、顧客説明質問、禁止主張 |
| what_not_to_claim | 故障原因、DTC不足、内部状態、保証費削減など |
| kill_signal | EPSサプライヤの判断へ転記できない場合 |

## EPSサプライヤとしての言い方

言ってよいこと:

> Kaggleの一部データは、EPS内部状態を示すものではないが、実使用条件、操舵要求、路面・環境、通信異常を読む公開proxyとして使える。これを評価scenario、診断質問、顧客説明質問、禁止主張へ変換できるかを見る価値がある。

まだ言ってはいけないこと:

> KaggleでEPS故障予測を実証できる。

> 公開proxyでEPS内部状態やDTC不足を断定できる。

> KaggleのCAN attack datasetでEPS/SbW cyber商品を作れる。

> 路面分類やADAS操舵モデルをEPSサプライヤ商品として売れる。

## Kill条件

この枝は、次のどれかに当たれば止める。

- 使用条件familyが、評価scenario、診断質問、顧客説明質問、禁止主張へ転記できない。
- 公開データの紹介で終わり、EPSサプライヤが次に何を確認すべきかが出ない。
- EPS内部状態、故障原因、DTC不足を断定し始める。
- ADAS制御、road quality product、generic IDS/cyber productへ流れる。
- OEM保証DB、fleet data、service outcomeがないと価値が出ない方向へ戻る。

## CoVe

| 検証質問 | 回答 | Confidence | 反映 |
|---|---|---|---|
| KGL003〜006を工程検査に効かないという理由で切るべきか | 切るべきではない。工程検査ではなく実使用条件proxyとして見るべきである。 | High | KGL003/005/006を主線に戻した |
| 追加IDに実使用proxyとして有望なものはあるか | ある。KGL007は運転スタイルと路面状態、KGL008はroad quality、KGL011はCAN通信異常の境界確認に使える。 | Medium | KGL007/008/011を追加優先候補にした |
| シミュレーションや合成データは使えるか | 実証には使えないが、feature schemaやscenario設計の型には使える。 | Medium | KGL009/010をschema onlyにした |
| EPS内部状態を公開proxyから言えるか | 言えない。DTC、freeze frame、assist state、limit state、thermal state、交換結果が見えない。 | High | 禁止主張に明記した |
| EPSサプライヤの成果物へ転記できるか | 可能性はある。評価scenario、診断質問、顧客説明質問、禁止主張へ落とせるかが次の検証点である。 | Medium | 次成果物を20〜50件の使用条件family表にした |

## Sources

- Kaggle: OBD-II & CAN-Based Driving Behavior Dataset, https://www.kaggle.com/datasets/isaygerardozamora/obd-ii-and-can-based-driving-behavior-dataset
- Kaggle: Udacity Self Driving Car - Behavioural Cloning, https://www.kaggle.com/datasets/andy8744/udacity-self-driving-car-behavioural-cloning
- Kaggle: Self Driving Car, https://www.kaggle.com/datasets/aslanahmedov/self-driving-carbehavioural-cloning
- Kaggle: PVS - Passive Vehicular Sensors Datasets, https://www.kaggle.com/datasets/jefmenegazzo/pvs-passive-vehicular-sensors-datasets
- Kaggle: Traffic, Driving Style and Road Surface Condition, https://www.kaggle.com/datasets/gloseto/traffic-driving-style-road-surface-condition
- Kaggle: Road Quality Dataset, https://www.kaggle.com/datasets/nickkotarelas/road-quality-dataset
- Kaggle: Driver Behavior KPI Dataset from CARLA, https://www.kaggle.com/datasets/lahkimesara/driver-behavior-kpi-dataset-from-carla
- Kaggle: Vehicle Telemetry for Driver Behavior Analysis, https://www.kaggle.com/datasets/sonalshinde123/vehicle-telemetry-for-driver-behavior-analysis
- Kaggle: CICIoV2024DecimalCSV, https://www.kaggle.com/datasets/pushpakattarde/ciciov2024decimalcsv
- University of New Brunswick: CICIoV2024 dataset, https://www.unb.ca/cic/datasets/iov-dataset-2024.html
- GitHub: CICIoV2024 public files, https://github.com/sali446/CICIoV2024
- Kaggle: BATTERY AND HEATING DATA IN REAL DRIVING CYCLES, https://www.kaggle.com/datasets/atechnohazard/battery-and-heating-data-in-real-driving-cycles
