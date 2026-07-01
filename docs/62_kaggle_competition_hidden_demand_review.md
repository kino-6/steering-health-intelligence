# Kaggleコンペを隠れた需要として読む

## 結論

Kaggleには有用な手札がある。
ただし、今まで探していたような「EPSの市場故障を公開データで予測する」用途ではない。

有用なのは、Kaggleのデータそのものよりも、企業がコンペとして外に出した課題を読むことだ。
コンペは、誰かが「この目的変数を当てたい」「この業務時間を減らしたい」「この不良を早く見つけたい」と定義している。
つまり、普通の公開データよりも、隠れた業務需要を読みやすい。

現時点で最も筋が良いのは、以下の2つである。

1. 製造ラインや最終検査で、不良になりそうな個体を早く見つける
2. 評価・検査・ベンチ試験にかかる時間を、構成情報や過去データから見積もる

これはEPSサプライヤ視点に合う。
なぜなら、製造ライン、工程検査、最終検査、ベンチ評価、HILS評価のデータは、OEMの保証DBやfleet dataではなく、サプライヤ側が持てる可能性があるからである。

一方で、Kaggleを使って「EPSの故障予測ができる」と主張するのはまだ無理である。
公開Kaggleデータには、対象EPSのDTC、freeze frame、assist電流、motor電流、limit状態、返却品判定、保証ラベルがほぼない。
したがって、EPS市場故障や劣化兆候の実証には使わない。

## 何を判断しているか

ここで判断しているのは、内部資料なしでも次の探索に進める公開データがあるかである。

前回までの探索では、内部資料がないため、既存診断や既存評価との差分を確認できず止まっていた。
Kaggleを使う場合も、同じ罠がある。
公開CANやOBDデータを見ても、EPS内部の不足診断や故障原因は分からない。

ただし、Kaggleコンペは少し違う。
コンペには、企業が外部に解いてほしい形で置いた課題がある。
その課題を読むと、以下のような業務需要が見える。

- 不良を後工程で見つけるのではなく、工程中の測定値から早く見つけたい
- 多品種構成で、評価や検査にかかる時間を減らしたい
- 大量の匿名化された工程・構成データから、品質や時間に効く特徴を見つけたい
- ただの可視化ではなく、現場の判断に使える予測値や優先順位を作りたい

この需要は、EPSサプライヤの製造品質、工程設計、最終検査、評価計画に接続しやすい。

## 候補の読み替え

| 候補 | Kaggle上の課題 | 隠れた需要 | EPSサプライヤでの読み替え | 判断 |
|---|---|---|---|---|
| Bosch Production Line Performance | 製造ラインの測定・試験データから内部不良を予測する | 工程中の大量データを使って、不良や手戻りを早く見つけたい | EPS製造、工程検査、最終検査、EOL検査で、出荷前に怪しい個体や工程を見つける | 最有力 |
| Mercedes-Benz Greener Manufacturing | 車両構成からテストベンチ時間を予測する | 多品種構成の評価・検査時間を減らしたい | EPSのvariant、software/calibration、機能構成から、bench/HILS/EOL試験時間や優先順位を見積もる | 有力 |
| OBD-II / CAN driving behavior dataset | OBD-II/CANで運転行動を分類する | 車両利用状態や運転スタイルをデータで分けたい | 低速高操舵や急操舵など、使用条件のproxyを作る | 入力止まり |
| CAN intrusion dataset | CAN通信から攻撃や異常を検出する | 車載ネットワーク異常を検出したい | 診断アクセスや通信異常の検出デモには使える | 既存cyber領域と被るため主商品にしない |
| steering angle / behavioral cloning dataset | 画像などから操舵角を推定する | 自動運転・ADAS向けに操舵要求を推定したい | steering demand proxyにはなるが、EPS品質・診断とは遠い | 優先度低 |

## 新しい仮説

今までの「市場に出た車両からEPSの劣化や故障兆候を出す」という方向は弱かった。
公開データだけでは、EPS内部の故障ラベルや診断差分が見えないためである。

Kaggleから見える新しい仮説は、より手前に置く。

> EPSサプライヤが自分で持つ製造、工程検査、最終検査、ベンチ評価、HILS評価のデータを使い、不良候補、再試験候補、評価時間、試験優先順位を出す。

これは、故障予測ではない。
市場に出た車の残寿命を当てる話でもない。
サプライヤ内部の製造品質と評価効率を上げる話である。

## 市場需要

自動車部品サプライヤは、多品種化、ソフトウェア化、検査項目増加、品質要求の高まりにより、製造・検査・評価の負荷が増えている。
Kaggle上でBoschが製造不良予測を、Mercedes-Benzがテストベンチ時間短縮を課題化したことは、この種の負荷が実務上の痛みであることを示す公開シグナルになる。

ここでの需要は、ドライバー向けの故障通知ではない。
EPSサプライヤ内部の品質部門、工程設計、EOL検査、評価計画、HILS/bench担当が、限られた時間で怪しい個体・怪しい工程・時間のかかる構成を先に見たい、という需要である。

## 未解決の痛み

公開情報だけで見る限り、次の痛みがありそうである。

- 工程や検査の信号は多いが、どれが不良や再検査に効いているか分かりにくい
- 最終検査で落ちるまで、怪しい個体を早く見つけられない
- 評価やベンチ試験の時間が、variantや構成の組み合わせで読みにくい
- 全部を厚く見るとコストが高く、薄く見ると品質リスクが残る
- データ分析ができても、現場の工程改善、検査優先順位、評価計画へ転記できないと価値にならない

## 解決策

初期の解決策は、外販SaaSではなく、公開Kaggle課題を使った小さな検証でよい。

作るものは以下。

