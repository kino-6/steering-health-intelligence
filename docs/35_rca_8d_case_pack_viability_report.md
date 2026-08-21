# RCA / 8D Evidence Case Pack Viability Report

## 結論

`RCA / 8D Evidence Case Pack` は、直感どおり **単独の外販プロダクトとしては筋が弱い**。

ただし、完全に捨てるほどではない。
成立する可能性があるのは、次のようにかなり狭く切った場合だけ。

> EPSサプライヤ内の warranty / customer quality / return-part analysis / diagnostic engineering が、実際に困っている返却品、NTF、市場claim、SCAR/8D案件について、EPS製品側で言える確認済み事実、未確認事項、推定禁止事項、次に読むDID/試験/OEM要求データを整理する短期有償assessment。

つまり、売り物は `8Dを作るツール` でも `ログ追加` でも `故障予測` でもない。
売り物にできる可能性があるのは、炎上中または滞留中の品質案件に対して、EPSサプライヤが責任を持って出せる **case-specific evidence attachment** である。

成立性評価は以下。

| 判定 | 内容 |
|---|---|
| 市場需要 | ある。NTF、返却品解析、保証claim、SCAR/8D、顧客品質説明で証拠が足りない痛みは公開情報でも見える。 |
| EPSサプライヤ適合 | 条件付きである。サプライヤDTC、freeze frame、extended data、reader、現品解析結果を使える範囲なら成立し得る。 |
| 差別化 | 弱い。汎用QMS、8D、SCAR、warranty analytics、コンサルが既にある。EPS固有factに絞らないと埋もれる。 |
| 収益モデル | 初期はSaaSではない。1ケースまたは20-50件の固定費assessment / NREが妥当。 |
| Kill可能性 | 高い。既存8D/品質報告に転記できない、または現行DTCで十分ならKill。 |

## 市場需要

市場側の需要は、`EPSをもっと賢くしたい` ではなく、もっと地味で切実なものに見える。

> 返却品や市場claimが来たとき、部品単体では再現しない。
> それでも顧客、OEM、監査、SCAR/8Dに対して、何が確認済みで、何が未確認で、何を原因と言ってはいけないかを早く説明しなければならない。

公開調査で見える需要シグナルは以下。

| 需要シグナル | 何を示すか | この仮説への意味 |
|---|---|---|
| AIAG warranty / CQI-14文脈 | NTF、returned parts、DTC、supplier、8Dなどが保証品質の用語として扱われる | NTF/返却品/診断データは市場品質の正式な業務文脈にある |
| AIAGのNTFデータ分析記事 | 修理・保守データの分析でNTFに対処する文脈がある | NTFは単なる社内愚痴ではなく、データで潰すべき市場課題 |
| SCAR/8D要求 | supplier corrective actionではproblem statement、scope、evidence、root cause、effectivenessが求められる | 事実整理と証拠添付はsupplier側の業務成果物になる |
| Warranty analytics vendor | field claims、returned parts、dealer narratives、vehicle diagnosticsを扱う | 保証・返却品・診断データをつなぐ支払市場は存在する |
| 8D/CAPA/QMS vendor | 8D、RCA、evidence evaluation、corrective actionを扱う | 一方で、汎用解決策は既に多い |

参照:

- AIAG CQI-14 warranty key terms: https://www.aiag.org/docs/default-source/quality/aiag-cqi-14-warranty-key-terms.pdf
- AIAG, Addressing No Trouble Found via Data Analysis: https://blog.aiag.org/addressing-no-trouble-found-via-data-analysis
- Symestic, SCAR: How Supplier Corrective Action Actually Works: https://www.symestic.com/en-us/what-is/scar
- AWM Warranty Data Analysis: https://www.awm-warranty-management.com/services/warranty-data-analysis/
- Supplios Supplier Quality: https://www.supplios.com/features/supplier-quality
- CAPA Engine: https://www.capaengine.com/

## 未解決の痛み

本Repoの既存調査を上位ルールで読み直すと、痛みは3つに分かれる。

| Pain | 既存資料 | 解釈 |
|---|---|---|
| NTF / 返却品で原因が見えない | `CP005`, `CP006`, `ECM001`, `ECM002` | 返却品単体で再現しないと、EPSサプライヤ側の説明が弱くなる |
| 8D / SCAR / CAPAで証拠が必要 | `CP009`, `CP010`, `CP011`, `CP014`, `ECM006` | 8Dのフォームではなく、D2-D4に入れる確認済み事実が不足する |
| 保証claim、DTC、返却品、技術者記述が分断 | `CP001-CP004`, `ECM004`, `ECM005` | OEM全体の保証DBは持てないが、EPS製品側factの翻訳schemaは作れる |

