# Kaggle問題設定ID別深掘り

## 結論

今回見ているのは、Kaggleの公開データでEPSの故障を当てられるかではない。
また、工程検査だけを目的にしているわけでもない。
企業や研究者がKaggleに出した課題の目的変数、入力データ、評価指標から、どの業務判断や利用状態を早く知りたいのかを読み、EPSサプライヤの仮説検証にどう使えるかを判断している。

前回の整理では、KGL001とKGL002を製造・評価効率の枝として強く見すぎ、KGL003〜KGL006を「工程検査に効かないから主テーマではない」と下げてしまった。
これは目的設定が狭すぎた。
KGL003〜KGL006は、工程検査ではなく、実使用条件、操舵要求、路面・環境、通信異常を読む公開proxyとして残す。

| ID | 対象 | 判断 | 理由 |
|---|---|---|---|
| KGL001 | Bosch Production Line Performance | Separate branch / not current main | 製造・EOL検査には読み替えやすいが、今回の主目的が工程検査でないなら最優先にはしない |
| KGL002 | Mercedes-Benz Greener Manufacturing | Separate branch / not current main | 評価時間短縮には使えるが、これも製造・評価効率の枝であり、EPS実使用価値の主材料ではない |
| KGL003 | OBD-II / CAN driving behavior | Keep / usage-condition lens | 低速高操舵、急操舵、速度帯、stop-startなど、EPS負荷や使われ方の公開proxyとして使える |
| KGL004 | Car-Hacking Dataset | Keep with boundary / communication-abnormality lens | 汎用cyber商品にはしないが、診断通信、異常通信、禁止主張を考える材料として残す |
| KGL005 | Steering angle / behavioral cloning | Keep / steering-demand lens | 操舵要求そのものを読むproxyであり、EPSがどんな操舵需要に晒されるかを考える材料になる |
| KGL006 | PVS passive vehicular sensors | Keep / road-and-environment lens | 路面、振動、走行環境を読むproxyであり、EPS負荷条件や評価scenarioの外部条件に使える |

したがって、次にやるべきなのはKGL001だけを進めることではない。
まずKGL003、KGL005、KGL006を使って「実使用でEPSにどんな操舵・路面・速度条件がかかるのか」を整理し、KGL004を「通信異常や診断アクセスで言ってよいこと / 言ってはいけないこと」の境界確認に使う。
KGL001とKGL002は、製造・評価効率を別枝として見る場合に戻す。

この判断を受けてKaggleを再調査し、KGL007〜KGL012を追加した結果は、[docs/86_kaggle_usage_proxy_refresh.md](86_kaggle_usage_proxy_refresh.md) に置く。
追加後の主線は、KGL003/005/006/007/008で実使用条件familyを作り、KGL011/KGL004で通信異常と禁止主張の境界を確認する、である。

## 市場需要

市場需要は、ドライバーにEPS交換時期を知らせることでも、工程検査だけを良くすることでもない。
いま見たいのは、公開データから、EPSがどんな実使用条件、操舵要求、路面・環境条件、通信異常に晒されるのかを読み、EPSサプライヤが評価scenario、診断コンテンツ、禁止主張、顧客説明の問いに変換できるかである。

Kaggle上でBoschは、製造ラインの測定・試験データから内部不良を予測する課題を出している。
これは、工程中の大量データから後工程の不良や手戻りを早く拾いたいという需要を示すが、工程検査の枝である。

Mercedes-Benzは、車両構成からテストベンチ時間を予測する課題を出している。
これは、多品種構成で評価・検査時間を読み、待ち時間や試験負荷を減らしたいという需要を示すが、評価時間短縮の枝である。

一方で、OBD-II/CAN、操舵角、受動車両センサ、CAN異常のデータは、工程検査ではなく実使用側の問いに近い。
これらはEPS内部状態を直接示さないが、どんな速度帯、操舵操作、路面、振動、通信状態を評価や説明の問いに入れるべきかを考える材料になる。

EPSサプライヤに引き寄せると、需要はこうなる。

> 公開データから実使用条件と操舵要求を読み、EPSサプライヤが評価scenario、診断コンテンツ、顧客説明、禁止主張に変換できる問いを作りたい。

