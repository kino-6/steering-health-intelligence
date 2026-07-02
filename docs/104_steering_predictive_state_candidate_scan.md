# Steering Predictive State Candidate Scan

## 結論

このブランチでは、Boschが使っている言葉に合わせて `predictive diagnostics`、`predictive maintenance`、`vehicle health` を正面から扱う。
ただし、最初に売るものを「EPS残寿命」や「交換時期予測」に戻すのはまだ早い。

公開情報から見える有望な方向は、次である。

> 操舵系について、故障前に早く分かると嬉しい注意状態を定義し、それを点検優先度、診断読み順、不要交換の回避、顧客説明、再発監視へつなげる。

この方向なら、Boschが言う予測診断の市場文脈に乗りつつ、EPSサプライヤが自分の持ち場で言えることへ戻せる。
今回の候補表は [data/steering_predictive_state_candidates.tsv](../data/steering_predictive_state_candidates.tsv) に置く。

## このブランチで戻してよい観点

このブランチでは、次の言葉を使ってよい。

- `predictive diagnostics`
- `predictive maintenance`
- `vehicle health`
- `remaining lifetime`
- `failure prediction`

ただし、同じ段落で必ず証拠レベルを分ける。

- Boschが一般論として言っている予測
- fleet / cloud / connected vehicleで成立する予測
- EPS / SbWで公開情報から言える予測
- EPSサプライヤが初期に商品化してよい予測

現時点で、EPSサプライヤが初期に商品化してよい候補は「交換時期予測」ではない。
「注意状態の早期説明」と「診断・点検行動への変換」である。

## Rule Check

