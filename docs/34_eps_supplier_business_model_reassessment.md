# EPS Supplier Business Model Reassessment

## 結論

上位ルールで既存データを見直すと、更新はある。

現状の `EPS Warranty / RCA Evidence Readiness Pack` は方向としては近い。
ただし、まだ `既存DTC / freeze frame / extended dataで足りるか` に寄りすぎていて、見え方が `ログ追加の前段` になっている。

EPSサプライヤの立場に帰着させるなら、より良い主商品名はこれ。

> **EPS RCA / 8D Evidence Case Pack**

これはログ追加商品ではない。
売るものは、`RCA / 8D / 顧客品質報告にそのまま転記できるケース成果物` である。

## 市場需要

既存データから見る需要は、以下に集中している。

| Demand | Existing repo signal | Buyer |
|---|---|---|
| NTF / 返却品で原因が再現しない | CP005, CP006, ECM001, ECM002 | warranty / return-part analysis |
| 8D / SCAR / CAPAで証拠添付が必要 | CP009, CP010, CP011, CP014, ECM006 | supplier quality / customer quality |
| 保証claim、DTC、返却品、技術者記述が分断 | CP001-CP004, ECM004, ECM005 | warranty / quality analytics |
| 診断仕様変更の根拠が弱い | VAL003, GAP002, GAP003, GAP008 | diagnostic engineering |

この需要は、`ログを増やしたい` ではない。

より正確には、

> 顧客/OEMに対して、確認済み事実、未確認事項、推定してはいけないこと、次に確認すべきことを、早く安全に説明したい。

## 仮説

EPSサプライヤは、初期には機能・SaaS・ログ追加ではなく、ケース処理型の有償パックを売るのが自然。

> 返却品/NTF/市場claim/8D候補の1ケースを受け取り、既存DTC/freeze frame/extended data、返却品reader、現品解析結果、公開scenarioを使って、RCA/8D/顧客品質報告に貼れるevidence attachmentを作る。

この仮説なら、EPSサプライヤが持つ手札に収まる。

- サプライヤEPSのDTC / freeze frame / extended data仕様
- engineering DID / reader / ODX
- 返却品解析結果
- 現品試験結果
- サプライヤ側で言える事実と、OEMデータが必要な境界

## 解決策

### Primary Offer

> **EPS RCA / 8D Evidence Case Pack**

想定期間:

- 1ケース: 3-5営業日
- 20-50件分類: 2-4週間

成果物:

| Artifact | 用途 |
|---|---|
| Case narrative | D2 problem descriptionの下書き |
| Confirmed / unconfirmed / do-not-infer table | 顧客品質報告で断定しすぎないため |
| Existing diagnostic evidence table | DTC / freeze frame / extended data / readerで何が説明できるか |
| RCA next-check list | 次に読むDID、追加試験、OEMへ要求するデータ |
| Evidence boundary note | サプライヤで言えること、OEMデータが必要なことを分ける |
| Optional gap heatmap | 20-50件後に繰り返し不足するfactだけを集計 |

### Not Core

以下は初期商品にしない。

- ECU追加ログ
- 波形保存
- 故障予測
- 劣化兆候通知
- 保証費削減保証
- 8D自動回答
- root cause自動断定
- OEM fleet analytics
- remote diagnostics / OTA連携

## なぜログ追加ではないか

ログ追加は、最後に残る可能性のある派生成果でしかない。

順番はこうする。

1. 実ケースでRCA/8Dに必要なfactを整理する
2. 既存DTC / freeze frame / extended data / readerで足りるか見る
3. 足りるなら追加ログは不要
4. 足りない場合だけ、繰り返し不足するfactをheatmap化する
5. NVM制約と読出し経路がある場合だけ、診断仕様改善候補にする

つまり、最初に売るのは `ログ` ではなく `ケース成果物`。

## EPSサプライヤとしての結論

### 売る

> EPS RCA / 8D Evidence Case Pack

顧客品質、返却品解析、supplier quality、diagnostic engineering向けに、1ケースまたは20-50件のケース分類を有償で実施する。

### やる

- 既存DTC / freeze frame / extended dataのcoverage整理
- 返却品reader / DID / ODXで読める事実の整理
- confirmed / unconfirmed / do-not-infer表の作成
- RCA/8D D2-D4に貼れるfact attachment作成
- 20-50件後のmissing fact heatmap作成

### やらない

- 故障予測を売る
- 劣化検知を売る
- 既存診断不足を公開データだけで断定する
- OEM保証DBやfleet platformを初期前提にする
- 8Dやroot causeを自動回答する

### 初期対象外

- OEM warranty analytics platform
- connected diagnostics / OTA integration
- service shop向け診断
- エンドユーザ通知

## 最初のDemo

`SCN001 low-speed high effort` で、追加データ分析ではなく1ページcase packを作る。

入れるもの:

- market demand statement
- case narrative
- confirmed / unconfirmed / do-not-infer
- existing diagnostic evidence table
- next-check list
- evidence boundary note
- 8D D2-D4 attachment draft

成功条件:

> warranty / customer quality / diagnostic engineeringの誰かが、既存の顧客品質報告または8Dテンプレートに貼れると言うこと。

## Kill条件

以下なら、この方向は弱い。

- 既存品質報告や8Dに転記できない
- 1ケース処理しても、次の解析行動が変わらない
- confirmed / unconfirmed / do-not-infer表が既存報告と差分を生まない
- 20-50件分類しても、再利用できるmissing fact patternが出ない
- 顧客がケース処理ではなく実装機能だけを求める

## CoVe

| Question | Answer | Confidence | Impact |
|---|---|---:|---|
| これは市場需要から始まっているか | Yes. NTF、返却品、8D、SCAR、顧客品質説明の証拠不足から始まる。 | High | Keep |
| EPSサプライヤの立場に戻っているか | Yes. サプライヤDTC、reader、返却品解析、顧客品質報告に限定する。 | High | Keep |
| ログ追加の話になっていないか | まだなりやすい。主商品をcase packに変更し、ログ追加は派生に下げる。 | High | Revise |
| OEM領域に依存しすぎていないか | 保証DB/fleet analyticsはoptional extensionへ下げた。 | High | Keep |
| 買い手の業務成果物に転記できるか | 仮説。次Demoで8D/品質報告への転記性を確認する。 | Medium | Next validation |

## 更新判断

更新あり。

旧:

> EPS Warranty / RCA Evidence Readiness Pack

新:

> EPS RCA / 8D Evidence Case Pack

`Evidence Readiness` はまだ抽象的で、ログ追加の前段に見える。
`Case Pack` まで落とすことで、売り物がログではなく、品質・保証・RCAの業務成果物になる。