この痛みは実在しそうだが、注意点がある。
公開市場調査だけでは、`EPSサプライヤがこれにいくら払うか` までは見えない。
よって、ビジネスとしては **需要あり、支払意思は未証明** と置くのが正しい。

## 仮説

成立し得る仮説はこれ。

> EPSサプライヤは、顧客品質/返却品/NTF/SCAR/8D案件で、既存診断・reader・現品解析から得られるproduct-side factsを、顧客品質報告や8D D2-D4へ転記できる形に整理する短期assessmentを提供できる。

成立しない仮説はこれ。

| 弱い仮説 | なぜ弱いか |
|---|---|
| 8D自動回答 | 8Dは責任分界、顧客指定様式、実証、是正効果確認が絡む。EPSサプライヤが自動生成してよい領域ではない。 |
| 汎用RCAツール | 既存QMS/8D/CAPAツールと正面衝突する。EPSサプライヤの差分が出ない。 |
| ログ追加サービス | 既存DTC/freeze frame/extended dataで足りる可能性がある。最初から追加ログを売ると既存診断の言い換えになる。 |
| OEM保証analytics | OEM保証DB、修理履歴、fleet/platform権限が必要。EPSサプライヤ初期商品として重い。 |
| 故障予測/劣化兆候通知 | 頻度、責任、説明可能性、データ取得経路が弱い。現時点の主張にしない。 |

## 解決策

### 初期提供物

`EPS RCA / 8D Evidence Case Pack` を、以下の成果物に限定する。

| Artifact | 使い道 | 注意 |
|---|---|---|
| Case narrative | 8D D2 problem description / 顧客品質報告の事実整理 | 原因断定をしない |
| Confirmed / unconfirmed / do-not-infer table | 言えること、言えないことを分ける | ここが一番価値になり得る |
| Existing diagnostic evidence table | DTC / freeze frame / extended data / readerで説明できる範囲 | 既存で足りれば追加提案しない |
| RCA next-check list | 次に読むDID、現品試験、OEMへ要求するデータ | OEMへの丸投げではなく、supplier側fact不足を明確化する |
| Evidence boundary note | EPSサプライヤで言えること、OEMデータが必要なことを分ける | 責任過多を避ける |
| Optional missing fact heatmap | 20-50件分類後に繰り返す不足factだけ集計 | 追加ログや仕様改善はここから先 |

### 提供形態

初期の収益モデルは、プロダクト課金ではなく以下が自然。

| Model | 内容 | 成立条件 |
|---|---|---|
| 1-case assessment | 1件のNTF/返却品/8D候補を3-5営業日でcase pack化 | 困っている具体案件がある |
| 20-50 case classification | 過去案件を2-4週間で分類し、繰り返し不足するfactを抽出 | case backlogがあり、内部資料を見られる |
| Diagnostic evidence design review | 既存DTC/freeze frame/extended dataで足りるかをレビュー | diagnostic engineeringが参加する |
| Optional NRE | 繰り返し不足するfactだけ、診断仕様/reader/試験項目改善へ接続 | missing factが複数案件で再発する |

## 買い手/利用者

初期の買い手は外部OEMではなく、EPSサプライヤ内の困っている部署に置くべき。

| Role | 嬉しいこと | 予算/導入の自然さ |
|---|---|---|
| Customer quality | 顧客向け説明で、断定しすぎずに事実を出せる | 高め。8D/SCAR対応が直接業務 |
| Warranty / return-part analysis | NTFや再現不能案件で、次に何を見るか明確になる | 中。案件数がある場合に成立 |
| Diagnostic engineering | 現行DTC/freeze frame/extended dataで足りるかを実ケースから見られる | 中。仕様改善NREに接続できる |
| Supplier quality liaison | 顧客/OEMとのやりとりで、要求データと境界を説明できる | 中。社内連携が必要 |

エンドユーザ、サービス店、OEM fleet analytics部門は初期対象外。
将来のextensionとしてはあり得るが、今の結論をそこに逃がすと、EPSサプライヤ視点から外れる。

## なぜ筋が悪く見えるか

筋が悪く見える理由は正しい。

1. 8DやRCAは既に業務として存在する
2. QMS/SCAR/CAPA/warranty analyticsツールも既にある
3. EPSのDTC/freeze frame/extended dataも既にある
4. OEM保証DBや市場データはEPSサプライヤ単独で持てない
5. 内部DTC仕様なしでは、公開データ分析やテンプレート整理で止まる

したがって、`RCA / 8D Evidence Case Pack` を広く売ろうとすると弱い。
ただし、以下まで絞ればまだ検証する価値がある。

> 汎用8Dでは扱えないEPS固有factを、顧客品質報告へ貼れる形に翻訳する。

ここでいうEPS固有factは、例えば以下。

