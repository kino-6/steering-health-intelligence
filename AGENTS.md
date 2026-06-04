# Repository Operating Rule

このRepoの事業仮説、調査、デモ、ドキュメント更新では、以下を最上位ルールにする。

## Market Demand First

必ず次の順で提示する。

1. 市場需要
2. 未解決の痛み
3. 仮説
4. 解決策
5. 買い手 / 利用者
6. 初期提供物
7. 検証方法
8. Kill条件

悪い提示:

> EPSにこういう公開事例がある。

良い提示:

> 市場ではNTF、返却品解析、保証claim、SCAR/8D、顧客品質説明で、サプライヤ側が使えるproduct-side evidence不足が痛みになっている。EPSサプライヤは、scenario別に必要factsを定義し、既存DTC/freeze frame/extended dataで説明できるかを確認するEvidence Readiness Packを提供できる。

## EPS Supplier Lens

このRepoの結論は、必ずEPSサプライヤの立場に帰着させる。

市場、OEM、エンドユーザ、サービス、connected platform、規制、Kaggle/公開データをメタ視点で見るのはよい。
ただし、最終判断は以下で締める。

- EPSサプライヤとして何を売るか
- EPSサプライヤとして何を実施できるか
- EPSサプライヤとして何を言ってはいけないか
- OEM領域、サービス領域、fleet platform領域として初期対象外に置くものは何か
- 次にEPSサプライヤ内のどの部署に見せるか

悪い結論:

> OEMや市場にはこういう需要がある。

良い結論:

> 市場にはこういう需要がある。そのうちEPSサプライヤが初期に取れる手札は、既存DTC/freeze frame/extended dataと返却品readerを使ったRCA Evidence Readiness Packである。OEM保証DB連携やfleet analyticsはoptional extensionに置く。

## Current Main Hypothesis

現在の主仮説は以下。

> EPS Warranty / RCA Evidence Readiness Pack

市場需要:

- NTF / 返却品解析で原因が再現しない
- 保証claim、修理記述、DTC、返却品解析が分断される
- SCAR / 8D / CAPAで、確認済み事実と未確認事項を分けた証拠が必要
- OEM保証DBやfleet dataに完全依存すると、EPSサプライヤ側の説明が後手になる

解決:

- 公開市場caseをscenario familyへ分類する
- scenario別に、RCA / 8D / 顧客品質説明で必要なproduct-side factsを定義する
- 既存DTC / freeze frame / extended dataで足りるかを確認する
- 足りない場合でも追加ログを断定せず、確認すべき項目、読める経路、未確認事項を整理する

## Historical Notes

過去の以下の方向はhistoricalとして扱う。最新結論としてそのまま採用しない。

- EPS故障予測
- 劣化兆候通知
- Health-ready EPS Feature Bundle
- ECU追加ログそのもの
- OTA / remote diagnosticsを主商品にする案
- Market Pain Scenario Library単体
- RFQ / Design Review Pack単体

これらは、`EPS Warranty / RCA Evidence Readiness Pack` の材料やoptional extensionとしてのみ使う。

## Required Output Shape

新しい提案や調査結果は、最低限この形にする。

| Field | Required content |
|---|---|
| Market demand | 誰が、どの業務で、何に困っているか |
| Evidence signal | 需要を示す公開情報、Repo内データ、または明示した推論 |
| Hypothesis | その需要に対して何が売れると考えるか |
| Solution | 成果物、workflow、schema、template、demo |
| Buyer / user | 初期に使う部署と役割 |
| Why supplier can play | OEM領域ではなく、EPSサプライヤ側で持てる手札 |
| EPS supplier conclusion | EPSサプライヤとして売る/やる/やらない判断 |
| Demo | 20-50件の調査、1ケースsample、TSV/HTMLなどで何を見せるか |
| What not to claim | 故障予測、保証費削減、root cause断定など禁止主張 |
| Kill criteria | 何が確認できなければ止めるか |

## CoVe Rule

結論を出す前に、以下を必ず確認する。

- これは市場需要から始まっているか
- 単に `こういう事例がある` と言っていないか
- 買い手の業務成果物に転記できるか
- 結論がEPSサプライヤの立場に戻っているか
- OEM保証DB、fleet data、サービスツールに過度依存していないか
- 既存DTC / freeze frame / extended dataとの差分を断定しすぎていないか
- Kill条件が具体的か

## Commit Guidance

Repo更新時は、READMEの現在地と推奨読書順が古い仮説を最新結論のように見せていないか確認する。
