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
| Bosch Production Line Performance | 製造ラインの測定・試験データから、後で不良になる個体を早く見つけたい | EPS製造、工程検査、EOL検査で、再検査・保留・工程確認候補を先に出す | 最有力 |
| Mercedes-Benz Greener Manufacturing | 多品種構成でテストベンチ時間を予測し、評価時間を短くしたい | EPS variant、software、calibration、機能構成から、bench/HILS/EOL評価時間や試験優先順位を見積もる | 有力 |
| OBD-II / CAN driving behavior | 運転行動や利用状態を分類したい | 低速高操舵、急操舵、速度帯などの使用条件proxy | 入力止まり |
| CAN intrusion | 通信異常や攻撃を検出したい | 診断通信やcyber demoの参考 | 既存cyber領域と被るため主商品にしない |
| Steering angle / behavioral cloning | 操舵要求を推定したい | steering demand proxy | EPS品質・診断とは遠く、優先度低 |

## RDI006との関係

この観点は、RDI006をProceedにする材料ではない。

RDI006で必要だったのは、EPS/SbW固有DID、freeze frame、assist / limit state、thermal indicators、software / calibration ID、service note転記先、service outcome feedbackである。
Kaggleの公開課題から、これらを直接埋めることはできない。

したがって、KaggleはRDI006の穴埋めには使わない。
使うなら、別テーマとして、製造品質、EOL検査、評価時間短縮の意図を読むために使う。

## Market Demand First

| Field | 内容 |
|---|---|
| Market demand | 製造、検査、評価では、不良候補や時間がかかる構成を早く見つけ、再検査、保留、工程確認、試験計画へつなげたい需要がある。 |
| Unresolved pain | 公開情報だけではEPS実データは見えないが、企業がKaggleに出した目的変数から、どの業務判断を改善したいかは読める。 |
| Hypothesis | Kaggleの課題設定を読むことで、EPSサプライヤが持てる製造・検査・評価データに近い業務痛みを抽出できる。 |
| Solution | Kaggle problem-setting lensで、課題タイトル、目的変数、入力データ、評価指標、業務転記先、禁止主張を整理する。 |
| Buyer / user | EPSサプライヤ内の製造品質、工程設計、EOL検査、評価計画、HILS/bench、software/calibration release gate。 |
| Initial artifact | Kaggle課題をEPSサプライヤ業務へ読み替える対応表と、Bosch型 / Mercedes型の小さなproxy workflow。 |
| Validation method | 目的変数が業務判断に直結するか、入力データがサプライヤ所有データに近いか、出力が帳票や判断へ転記できるかを見る。 |
| Kill criteria | EPS市場故障予測に飛躍する、RDI006の内部data fieldを埋めた扱いにする、既存SPC/BI/品質管理の言い換えで終わる、利用部署が具体化しない。 |

## EPSサプライヤとしての言い方

言ってよいこと:

> Kaggleの自動車系コンペは、公開データそのものより、企業が外に出した問題設定から需要を読める。Bosch型は製造・EOL検査、Mercedes型は評価時間短縮に読み替えやすい。

まだ言ってはいけないこと:

> KaggleでEPS故障予測を実証できる。

> KaggleでRDI006に必要なEPS/SbW内部data fieldを埋められる。

> BoschやMercedes-Benzのコンペがあるので、EPSサプライヤ向け商品が売れる。

次に見る最小項目:

> Bosch型とMercedes型について、目的変数、入力データ、現場判断、EPSサプライヤ部署、Kill条件を1行ずつ整理し、製造品質 / EOL検査 / 評価時間短縮のどれに寄せるか決める。

## Sources

- Kaggle: Bosch Production Line Performance, https://www.kaggle.com/competitions/bosch-production-line-performance
- Kaggle: Mercedes-Benz Greener Manufacturing, https://www.kaggle.com/c/mercedes-benz-greener-manufacturing
- Kaggle: OBD-II & CAN-Based Driving Behavior Dataset, https://www.kaggle.com/datasets/isaygerardozamora/obd-ii-and-can-based-driving-behavior-dataset
- Kaggle: Car-Hacking Dataset, https://www.kaggle.com/datasets/pranavjha24/car-hacking-dataset
