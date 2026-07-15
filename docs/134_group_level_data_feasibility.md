# Group-Level Steering Risk Curve: Data Feasibility

## 結論

フェーズBの判定条件は「**車齢×操舵系不具合率の曲線が1本でも誠実に引けるか**」だった。

判定: **引ける。フェーズC(Demo構築 v2)へ進む。**

| データ源 | 実在・粒度の確認結果 | 曲線への使い方 | 判定 |
|---|---|---|---|
| NHTSA苦情DB | **API実働確認済み**。2010 Ford Fusion単独で苦情5,122件。fieldに `components`(STEERINGカテゴリあり)、`dateOfIncident`、`dateComplaintFiled`、`products`(年式・make・model) | 車種×年式cohort別の「車齢に対する操舵系苦情の発生曲線」。分母がないため、**同一車種の年式間比較**と**全苦情に占める操舵系比率**で正規化 | **主データ(フェーズCで使用)** |
| NHTSAリコール/ODI | 第1ラウンドで精読済み(15V-340、17V-414等)。是正時期・対象年式が既知 | 曲線の**答え合わせ**に使う。既知の不具合cohort(Fusion 2010-2012)が曲線上で本当に浮くかの検証 | 検証用(フェーズCで使用) |
| 英国DVSA MOT車検データ | **実在確認済み**。テスト結果+failure item(RfR)の年次CSV、2005年以降、make/model・走行距離・初度登録あり。Open Government Licence v3.0 | 車検合格/不合格が全数記録されるため**分母がある**唯一の源。「車齢×操舵系不合格率」の真の率曲線 | 拡張(フェーズC第2段。ファイルが大きく、操舵カテゴリの項目分類はlookup tableで実装時確認) |
| 既存Kaggle/proxy資産 | リポジトリ内に既存 | 使用条件側の補完。曲線本体には使わない | 補助 |

詳細表は [data/group_level_data_feasibility.tsv](../data/group_level_data_feasibility.tsv) に置く。

## 何を判断しているか

需要マップ([docs/133](133_failure_prediction_demand_map.md))の空席(2)「群レベルの故障傾向」が、公開データで誠実に作れるかである。
「誠実に」の意味は、(a)分母や偏りの問題を隠さない、(b)個車の未来の予測に見せない、(c)既知の事実(リコール)と突き合わせて検証できる、の3点である。

## Rule Check

今回の判断では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`: 曲線の買い手は docs/133 で特定済み(EPSサプライヤ内部の品質改善・製品企画)
2. `Natural Language First`: 曲線の意味は「市場で観測された過去の記述」であり、予測モデルの精度自慢にしない
3. `EPS Supplier Lens`: 成果物の転記先は次期設計の重点・評価計画・RFQ回答の裏付け
4. `Kaggle / Public Proxy Predictive Value Rule`: 個車RUL・交換時期・保証費削減を主張しない。公開proxyの限界(苦情の偏り、車検制度差)を明記する
5. 特定OEM/車種の設計優劣の断定に使わない(検証用cohortは「既知のリコール事例」としてのみ扱う)

## フェーズC Demo設計(この判定に基づく)

### Demo v2: 操舵系苦情のcohort曲線(NHTSA)

1. **対象**: Ford Fusion MY2010〜2014(EPASリコール15V-340の対象2010-2012と、対象外の2013-2014を同一車種内で比較)。可能なら GM Silverado MY2014(17V-414)も
2. **曲線**: 各年式cohortについて、車齢(発生日−年式)に対する操舵系苦情の累積/率。正規化は「全苦情に占める操舵系比率」を併記
3. **答え合わせ**: リコール対象cohortの曲線が非対象cohortより実際に浮くか。浮けば「公開データで群レベルの操舵系リスク傾向は読める」の実証になる
4. **偏りの可視化を demo の一部にする**: `dateComplaintFiled` と `dateOfIncident` の乖離で、リコール公表(2015年7月)後の届出スパイク(報道・通知バイアス)を明示的に見せる。隠すのではなく「苦情データはこう歪む」を成果物に含める
5. 実装: `scripts/` にAPI取得+集計+HTML出力(取得結果はキャッシュしてre-run可能に)

### Demo v2拡張(任意): DVSA MOT率曲線

分母付きの真の率(車齢×操舵系不合格率、make別)。年次CSVのダウンロードサイズが大きいため、第2段として分離。

## 限界(正直に)

1. **苦情データに分母はない**。稼働台数不明のため絶対率は出せない。同一車種内のcohort比較と比率化で相対傾向のみを言う
2. **報告バイアス**: リコール公表・報道で苦情は急増する。これは欠陥発生の波形ではなく社会的な波形。demoで明示する
3. **米国市場のみ**(NHTSA)。MOTは英国のみ。市場をまたぐ一般化はしない
4. **操舵カテゴリの粒度**: NHTSAのSTEERINGはEPS以外(機械系)も含む。MOTの操舵項目も同様。EPS固有の切り出しは苦情本文のキーワードでの近似になる(限界として明記)
5. 群曲線は過去の記述である。個車の故障予測として提示しない(禁止主張)

## 次の作業

1. フェーズC: Demo v2(NHTSA cohort曲線)を実装する。チャート描画を含むため、実装時に可視化の設計規約を確認してから着手する
2. 答え合わせ(リコールcohortが浮くか)の結果を docs/135 に判定として書く
3. 浮かなかった場合も隠さず記録する(「公開苦情データでは群傾向は読めない」も需要調査の成果)

## Sources

- [NHTSA Datasets and APIs](https://www.nhtsa.gov/nhtsa-datasets-and-apis)
- [NHTSA complaints API(実働確認: 2010 Fusion、5,122件、STEERINGカテゴリ)](https://api.nhtsa.gov/complaints/complaintsByVehicle?make=ford&model=fusion&modelYear=2010)
- [ODI Complaints Flat File(data.transportation.gov)](https://data.transportation.gov/Automobiles/NHTSA-s-Office-of-Defects-Investigation-ODI-Compla/jhit-z9cc)
- [DVSA MOT Anonymised open data](https://open.data.dvsa.gov.uk/mot-anonymised/index.html)(Open Government Licence v3.0)
- [Anonymised MOT tests and results(data.gov.uk)](https://www.data.gov.uk/dataset/c63fca52-ae4c-4b75-bab5-8b4735e1a4c9/anonymised-mot-tests-and-results)
