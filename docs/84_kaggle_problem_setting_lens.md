# Kaggleを問題設定から読む観点

## 結論

Kaggleは、公開データとしてだけ見ると弱い。
EPS固有のDTC、freeze frame、assist state、thermal state、service outcomeは見えないため、EPS市場故障予測やRDI006の穴埋めには使いにくい。

ただし、Kaggleには別の使い方がある。
企業がKaggleに出した課題は、単なるデータ公開ではなく、「外部に解いてほしい業務課題」の形になっている。
つまり、目的変数、入力データ、評価指標、コンペ説明から、その企業が何を早く知りたいのか、どの業務時間を減らしたいのか、どの判断を改善したいのかを読める。

この観点では、Kaggleは **隠れた需要を読むための公開シグナル** として使う。

## 何を読むか

Kaggleを見るときは、まずデータ列やモデル精度ではなく、次を読む。

| 見るもの | 読み取ること |
|---|---|
| 課題タイトル | 企業がどの業務問題を外に出したか |
| 目的変数 | 何を早く知りたいか、何を減らしたいか |
| 入力データ | 企業がどの種類のデータを持っているか |
| 評価指標 | 現場で何を重視しているか |
| コンペ説明 | どの業務成果へ転記したいか |
| 禁止されている使い方 | そのデータで言ってはいけないこと |

この読み方を、以後 `problem-setting lens` と呼ぶ。
意味は、Kaggleを「データセット」ではなく「企業が外に出した問題設定」として読む、ということである。

## EPSサプライヤへの読み替え

| Kaggle課題 | 読める企業側の意図 | EPSサプライヤでの読み替え | 判断 |
|---|---|---|---|
| Bosch Production Line Performance | 製造ラインの測定・試験データから、後で不良になる個体を早く見つけたい | EPS製造、工程検査、EOL検査で、再検査・保留・工程確認候補を先に出す | 製造・EOL検査の別枝 |
| Mercedes-Benz Greener Manufacturing | 多品種構成でテストベンチ時間を予測し、評価時間を短くしたい | EPS variant、software、calibration、機能構成から、bench/HILS/EOL評価時間や試験優先順位を見積もる | 評価時間短縮の別枝 |
| OBD-II / CAN driving behavior | 運転行動や利用状態を分類したい | 低速高操舵、急操舵、速度帯、stop-startなどの使用条件proxy | 残す |
| CAN intrusion | 通信異常や攻撃を検出したい | 診断通信、異常通信、security access、禁止主張の境界確認 | 境界付きで残す |
| Steering angle / behavioral cloning | 操舵要求を推定したい | steering demand proxy、操舵要求family | 残す |
| PVS passive vehicular sensors | 路面や走行環境を分類したい | 路面、振動、速度、環境条件proxy | 残す |

## RDI006との関係

この観点は、RDI006をProceedにする材料ではない。

RDI006で必要だったのは、EPS/SbW固有DID、freeze frame、assist / limit state、thermal indicators、software / calibration ID、service note転記先、service outcome feedbackである。
Kaggleの公開課題から、これらを直接埋めることはできない。

したがって、KaggleはRDI006の穴埋めには使わない。
使うなら、別テーマとして、製造品質、EOL検査、評価時間短縮の意図を読むために使う。

## Market Demand First

| Field | 内容 |
|---|---|
| Market demand | EPSサプライヤが、公開情報だけで実使用条件、操舵要求、路面・環境、通信異常を読み、評価scenario、診断コンテンツ、顧客説明、禁止主張へ変換したい需要がある。 |
| Unresolved pain | 公開情報だけではEPS内部状態は見えないが、OBD/CAN、操舵角、受動車両センサ、CAN異常から、実使用側の問いを作れる可能性がある。 |
| Hypothesis | Kaggleの課題設定を読むことで、EPS内部故障を断定せずに、EPSが晒される使用条件familyと、評価・診断・説明に入れるべき問いを抽出できる。 |
| Solution | KGL003、KGL005、KGL006から実使用条件familyを作り、KGL004で通信異常の境界を確認する。KGL001/002は製造・評価効率の別枝として保存する。 |
| Buyer / user | EPSサプライヤ内の評価企画、HILS/bench、診断コンテンツ担当、顧客技術説明担当、software/calibration release gate。 |
| Initial artifact | Kaggle課題をEPSサプライヤ業務へ読み替える対応表と、KGL003/005/006を使った実使用条件familyの小さなproxy workflow。 |
| Validation method | 目的変数が評価scenario、診断質問、顧客説明質問、禁止主張に転記できるかを見る。 |
| Kill criteria | EPS市場故障予測に飛躍する、内部data fieldを埋めた扱いにする、公開データ紹介で終わる、既存評価項目や既存診断仕様の一般論で終わる、利用部署が具体化しない。 |

## EPSサプライヤとしての言い方

言ってよいこと:

> Kaggleの自動車系データは、公開データそのものより、問題設定から需要を読める。工程検査だけでなく、OBD/CAN、操舵角、受動車両センサ、CAN異常から、EPSが晒される実使用条件や診断・説明上の問いを作れる可能性がある。

まだ言ってはいけないこと:

> KaggleでEPS故障予測を実証できる。

> KaggleでRDI006に必要なEPS/SbW内部data fieldを埋められる。

> BoschやMercedes-Benzのコンペがあるので、EPSサプライヤ向け商品が売れる。

次に見る最小項目:

> KGL003、KGL005、KGL006について、目的変数、入力データ、実使用条件family、EPSサプライヤ部署、Kill条件を1行ずつ整理し、評価scenario / 診断質問 / 顧客説明質問のどれに転記できるか決める。KGL004は通信異常と禁止主張の境界確認として扱う。

この最小項目をKGL001〜KGL006へ展開した結果は、[docs/85_kaggle_problem_setting_id_deep_dive.md](85_kaggle_problem_setting_id_deep_dive.md) と [data/kaggle_problem_setting_id_deep_dive.tsv](../data/kaggle_problem_setting_id_deep_dive.tsv) に置く。
結論は、工程検査が目的ではないため、KGL003、KGL005、KGL006を実使用条件proxyとして残し、KGL004を境界付きで残す。KGL001とKGL002は製造・評価効率の別枝として保存する、である。

この観点でKaggleを再調査し、KGL007〜KGL012を追加した結果は、[docs/86_kaggle_usage_proxy_refresh.md](86_kaggle_usage_proxy_refresh.md) と [data/kaggle_usage_proxy_refresh.tsv](../data/kaggle_usage_proxy_refresh.tsv) に置く。
追加後の主線は、KGL003/005/006/007/008で実使用条件familyを作り、KGL011とKGL004で通信異常と禁止主張の境界を確認する、である。

KGL001〜KGL012を同じ判定軸で深掘りした結果は、[docs/87_kaggle_each_id_deep_dive.md](87_kaggle_each_id_deep_dive.md) と [data/kaggle_each_id_deep_dive.tsv](../data/kaggle_each_id_deep_dive.tsv) に置く。

## Sources

- Kaggle: Bosch Production Line Performance, https://www.kaggle.com/competitions/bosch-production-line-performance
- Kaggle: Mercedes-Benz Greener Manufacturing, https://www.kaggle.com/c/mercedes-benz-greener-manufacturing
- Kaggle: OBD-II & CAN-Based Driving Behavior Dataset, https://www.kaggle.com/datasets/isaygerardozamora/obd-ii-and-can-based-driving-behavior-dataset
- Kaggle: Car-Hacking Dataset, https://www.kaggle.com/datasets/pranavjha24/car-hacking-dataset