- assist command / actual motor current / current tracking
- assist limit / derating / fail-safe state
- EPS internal voltage / reset / brownout context
- EPS thermal state
- torque sensor plausibility / redundancy / residual
- steering angle / vehicle speed / low-speed high-effort context
- related DTC, freeze frame, extended data, engineering DID
- returned-part reader availability and readout boundary

これらが使えないなら、この商品は汎用報告書作成代行に落ちる。
その場合はKillした方がよい。

## 検証方法

次の検証は、追加の市場調査ではなく、**1ケース成果物の転記性検証** がよい。

### 検証1: SCN001 case pack sample

`SCN001 low-speed high effort` で1ページsampleを作る。

必須項目:

- D2 problem statement案
- D4 fact table
- confirmed / unconfirmed / do-not-infer
- existing diagnostic coverage check
- next DID / reader / test list
- OEM data required boundary
- supplier conclusion wording

成功条件:

> EPS supplier customer quality / warranty / diagnostic engineering の誰かが、既存の8Dまたは顧客品質報告に貼れると言う。

### 検証2: 20-50件分類の価値確認

20-50件の過去案件を仮に分類できたとして、嬉しいことは以下に限定される。

| 嬉しいこと | ビジネス意味 |
|---|---|
| 同じmissing factが複数案件で繰り返す | 診断仕様/reader/試験項目改善のNRE根拠になる |
| 現行診断で十分な案件が多い | 追加ログ提案を止められる。無駄な開発を避ける |
| OEMデータが必要な境界が明確になる | OEMに丸投げではなく、要求データを具体化できる |
| D2/D4に転記できる表現が標準化される | customer qualityの作業時間と責任リスクを下げる |

嬉しくない分類はこれ。

- scenarioが増えるだけ
- proxy windowが増えるだけ
- ログ候補が増えるだけ
- `可能性があります` の文章が増えるだけ

## Kill条件

以下なら、このビジネスモデルは止める。

| Kill condition | 理由 |
|---|---|
| 1ページsampleが既存8D/品質報告に転記できない | 業務成果物になっていない |
| EPS固有factが入らない | 汎用8D整理と差別化できない |
| 現行DTC/freeze frame/extended dataで十分 | 追加価値がない |
| 内部DTC仕様、reader、現品解析結果にアクセスできない | EPSサプライヤらしい価値が出ない |
| case backlogがない | case-triggered商品として買う理由がない |
| 顧客が求めているのが実装機能だけ | assessmentでは刺さらない |
| 品質部門が`これは自分たちでやっている`と言う | 既存業務の言い換えになる |

## Chain-of-Verification

| Question | Evidence check | Confidence | 修正 |
|---|---|---:|---|
| 市場需要は本当にあるか | AIAG warranty/NTF文脈、SCAR/8D要求、warranty analytics/8D vendorが存在する。 | High | 需要はあるとする |
| EPS-specificの支払意思まで証明できるか | 公開調査では直接見えない。Repo内でも内部案件確認が必要とされている。 | Low | `支払意思は未証明` に修正 |
| これは既存ツールの言い換えではないか | QMS、CAPA、8D、SCAR、warranty analyticsが既に存在する。 | High | 汎用RCA/8DではなくEPS固有fact attachmentへ限定 |
| EPSサプライヤが主語で成立するか | サプライヤDTC、freeze frame、extended data、reader、現品解析結果を扱える範囲なら主語にできる。 | Medium | OEM保証DB/fleet analyticsを初期対象外へ下げる |
| ログ追加に戻っていないか | case packを先に作り、missing fact heatmapは二次成果物にする必要がある。 | High | 初期提供物から追加ログを外す |
| 次の意思決定は何か | 1ページsampleが8D/品質報告に転記できるかでProceed/Killできる。 | Medium | 次アクションをsample検証へ固定 |

## EPSサプライヤとしての最終判断

### 売るなら

> EPS RCA / 8D Evidence Case Pack Assessment

ただし、商品説明はこうする。

> 返却品、NTF、市場claim、SCAR/8D候補に対して、EPS製品側で確認できる事実、未確認事項、推定禁止事項、次に読むDID/試験/OEM要求データを、顧客品質報告に転記できる形で整理する短期assessment。

### 売らない

- 8D自動生成
- root cause断定
- 故障予測
- 劣化兆候通知
- ECUログ追加単体
- OEM保証analytics platform
- エンドユーザ通知

### 現時点の評価

> **Proceed as validation, not as business conclusion.**

ビジネスとして成立する可能性はあるが、今のままではまだ弱い。
次に必要なのは市場調査の追加より、`実際の8D/顧客品質報告に貼れる1ページcase pack sample` を作って、EPSサプライヤ内の品質/保証/診断担当が使うかを確認すること。

それが刺さらなければ、この仮説はKillでよい。
