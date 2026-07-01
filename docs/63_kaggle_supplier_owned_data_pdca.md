# Kaggleから製造・評価データ仮説を深掘りする

## 結論

今回の深掘りで、Kaggleを使う方向は少し前に進めてよい。
ただし、進める対象はEPSの市場故障予測ではない。

進めるなら、EPSサプライヤが自分で持てる製造、工程検査、最終検査、EOL検査、bench/HILS評価のデータを使い、次の判断を助ける方向である。

- どの個体を再検査、保留、工程確認に回すべきか
- どの工程や測定値が後工程の不良や再試験に効いていそうか
- どのvariant、software、calibration、機能構成が評価時間を増やしそうか
- 評価計画や試験順序をどう組むと、品質を落とさずに待ち時間を減らせるか

一番筋が良いのは、**製造・EOL検査の早期不良候補抽出**である。
次点は、**bench/HILS/EOL評価時間の見積もり**である。

この2つは、Kaggleコンペの課題設定と、EPSサプライヤが持てるデータの境界が合いやすい。
反対に、OBD-II、CAN、steering angleの公開データからEPS故障や診断不足を証明する方向は、今回も止める。

## 何を判断しているか

内部資料を使わない現行方針では、対象EPSの実データを直接見ない。
そのため、公開情報だけで「この商品は売れる」とは言わない。

今回判断するのは、次の小さな問いである。

> Kaggleコンペの課題設定を使って、EPSサプライヤが持てる製造・検査・評価データに近い業務痛みを見つけられるか。

答えは、条件付きでYesである。

Boschの製造ライン不良予測は、工程・検査・EOLの「後で落ちる個体を早く見つけたい」という需要に近い。
Mercedes-Benzのテスト時間予測は、多品種構成の「評価やベンチ試験の時間を読みたい」という需要に近い。

ただし、どちらも既存の工程管理、統計的工程管理、品質管理、評価計画の業務と重なる。
価値が出るのは、既存業務で見えていない「個体単位の再検査優先順位」「工程単位の疑わしさ」「variant単位の評価時間見積もり」を、現場の判断に貼れる場合だけである。

## 市場需要

公開情報から見える需要は、次の通りである。

製造側では、EOL検査は最終品質確認として重要だが、最後に不良が見つかると手戻り、再検査、廃棄のコストが大きい。
工程中の測定や試験データから、後で落ちる個体や工程を早く見つけたい需要がある。

評価側では、車両や部品のvariantが増え、softwareやcalibrationの組み合わせも増える。
すべてを同じ厚さで評価すると時間がかかる。
一方で、安全・品質を落とすわけにもいかない。
そのため、評価時間や試験負荷を事前に読み、試験計画や順序を組みたい需要がある。

EPSサプライヤに引き寄せると、需要はこうなる。

> EPSサプライヤは、製造・検査・評価データを持っている可能性がある。しかし、そのデータが個体保留、再検査、工程改善、評価時間見積もりに十分使えているとは限らない。Kaggle型の課題設定を使えば、公開データだけでその業務仮説を小さく試せる。

## 未解決の痛み

今回残す痛みは、次の5つである。

1. EOLで落ちるまで怪しい個体が見えない
2. 工程測定値は多いが、どれが後工程のfailやretestに効くか分からない
3. 再検査する個体、保留する個体、工程確認する個体の優先順位が説明しにくい
4. variantやsoftware/calibration構成ごとの評価時間が読みづらい
5. データ分析結果が、工程改善や評価計画の帳票に転記されない

この痛みは、EPS故障予測よりもサプライヤの手元に近い。
ただし、既存の工程管理で既に解けている可能性も高い。

## 仮説

### 仮説1: 製造・EOL検査の早期不良候補抽出

EPS製造ライン、工程検査、EOL検査の測定データから、後工程でfail、retest、保留になりそうな個体を順位付けする。
出力は「故障予測」ではなく、「この個体は再検査または工程確認を先に見るべき」という現場向けの優先順位である。

買い手または利用者は、製造品質、工程設計、EOL検査、工場品質保証である。

これはBosch Production Line Performanceの課題設定に近い。
Boschの公開課題は、製造ラインの測定・試験データから内部不良を予測するものだった。
EPSに置き換えるなら、工程データとEOL結果をつなぎ、どこで怪しくなったかを早めに見る用途になる。

### 仮説2: bench/HILS/EOL評価時間の見積もり