## 未解決の痛み

残す痛みは5つである。

1. 公開情報だけでは、EPS内部状態は見えない。
2. それでも、実使用でどんな速度帯、操舵要求、路面、振動、通信異常が出るかは公開proxyから読める可能性がある。
3. そのproxyを、評価scenario、診断コンテンツ、顧客説明の問いに転記する型がまだない。
4. OBD/CAN、操舵角、路面センサ、CAN異常を別々に見ると、EPSサプライヤの判断に戻りにくい。
5. Kaggleを精度競争として見てしまうと、EPSサプライヤが何を評価し、何を言ってはいけないかに落ちない。

この痛みは、EPS市場故障予測ではない。
また、工程検査の話だけでもない。
公開proxyから実使用側の問いを作り、それがEPSサプライヤの既存評価、既存診断、既存顧客説明に足せるかを見る話である。

## ID別判断

### KGL001: Bosch Production Line Performance

KGL001は、製造・EOL検査の枝では有力である。
Boschの課題は、製造ライン上の測定・試験データを使って内部不良を予測するものだった。
公開情報では、データは部品が組立工程を進む中で記録された測定・試験の集合で、feature名にはline、station、test numberのような工程構造が含まれる。

EPSサプライヤに読み替えると、これは「市場に出た後の故障予測」ではなく、「出荷前に怪しい個体や工程を早く見つける」話である。
出力は故障断定ではなく、再検査、保留、工程確認の優先順位にする。

残す理由:

- 目的変数が製造品質の判断に近い。
- 入力データが工程測定、試験値、EOL結果に近く、EPSサプライヤが持てる可能性がある。
- 出力を個体単位の再検査、保留、工程確認へ転記しやすい。
- 既存のEPS EOLやモータ試験には、測定値、効率、NVH、torque-speed、レポート出力などの構造化データがあり、Kaggle型の読み替え対象として自然である。

止める条件:

- 上位リスク個体を出しても、再検査、保留、工程確認の判断が変わらない。
- 既存SPC、MES、BI、品質管理で同じ判断が既にできる。
- featureが匿名化されすぎて、工程確認の説明に落ちない。
- EPS故障予測、保証費削減、root cause断定を言い始める。

ただし今回の主目的が工程検査でないなら、ここを最優先にしない。
KGL001は「製造・EOL検査の別枝」として保存し、実使用条件の読み取りではKGL003、KGL005、KGL006を先に見る。

別枝として進める場合の次アクション:

> Bosch型proxyを作り、上位リスク個体、工程グループ説明、再検査/保留/工程確認への転記1枚を作る。

### KGL002: Mercedes-Benz Greener Manufacturing

KGL002は、評価時間短縮の枝では有力である。
Mercedes-Benzの課題は、匿名化された車両構成からテストベンチ時間を予測し、試験時間を減らすものだった。
これは品質そのものではなく、評価や検査の計画を良くする課題である。

EPSサプライヤに読み替えると、variant、software、calibration、機能構成、診断設定、試験セットから、bench、HILS、EOLの評価時間や試験負荷を見積もる話になる。
出力は「この構成は時間がかかりそう」「この試験順序では待ちが増えそう」という評価計画向けの情報である。

残す理由:

- 目的変数が業務時間に直結している。
- EPS評価でもvariant、software、calibration、試験セットは増えやすい。
- KGL001ほど品質判断に直結しないが、評価計画やrelease gateには貼れる可能性がある。

弱い理由:

- 既存の評価計画、試験管理、HILS運用で十分かもしれない。
- 評価時間のばらつきが小さい場合、予測しても業務が変わらない。
- 構成情報だけでなく、設備空き、治具、担当者、試験失敗時の再実行など、Kaggle外の要因が効く可能性がある。

ただし今回の主目的が実使用条件やEPS product valueの読み取りなら、KGL002も最優先ではない。
KGL002は、後で評価計画やHILS/bench負荷の話に戻る場合の材料として残す。

別枝として進める場合の次アクション:

> KGL001を先に進め、KGL002は「評価時間のばらつきが業務判断を変えるか」を見る補助テーマとして残す。