今回の判断では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Kaggle / Public Proxy Predictive Value Rule`
5. `OEM Usage Translation Rule`
6. `Mandatory Rule Check Before Stop / Kill / Archive`

この文書では、StopやArchiveを出していない。
ただし、予測という言葉を戻すため、次を確認する。

- Boschが使う予測語は正面から扱う
- ただし、Boschのfleet / cloud文脈をEPS単体へそのまま移植しない
- 公開proxyだけでEPS残寿命や交換日が出るとは言わない
- 内部DTCやfreeze frameが見えないことを主Kill理由にしない
- 代わりに、操舵系として早く分かると嬉しい状態があるかを見る

## 市場需要

Bosch / Uptakeの2026年発表では、fleetのdowntime、maintenance cost、vehicle uptime、parts planning、maintenance workflow、repair feedback loopが明確に出ている。
Bosch Predictive Diagnosticsでは、connected vehicle dataとcloud informationからcomponent / system condition、faults、probable remaining lifetime、maintenance forecastを扱う。
Bosch Cloud and predictive diagnosticsでは、deep component levelのanomalies / wear、behavior-based failure prediction、component-specific load and diagnostic featuresが出ている。

つまり市場側には、故障してから直すのではなく、状態を早く把握して整備行動を決めたい需要がある。

出典:

- Bosch Media Service US, `Bosch strengthens U.S. mobility services portfolio`, 2026-03-19
  <https://us.bosch-press.com/pressportal/us/en/press-release-30080.html>
- Bosch Mobility, `Predictive Diagnostics`
  <https://www.bosch-mobility.com/en/solutions/diagnostics/predictive-diagnostics/>
- Bosch Mobility, `Cloud and predictive diagnostics`
  <https://www.bosch-mobility.com/en/solutions/software-and-services/cloud-and-predictive-diagnostics/>

## 公開情報から見える操舵系の注意状態

### 1. 熱保護に近い状態

公開サービス情報では、過度なlock-to-lock操作により、thermal protectionが働き、power steering control moduleが一時的にsteering motorをoff-lineにすることがあると説明されている。
これは正常な保護動作として説明され、部品交換ではなく診断上の切り分けが必要になる。

出典:

- NHTSA public file, GM bulletin `Power Steering Inoperative / Steering Wheel Hard to Turn`, DTCs C0176 / C0476
  <https://static.nhtsa.gov/odi/inv/2010/INRD-RQ10004-45543P.pdf>
- NHTSA public file, `Normal Operating Characteristics of Electric Power Steering System During Extended Lock-to-Lock Turns`
  <https://static.nhtsa.gov/odi/inv/2010/INRD-PE10005-39797P.pdf>

EPSサプライヤとしての意味:

これは、EPS寿命予測ではない。
しかし「高負荷操舵が続き、熱保護に近い状態に入った / 入りそう」という注意状態なら、点検優先度、診断読み順、不要交換回避、顧客説明に使える可能性がある。

### 2. 低電圧 / 高電圧 / 過温度によるreduced assist

Ford EPASの公開資料では、PSCMがlow/high battery voltageやover-temperature concernsを検出した場合に、EPASがreduced steering assist modeへ入ると説明されている。
同資料では、critical safety concernの場合や、reduced assistの原因が一定key cycle継続した場合にはmanual steering modeに入る説明もある。

出典:

- NHTSA public file, Ford EPAS material in PE12-017 Appendix
  <https://static.nhtsa.gov/odi/inv/2012/INRD-PE12017-56147P.pdf>

EPSサプライヤとしての意味:

これは、操舵系の注意状態としてかなり強い。
電圧、温度、reduced assist継続、key cycle、manual modeに近い状態を、故障断定ではなく「次に見るべき状態」として扱える可能性がある。

### 3. 他ECUや通信値の異常により操舵側が影響を受ける状態

GMの公開TSBでは、`Steering Assist Reduced` が表示され、DTC P0128 / U0401が出る場合が説明されている。
資料では、steering gearを交換しないよう注意し、ECMからのcoolant temperature signalがinvalidになった結果、steering module側の機能が影響を受けると説明している。

出典:

- NHTSA public TSB, GM `Information on Steering Assist Reduced Displayed on Driver Information Center - DTCs P0128 and U0401 Set`
  <https://static.nhtsa.gov/odi/tsbs/2017/MC-10137654-9999.pdf>

EPSサプライヤとしての意味:

これは「EPSが壊れた」ではなく、「操舵説明に必要な外部signalや通信contextが壊れている」状態である。
予測価値は、故障予測ではなく、誤交換回避、診断読み順、責任境界、サービス説明にある。

### 4. 電気接続 / harness / network由来の複合症状

GMの公開サービス情報では、reduced or loss of power steering assist、steering wheel jerks、Service Stabilitrak、engine stall、IPC / radio / HVAC blankなどが同時に出るケースが説明されている。
これらはEPS単体故障ではなく、電気接続やnetwork / cable問題として切り分ける必要がある。

出典:

- NHTSA public TSB, GM `Service Bulletin TECHNICAL`
  <https://static.nhtsa.gov/odi/tsbs/2020/MC-10181672-9999.pdf>
- NHTSA public TSB, GM PIT5405C
  <https://static.nhtsa.gov/odi/tsbs/2017/MC-10113356-9999.pdf>

EPSサプライヤとしての意味:

これは、vehicle health側で強い注意状態になりやすい。
操舵異常だけでなく複数ECU症状が同時に出る場合、EPS内部ではなく電源 / harness / networkを先に見る、という診断読み順価値がある。

### 5. steering gear温度上昇 / thermal protection / warning有無

Ford recall公開資料では、steering gear heat shield fastenerの問題によりsteering gearが高温にさらされ、thermal protection modeが働くとsteering assistが低下する可能性が説明されている。
場合によっては、connector meltによる急なloss of assistと警告表示も説明されている。

出典:

- NHTSA Part 573 Safety Recall Report 17V-530
  <https://static.nhtsa.gov/odi/rcl/2017/RCLRPT-17V530-1576.PDF>

EPSサプライヤとしての意味:

これは特定recallの話なので、一般化しすぎてはいけない。
ただし、熱環境、thermal protection、warning有無、assist reductionの関係を、予測診断の注意状態として考える材料になる。

### 6. DTC coverageと安全要求の接点

NHTSAのGeneric EPS functional safety assessmentでは、EPS system safety requirements、test scenarios、DTC coverageの領域が扱われている。
Steer-by-wireについても同様に、foundational steering systemとしてfunctional safety assessmentが公開されている。

出典:

- NHTSA, `Functional Safety Assessment of a Generic Electric Power Steering System With Active Steering and Four-Wheel Steering Features`, DOT HS 812 575
  <https://www.nhtsa.gov/sites/nhtsa.gov/files/documents/13501_812575_electricpowersteeringreport.pdf>
- NHTSA, `Functional Safety Assessment of a Generic Steer-by-Wire Steering System With Active Steering and Four-Wheel Steering Features`, DOT HS 812 576
  <https://www.nhtsa.gov/sites/nhtsa.gov/files/documents/13502_812576_steerbywire.pdf>

EPSサプライヤとしての意味:

これは予測診断の直接証拠ではない。
しかし、操舵系でどの状態をDTC、警告、fallback、degraded stateとして扱うかを、予測診断の注意状態へ翻訳する土台になる。

## 候補の優先順位

最初に深掘りするなら、優先順位は次である。

1. 熱保護に近い状態
2. 低電圧 / 高電圧 / 過温度によるreduced assist
3. 外部signal / 通信値異常により操舵説明が誤る状態
4. 電気接続 / harness / network由来の複合症状
5. DTC履歴、発生頻度、key cycleから見た再発監視
6. 特定hardware / thermal exposure由来の注意状態

理由は、1から4は、故障断定ではなく、診断読み順、点検優先度、不要交換回避、顧客説明に落ちやすいからである。
5は内部データが必要になりやすいが、予測診断の実装には重要である。
6はrecallや特定設計に寄るため、汎用商品にしにくい。

## ビジネス仮説

この観点で調査すると、ビジネス候補は次の形になる。

> EPS / SbWサプライヤが、操舵系の注意状態を「早く分かると嬉しい状態」として定義し、既存DTC、freeze frame、extended data、制御制限、電圧、温度、通信context、発生頻度、修理結果との関係を整理する短期assessment。

成果物は次に絞る。

1. 操舵系の注意状態候補表
2. 各状態に対して、既存診断で見えるもの / 見えないもの
3. 点検優先度、診断読み順、不要交換回避、顧客説明のどれに使えるか
4. 交換時期予測、残寿命、安全保証、原因断定に見えるため避ける表現
5. repair feedback loopで確認すべき結果

## 判定

この調査の現時点判断は `Proceed to internal screening` である。

このブランチでは、`predictive diagnostics` の言葉を使ってよい。
Boschがその言葉を使っているためである。
ただし、最初の商材はEPS交換日予測ではなく、操舵系の注意状態を定義し、整備・診断行動へ変換するreadiness確認に置く。

Proceed条件:

- 診断企画が、熱保護、電圧、通信、DTC履歴、fallbackのうち3つ以上を注意状態として扱える
- 品質改善またはサービス技術が、不要交換回避または診断読み順に使えると言える
- 既存DTC / freeze frame / extended dataで説明できる範囲と、追加で必要な範囲を分けられる
- repair feedback loopで、注意状態が本当に整備行動に役立ったかを検証できる

Hold条件:

- 注意状態は見えるが、既存診断や既存サービス資料と同じ表になる
- OEM / fleet / service側の行動にどうつながるかが曖昧
- steering-specificではなく汎用vehicle healthに吸収される

Stop候補:

- 価値説明がEPS交換日、残寿命、安全保証、root cause断定に戻る
- 熱、電圧、通信、DTC履歴の注意状態が、既存診断説明と区別できない
- feedback loopに一切つながらず、予測と言えない

Stop候補と書く場合も、最終Stopではない。
最終判断では、上位ルールに沿ったRule Checkを改めて書く。

## CoVe

| 検証質問 | 回答 | Confidence | 反映 |
|---|---|---:|---|
| 操舵系に早く分かると嬉しい注意状態はあるか | Yes。熱保護、低/高電圧、過温度、通信値異常、複合電気症状、DTC履歴が公開資料に出る。 | High | 候補表と優先順位に反映 |
| これはEPS寿命予測か | No。初期候補は寿命や交換日ではなく、点検優先度、診断読み順、不要交換回避、顧客説明に効く注意状態である。 | High | 結論と判定に反映 |
| Boschの予測語に戻してよいか | このブランチではYes。Boschがpredictive maintenance / predictive diagnosticsを明確に使っているため。ただしEPS単体へ直輸入しない。 | High | このブランチで戻してよい観点に反映 |
| EPSサプライヤが主語になれるか | Partial。操舵系の診断・制御・limit / fallback知識では主語になれるが、fleet運用DBやrepair feedback loopはOEM / service依存である。 | Medium | ビジネス仮説とHold条件に反映 |
| 次に何を確認すべきか | 既存DTC / freeze frame / extended dataで、熱・電圧・通信・reduced assist履歴をどこまで説明できるか。 | High | 次アクションに反映 |

## EPSサプライヤとしての言い方

言ってよいこと:

> Boschがpredictive diagnostics / vehicle healthを明確に打ち出しているため、操舵系でも「故障前に早く分かると嬉しい状態」を定義する価値がある。初期候補は、熱保護に近い状態、低/高電圧や過温度によるreduced assist、外部signalや通信値異常、電気接続やnetwork由来の複合症状、DTC履歴や再発間隔である。これらは、交換時期予測ではなく、点検優先度、診断読み順、不要交換回避、顧客説明に使えるかを確認する。

まだ言ってはいけないこと:

> 公開情報だけでEPS残寿命や交換日を予測できる。

> 熱保護、低電圧、通信異常が出ればEPS故障である。

> 操舵系の注意状態を定義すれば、安全保証、root cause断定、保証費削減ができる。

> EPSサプライヤ単独でfleet predictive maintenance platformを外販できる。

## 次アクション

次は、この候補を質問票にする。
最初のレビュー対象は、診断企画、品質改善、サービス技術である。

最初に聞く質問は2つでよい。

1. 熱、電圧、通信、DTC履歴、fallbackのうち、故障前に早く分かると嬉しい操舵系状態はどれか
2. それは既存DTC / freeze frame / extended data / service note / repair resultで、どこまで説明または検証できるか