EPSのvariant、software、calibration、機能構成、診断設定、試験セットから、bench/HILS/EOL評価時間や試験負荷を見積もる。
出力は「この構成は時間がかかりそう」「この試験順序にすると待ち時間が増えそう」という評価計画向けの情報である。

買い手または利用者は、評価計画、HILS/bench担当、software/calibration release gate担当である。

これはMercedes-Benz Greener Manufacturingの課題設定に近い。
Mercedes-Benzの公開課題は、車両構成からテストベンチ時間を予測するものだった。
EPSに置き換えるなら、評価時間や試験計画の見積もりに使う。

### 仮説3: 工程・評価データの説明用1枚

モデル精度そのものではなく、工程、検査、評価の判断に貼るための1枚を作る。
例えば、以下を1枚にする。

- 何を予測しているか
- どの測定値や構成が効いていそうか
- どの個体や構成を先に見るべきか
- 何を断定してはいけないか
- 既存工程管理や既存評価計画と何が違うか

これは、Kaggle精度競争で終わらせないための仮説である。

## 解決策

初期解決策は、SaaSや大きなツールではない。
次の3点を作る。

1. Kaggle課題をEPSサプライヤ業務へ読み替える対応表
2. 製造不良候補抽出と評価時間見積もりの2つの最小ワークフロー
3. 現場に貼るための判断1枚の型

現時点で言える価値は、以下までである。

> 製造・検査・評価データを、個体保留、再検査、工程確認、評価計画の判断に接続できるかを、公開Kaggle課題で先に試せる。

まだ言ってはいけないことは、以下である。

- EPS故障予測ができる
- 保証費を下げられる
- EOL検査を省略できる
- root causeを断定できる
- 既存工程管理より優れている

## PDCA

### 1周目: Kaggle課題の読み替え

Plan:
Kaggleの自動車系コンペを、公開代替データではなく「企業が外に出した目的変数」として読む。

Do:
Bosch Production Line Performance、Mercedes-Benz Greener Manufacturing、OBD-II/CAN、Car-Hacking、steering angle系を比較した。

Check:
BoschとMercedes-Benzは、製造不良とテスト時間という業務判断に近い目的変数を持つ。
OBD-II/CANやsteering angleは、使用条件proxyにはなるが、EPSサプライヤの製造・評価判断には遠い。

Act:
Bosch型とMercedes型だけを次候補に残す。
OBD-II/CAN、Car-Hacking、steering angleは主商品候補から外す。

### 2周目: EPSサプライヤ業務への接続

Plan:
Bosch型とMercedes型が、EPSサプライヤのどの部署・帳票・判断に接続できるかを見る。

Do:
EOL検査、EPS/EPAS向けEOL test bench、品質データ蓄積、bench/HILS評価時間の公開情報を確認した。

Check:
EPS向けEOL試験は、100%検査、機能・音響・通信、品質データ保存まで既に存在する。
そのため、「EOL試験を作る」は価値にならない。
価値があるとすれば、工程中のデータとEOL結果をつなぎ、再検査や工程確認の優先順位を出すことである。

Act:
主仮説を「EOL試験の追加」ではなく、「製造・工程・EOLデータの判断支援」へ修正する。

### 3周目: Kill条件で絞る

Plan:
既存工程管理、統計的工程管理、品質管理、評価計画の言い換えで終わらないかを確認する。

Do:
仮説ごとに、業務転記先、既存業務との差分、必要データ、Kill条件を表にした。

Check:
仮説1は、個体単位の再検査・保留・工程確認へ接続できるため、まだ検証価値がある。
仮説2は、評価時間のばらつきが大きく、variantやsoftware/calibrationで説明できる場合だけ価値がある。
仮説3は、単独商品ではなく、仮説1/2の出力を現場に貼るための補助である。

Act:
次に進めるなら、Bosch型を最優先にする。
Mercedes型は2番手に置く。
説明1枚は、精度よりも業務転記性を見るために同時に作る。

## 検証結果