### KGL003: OBD-II / CAN driving behavior

KGL003は切らない。
OBD-II/CANで運転行動や利用状態を分類するデータは、低速高操舵、急操舵、速度帯、停止発進のような使用条件proxyにはなる。

ただし、EPS内部のDTC、freeze frame、assist state、limit state、thermal state、EOL結果、返却品結果は見えない。
そのため、EPS内部故障や診断不足の証拠にはならないが、実使用条件を読む材料にはなる。

使い道は、公開CAN/OBDから速度帯、加減速、stop-start、急操舵に近い操作を抽出し、EPS評価scenarioや顧客説明の問いに変換することである。
ここで見るべきことは、モデル精度ではなく「どんな使用条件familyを作れるか」である。

### KGL004: Car-Hacking Dataset

KGL004は切らないが、境界を置く。
CAN trafficからnormal/attackを分けるデータは、通信異常や攻撃検出の参考にはなる。
公開元の説明でも、DoS、fuzzy attack、gear/RPM spoofingのようなメッセージ注入を扱っている。

しかし、これは既存のvehicle cyber、IDS、TARA、CSMS、ISO/SAE 21434支援に近い。
このRepoでは、汎用cyber/SBOM/CVE支援を既にKill寄りに下げている。
したがって、KGL004から新しい汎用cyber商品を作らない。

使ってよいのは、診断通信、異常通信、security access、禁止主張を考えるときの参考までである。
EPSサプライヤとしては、「通信異常を検出できる」と売るのではなく、「この種の通信異常をEPS状態説明や診断コンテンツの根拠にしてよいか / いけないか」を確認する材料として使う。

### KGL005: Steering angle / behavioral cloning

KGL005は切らない。
behavioral cloningやself-driving car向けのデータは、画像などから操舵角や操舵要求を推定する。
これは操舵需要proxyとしては面白い。

ただし、話の中心はADASや自動運転に寄りやすい。
EPSの内部状態や診断不足も見えない。

それでも、操舵要求そのものを公開proxyとして見られる点は重要である。
EPSサプライヤの問いに戻すなら、「どんな操舵角、操舵変化、速度条件を評価scenarioや異常時説明に入れるべきか」を見る。
ADAS制御モデルを作るのではなく、EPSが晒される操舵需要の棚卸しに使う。

### KGL006: PVS passive vehicular sensors

KGL006は切らない。
PVSは、加速度、ジャイロ、GPS、カメラなどの受動的な車両センサから路面種別や走行環境を分類する方向のデータである。
路面、振動、使用環境を考えるには使える。

しかし、EPS内部の不良、EOL結果、DTC、assist state、thermal stateを直接示すものではない。
したがって、EPS内部状態の主証拠にはならない。

使い道は、路面、振動、速度、環境条件を、EPS負荷条件や評価scenarioの外部条件に変換することである。
KGL003の運転行動、KGL005の操舵要求と組み合わせると、公開proxyだけで「実使用条件family」を作れる可能性がある。

## 解決策

初期解決策は、商品名を付けた外販サービスではない。
まず作るものは、KGL003、KGL005、KGL006を中心にした実使用条件の棚卸しである。

1. KGL003から、速度帯、stop-start、急加減速、急操舵に近い使用条件familyを作る。
2. KGL005から、操舵角、操舵変化、操舵要求のfamilyを作る。
3. KGL006から、路面、振動、走行環境のfamilyを作る。
4. KGL004から、通信異常や診断アクセスに関して言ってよいこと / 言ってはいけないことを確認する。
5. それらを、EPS評価scenario、診断コンテンツ質問、顧客説明質問、禁止主張リストに落とす。
6. KGL001/002は、製造・EOL検査または評価時間短縮の別枝として保存する。

## Required Output Shape