1. Kaggle課題をEPSサプライヤ業務に読み替える対応表
2. Bosch型の製造不良予測を、EPS製造・EOL検査に置き換えたワークフロー
3. Mercedes-Benz型のテスト時間予測を、EPS bench/HILS/EOL評価に置き換えたワークフロー
4. 予測精度だけでなく、誰が何の判断に使うかを示す1枚
5. 「これはEPS市場故障予測ではない」という禁止主張リスト

## 買い手 / 利用者

初期に見るべき利用者は、OEMでもドライバーでもない。
EPSサプライヤ内の以下である。

- 製造品質
- 工程設計
- 最終検査 / EOL検査
- 評価計画
- HILS / bench評価
- software / calibration release gate担当

買い手が外部にいるかはまだ不明である。
ただし、少なくともこの方向は、サプライヤが持てないOEM保証DBやfleet dataに依存しない。
そのため、過去の故障予測案よりも、EPSサプライヤ視点では現実的である。

## 初期提供物

最初に作るなら、商品ではなく検証用の小さな成果物にする。

| 成果物 | 目的 |
|---|---|
| Kaggle hidden demand map | コンペ課題を、EPSサプライヤの業務痛みに読み替える |
| Bosch型 proxy notebook / HTML | 製造・工程検査データから不良候補を順位付けできるかを見る |
| Mercedes型 proxy notebook / HTML | 構成情報から評価時間や検査負荷を見積もれるかを見る |
| EPS supplier workflow one-pager | 予測結果を工程改善、再検査、評価計画のどこに貼るかを示す |
| Kill checklist | generic ML demoで終わったら止める |

## 検証方法

内部資料を使わない現行方針では、実EPSデータでの価値検証はしない。
代わりに、Kaggleの公開課題で次を確認する。

1. 目的変数が業務判断に直結しているか
2. 入力データがEPSサプライヤでも持てそうな種類か
3. 出力が工程、検査、評価計画のどこかに転記できるか
4. EPS市場故障予測に飛躍していないか
5. 既存のBI、SPC、品質管理、工程改善の言い換えで終わっていないか

この5つを満たすなら、次にBosch型とMercedes型をそれぞれ小さくデモする価値がある。

## Kill条件

次のどれかに当たるなら止める。

- 予測対象が、EPSサプライヤの業務判断に転記できない
- ただのKaggle精度競争になり、製造・検査・評価の判断が変わらない
- EPSサプライヤが持てるデータではなく、OEM保証DBやfleet dataを前提に戻ってしまう
- 既存の工程管理、SPC、BI、品質管理システムで十分説明できる
- 製造品質や評価計画の利用者が具体化しない
- 「EPS故障予測ができる」と言い始める

## EPSサプライヤとしての言い方

言ってよいこと:

> Kaggleの自動車系コンペを見ると、公開データそのものより、企業が外部に出した課題設定から需要を読める。特に製造不良予測とテスト時間短縮は、EPSサプライヤが持つ製造、EOL検査、bench/HILS評価データに近い。ここは、OEM保証DBやfleet dataに頼らずに検証できる可能性がある。

まだ言ってはいけないこと:

> KaggleでEPS故障予測を実証できる。

> 公開OBD/CANデータでEPS内部診断の不足が分かる。

> BoschやMercedes-Benzのコンペがあるので、EPSサプライヤ向け商品が売れる。

## 現時点判断

Kaggleは、内部資料なし探索の中では久しぶりに見直す価値がある。
ただし、方向は変える。

過去の主題だった「市場に出たEPSの故障予測」ではなく、次の探索に切り替える。

> EPSサプライヤが自分で持てる製造・検査・評価データを使い、品質と評価効率の判断を支援できるか。

この方向なら、最初に見るべきKaggleは、Bosch Production Line PerformanceとMercedes-Benz Greener Manufacturingである。

## CoVe

| 検証質問 | 回答 | Confidence | 反映 |
|---|---|---|---|
| KaggleにEPS故障予測に直接使えるデータがあるか | 見つかっていない。公開OBD/CAN/steering angleは、EPS内部故障ラベルや診断情報を持たない | High | 故障予測には使わない |
| Kaggleコンペは需要シグナルとして読めるか | 読める。少なくとも企業が目的変数と課題を設定しているため、単なる公開データより業務痛みを読みやすい | Medium | 隠れた需要として扱う |
| EPSサプライヤ視点に合う候補はあるか | Bosch型の製造不良予測、Mercedes型のテスト時間予測は、サプライヤ所有データに寄せやすい | Medium | 次探索候補にする |
| 既存業務との重複リスクはあるか | ある。SPC、BI、品質管理、工程改善、評価計画と被る可能性が高い | High | Kill条件に入れる |
| 外販商品として今Proceedできるか | できない。まずは公開コンペで業務転記先を示せるかを見る段階 | High | 商品名化しない |

## 参照

- Kaggle: Bosch Production Line Performance, https://www.kaggle.com/competitions/bosch-production-line-performance
- Kaggle: Mercedes-Benz Greener Manufacturing, https://www.kaggle.com/c/mercedes-benz-greener-manufacturing
- Kaggle: OBD-II & CAN-Based Driving Behavior Dataset, https://www.kaggle.com/datasets/isaygerardozamora/obd-ii-and-can-based-driving-behavior-dataset
- Kaggle: Car-Hacking Dataset, https://www.kaggle.com/datasets/pranavjha24/car-hacking-dataset
- Kaggle Blog: Bosch competition winner/interview material, https://medium.com/kaggle-blog/bosch-production-line-performance-competition-winners-interview-3rd-place-team-data-property-8b24c3747321
- Machine Learning Orientation: Bosch Production Line Performance summary, https://machinelearningintro.uwesterr.de/bosch-production-line-performance.html