| 仮説 | 市場需要 | EPSサプライヤが持てるデータに近いか | 既存業務との差分 | 現時点判断 |
|---|---|---|---|---|
| 製造・EOL検査の早期不良候補抽出 | 強い。EOLで落ちる前に怪しい個体を見たい | 近い。工程測定、EOL結果、retest、hold、scrapはサプライヤ側にあり得る | 既存SPCより個体単位の再検査優先順位を出せるなら差分あり | Proceed to proxy |
| bench/HILS/EOL評価時間の見積もり | 中程度。評価計画や待ち時間削減の需要はある | やや近い。variant、software、calibration、試験セットはサプライヤ側にあり得る | 評価時間のばらつきが小さいなら価値なし | Hold / second |
| 工程・評価データの説明用1枚 | 補助的。モデル結果を現場判断に貼る需要 | 近い。既存データから作る | 既存品質報告や評価計画に貼れなければ価値なし | 仮説1/2の付属 |
| OBD/CAN使用条件proxy | 弱い。使用条件を見るだけでは製造・評価判断に遠い | 遠い。車両利用データ寄り | 過去の公開proxyと同じ | Stop as main |
| CAN cyber/anomaly demo | 需要はあるが既存cyber領域 | 近い場合もあるが既存プレイヤーが強い | 過去にKill寄り | Stop as main |

## 次に作るべき最小デモ

次にやるなら、Bosch型を使って以下を作る。

目的:

> 工程・検査データから、後工程でfail/retest/holdになりそうな個体を順位付けし、EOL検査や工程確認の優先順位へ転記できるかを見る。

入力:

- 個体ID
- 工程ID
- 測定値
- 試験結果
- EOL pass/failまたはretest/hold/scrapラベル

出力:

- 個体ごとの要注意スコア
- どの工程・測定グループが効いていそうか
- 再検査・保留・工程確認の推奨
- 断定禁止事項

公開Kaggleでできること:

- 製造ライン不良予測のproxy pipelineを作る
- 予測精度だけでなく、上位何件を先に見ればfailを拾えるかを見る
- station / feature group単位で、工程確認に使える説明を作る

公開Kaggleでできないこと:

- EPS固有の工程差分を断定する
- 実EOL省略を主張する
- root causeを断定する
- 保証費削減を主張する

## Kill条件

次のどれかに当たるなら、この方向も止める。

- 予測精度は出ても、再検査、保留、工程確認、評価計画に貼れない
- 既存SPC、BI、MES、品質管理システムで同じ判断が既にできる
- データが匿名化されすぎて、工程改善や評価計画への説明が作れない
- EPSサプライヤが持つデータではなく、OEM保証DBやfleet dataが必要になる
- 製造品質または評価計画の利用者が具体化しない
- 「EOL検査を省ける」「故障予測できる」「保証費を下げられる」と言い始める

## EPSサプライヤとしての言い方

言ってよいこと:

> Kaggleの製造不良予測とテスト時間予測は、EPSサプライヤが自分で持てる製造・検査・評価データに近い。ここから、出荷後の故障予測ではなく、出荷前の再検査優先順位、工程確認、評価時間見積もりを支援する仮説を作れる。

まだ言ってはいけないこと:

> 公開KaggleでEPSの故障予測ができる。

> EOL検査を減らせる。

> 既存工程管理より優れている。

> root causeを自動特定できる。

## 現時点判断

この方向は、過去の故障予測や診断証跡追加よりは筋が良い。
理由は、OEMデータやfleet dataではなく、EPSサプライヤが持てる製造・評価データに寄せられるためである。

ただし、外販商品としてはまだ早い。
まず作るべきは、Bosch型の公開データを使った最小デモである。
そのデモで、精度ではなく「現場の判断がどう変わるか」を見せる。

次アクション:

> Bosch Production Line Performance型のproxyで、上位リスク個体抽出、工程グループ説明、再検査/保留/工程確認への転記1枚を作る。

## 参照

- Bosch Production Line Performance, https://www.kaggle.com/competitions/bosch-production-line-performance
- Using Big Data to Enhance the Bosch Production Line Performance, https://arxiv.org/abs/1701.00705
- Machine Learning Orientation: Bosch Production Line Performance summary, https://machinelearningintro.uwesterr.de/bosch-production-line-performance.html
- Mercedes-Benz Greener Manufacturing, https://www.kaggle.com/c/mercedes-benz-greener-manufacturing
- Mercedes-Benz Bench Test Time Estimation, https://noiselab.ucsd.edu/ECE228_2018/Reports/Report11.pdf
- Klotz EPS/EPAS End-of-Line test bench, https://www.klotz.de/en/competencies/end-of-line-test-bench-for-electric-power-steering-eps-epas/
- Dewesoft End-of-Line Testing overview, https://dewesoft.com/blog/end-of-line-testing
- Acerta automotive EOL testing article, https://acerta.ai/articles/an-introduction-to-automotive-end-of-line-testing/