| Field | 内容 |
|---|---|
| Market demand | EPSサプライヤが、公開情報だけで実使用条件、操舵要求、路面・環境、通信異常を読み、評価scenario、診断コンテンツ、顧客説明、禁止主張へ変換したい。 |
| Evidence signal | OBD-II/CANは運転行動、steering angle / behavioral cloningは操舵要求、PVSは路面・環境、Car-Hackingは通信異常を目的変数または分類対象にしている。 |
| Hypothesis | Kaggleの問題設定を読むことで、EPS内部状態は見えなくても、EPSが晒される実使用条件familyと、評価・診断・説明に入れるべき問いを作れる。 |
| Solution | KGL003、KGL005、KGL006から実使用条件familyを作り、KGL004で通信異常の境界を確認する。KGL001/002は製造・評価効率の別枝として保存する。 |
| Buyer / user | EPSサプライヤ内の評価企画、HILS/bench、診断コンテンツ担当、顧客技術説明担当、software/calibration release gate。 |
| Why supplier can play | EPS内部故障を断定せず、公開proxyから評価scenarioや禁止主張を作るだけなら、OEM保証DBやfleet dataに直接依存しないため。 |
| EPS supplier conclusion | 外販商品としてはまだ売らない。次はKGL003/005/006を中心に、実使用条件familyとEPSサプライヤ向け質問表を作る。KGL004は境界確認。KGL001/002は別枝。 |
| Demo | KGL003/005/006から20-50件の使用条件familyを作り、各familyを評価scenario、診断質問、顧客説明質問、禁止主張へ対応付ける。 |
| What not to claim | EPS故障予測、内部状態推定、DTC不足の断定、保証費削減、root cause断定、ADAS制御モデル化、汎用cyber商品化。 |
| Kill criteria | 使用条件familyがEPS評価・診断・説明の問いに転記できない、単なる公開データ紹介になる、内部状態や故障原因を断定し始める、OEM/fleet/service outcomeが必要になる。 |

## 買い手 / 利用者

初期の利用者はOEM、fleet、ドライバーではない。
EPSサプライヤ内の以下である。

- 評価計画
- HILS/bench担当
- 診断コンテンツ担当
- 顧客技術説明担当
- software/calibration release gate担当

KGL003、KGL005、KGL006は、評価計画、HILS/bench、顧客技術説明に効く。
KGL004は、診断コンテンツ、security access、禁止主張の境界確認に効く。
KGL001は製造品質、工程設計、EOL検査の別枝であり、KGL002は評価時間短縮の別枝である。

## 検証方法

内部資料を使わない現行ルールでは、実EPSデータで効果検証しない。
公開Kaggle課題を使い、次だけを見る。

| 見ること | 進める条件 | 止める条件 |
|---|---|---|
| 目的変数 | 運転行動、操舵要求、路面・環境、通信異常のように、評価・診断・説明の問いに変換できる | 精度指標だけで、EPSサプライヤの問いが増えない |
| 入力データ | 公開proxyとして使えるCAN/OBD、操舵角、受動センサ、通信trafficに近い | OEM保証DB、fleet data、service outcomeがないと何も言えない |
| 出力 | 使用条件family、評価scenario、診断質問、顧客説明質問、禁止主張のどれかに貼れる | 何となく面白いデータ紹介で終わる |
| 既存業務との差分 | 公開情報だけで実使用条件から質問表を作れる | 既存評価項目や一般論の言い換えになる |
| 禁止主張 | 故障予測やroot cause断定を避けられる | EPS故障予測、保証費削減、EOL省略を言い始める |

## EPSサプライヤとしての結論

EPSサプライヤとして売るなら、現時点ではまだ売らない。
ただし、検証用の公開proxyとしてKGL003、KGL005、KGL006は進めてよい。

EPSサプライヤとして実施できること:

- OBD/CAN、操舵角、受動車両センサから実使用条件familyを作る。
- そのfamilyを評価scenario、診断コンテンツ質問、顧客説明質問、禁止主張に対応付ける。
- KGL004を通信異常やsecurity accessの境界確認に使う。
- KGL001/002は、製造・EOL検査または評価時間短縮へ寄せる別枝として保存する。

EPSサプライヤとして言ってはいけないこと:

- KaggleでEPS故障予測を実証できる。
- 保証費を下げられる。
- root causeを自動断定できる。
- 公開proxyからEPS内部状態やDTC不足を断定できる。
- ADAS制御モデルや汎用cyber商品として売れる。

初期対象外に置くもの:

- OEM保証DBやfleet dataを使う故障予測
- ドライバー向け交換時期通知
- 汎用vehicle cyber / IDS商品
- ADAS/自動運転向け操舵制御モデル
- 路面分類そのものの外販

次に見せるなら、評価企画、HILS/bench、診断コンテンツ担当に、KGL003/005/006から作る実使用条件familyの1枚を見せる。
KGL004は、診断通信やsecurity accessの境界確認として後続で見る。

## Kill条件

このKaggle枝は、次のどれかに当たれば止める。

- KGL003/005/006から作った使用条件familyが、評価scenario、診断質問、顧客説明質問に転記できない。
- KGL004が、通信異常やdiagnostic/security accessの境界確認ではなく、汎用cyber商品化へ流れる。
- 公開proxy紹介で終わり、EPSサプライヤが次に確認すべき質問にならない。
- 既存評価項目や既存診断仕様の一般論の言い換えで終わる。
- OEM保証DB、fleet data、service outcomeを必要とする方向へ戻る。
- EPS故障予測、保証費削減、root cause断定、内部状態断定を主張し始める。

## CoVe

| 検証質問 | 回答 | 反映 |
|---|---|---|
| 市場需要から始まっているか | Yes。需要は工程検査ではなく、公開proxyから実使用条件、操舵要求、路面・環境、通信異常を読み、評価・診断・説明の問いに変換することに置いた。 | KGL003/005/006を主確認対象に戻した。 |
| 単に事例紹介になっていないか | No。Kaggleのデータ内容ではなく、目的変数とEPSサプライヤ成果物への転記先を読んだ。 | problem-setting lensとして扱った。 |
| 買い手の業務成果物に転記できるか | KGL003/005/006は評価scenarioや顧客説明質問へ転記できる可能性がある。KGL004は診断通信や禁止主張の境界確認に使える。KGL001/002は別枝。 | Stopではなく、用途別にKeepへ修正した。 |
| EPSサプライヤの立場に戻っているか | Yes。OEM保証DBやfleet dataを使わず、公開proxyから質問表を作る範囲に絞った。 | EPS supplier conclusionを修正した。 |
| 既存業務との差分を断定しすぎていないか | 断定していない。既存評価項目や既存診断仕様の一般論で終わるならKillとした。 | Kill条件に既存業務の言い換えを入れた。 |
| 自然言語で読んでも結論が分かるか | Yes。工程検査が目的ではないため、KGL003/005/006を実使用条件proxy、KGL004を境界確認、KGL001/002を別枝と書いた。 | ID別判断表を修正した。 |

## Sources

- Kaggle: Bosch Production Line Performance, https://www.kaggle.com/competitions/bosch-production-line-performance
- Mangal and Kumar: Using Big Data to Enhance the Bosch Production Line Performance, https://arxiv.org/abs/1701.00705
- Kaggle: Mercedes-Benz Greener Manufacturing, https://www.kaggle.com/competitions/mercedes-benz-greener-manufacturing
- Kaggle: OBD-II & CAN-Based Driving Behavior Dataset, https://www.kaggle.com/datasets/isaygerardozamora/obd-ii-and-can-based-driving-behavior-dataset
- Kaggle: Car-Hacking Dataset, https://www.kaggle.com/datasets/pranavjha24/car-hacking-dataset
- HCRL: Car-Hacking Dataset, https://ocslab.hksecurity.net/Datasets/CAN-intrusion-dataset
- Kaggle: Udacity Self Driving Car - Behavioural Cloning, https://www.kaggle.com/datasets/andy8744/udacity-self-driving-car-behavioural-cloning
- Kaggle: PVS - Passive Vehicular Sensors Datasets, https://www.kaggle.com/datasets/jefmenegazzo/pvs-passive-vehicular-sensors-datasets
- Klotz: End-of-line testing for electric power steering systems, https://www.klotz.de/en/competencies/end-of-line-test-bench-for-electric-power-steering-eps-epas/
- 4Q Systems: EPS Motor Testing System for EOL and R&D, https://www.4q-systems.com/products/electric-motor-test-systems/motor-test-bench-for-eps-motors/
