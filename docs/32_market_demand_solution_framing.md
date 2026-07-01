# Market Demand To Solution Framing

## 結論

前回までの提示は弱かった。

`こんな公開事例がある`、`こんなscenario cardが作れる` だけでは、事業仮説としては薄い。

市場需要から見ると、中心に置くべき問いはこれ。

> EPSサプライヤは、NTF、返却品解析、保証claim、SCAR/8D、顧客品質説明で、何を説明できなくて困っているのか。

この問いに対する初期仮説は以下。

> 市場には、返却品や保証claimだけでは再現/原因説明できない案件に対して、サプライヤ側が使えるproduct-side evidenceを早く、構造化して、顧客品質/RCA/8Dへ接続したい需要がある。

したがって、解決策は `EPS Market Pain Scenario Library` では弱い。
より良い解決名は、

> **EPS Warranty / RCA Evidence Readiness Pack**

である。

## 市場需要

| Demand | 市場で起きていること | 買い手 |
|---|---|---|
| DMD001 | NTF/返却品解析で、サプライヤがRCAに使える診断データを十分に得られない | EPS supplier warranty / quality |
| DMD002 | 保証、修理、返却品、DTC、技術者記述が分断され、解析に時間がかかる | OEM / supplier warranty |
| DMD003 | SCAR/8D/CAPAで、紙の回答ではなく、根本原因・是正・再発防止の証拠が求められる | Supplier quality / customer quality |
| DMD004 | SDV/connected diagnosticsでsubsystem evidence payload需要はあるが、OEM platform依存が強い | OEM connected diagnostics |
| DMD005 | EPSのdriver-visible painは公開recall/ODI/TSBで継続的に出ており、評価/診断レビューで先に潰したい | EPS validation / diagnostics |

## 解決策

### 本命: EPS Warranty / RCA Evidence Readiness Pack

売るもの:

- 返却品/NTF/保証claimで必要になるproduct-side factsの定義
- 既存DTC / freeze frame / extended dataで足りるかのレビュー
- 足りない場合でも、追加証跡を断定せず、`確認すべき項目` と `読める経路` を整理
- 顧客品質/8D/D4向けのfact summary skeleton

買い手:

- EPS supplier warranty
- supplier quality
- diagnostic engineering
- customer quality

なぜ買う可能性があるか:

- NTFや返却品解析は、現品だけ見ても原因が再現しないことがある
- OEM側の保証DBやサービス履歴に完全依存すると、サプライヤ側の説明が後手になる
- 既存診断で足りる/足りないを先に整理できれば、無駄な追加ログ提案を避けられる
- 8Dや顧客品質報告で、確認済み事実・未確認・推定禁止を分けられる

### 位置づけ変更

前回までのBMR001/BMR002は、主商品ではなく前段に下げる。

| Before | After |
|---|---|
| BMR001 Market Pain Scenario Libraryを売る | 公開市場caseを、Warranty/RCA Evidence Readinessの入力にする |
| BMR002 RFQ / Design Review Packを売る | RFQ/DRは副産物。主目的はNTF/RCA/品質説明で使える証拠設計 |
| scenario cardが価値 | scenario cardは、どの事実を確認すべきか決めるための索引 |

## 需要から見た提供価値

### 1. NTF / returned part RCA

市場需要:

> 返却品が再現しない、または原因が特定できない時、車両上で何が起きたかを説明したい。

解決:

> EPS ECUで読める既存DTC/freeze frame/extended dataと、必要なproduct-side factsをscenario別に照合する。

成果物:

- NTF evidence checklist
- scenario-to-fact matrix
- existing diagnostic coverage review
- missing evidence decision log

### 2. Warranty analytics integration

市場需要:

> 保証claim、修理記述、返却品、DTC、現品解析が分断されていて、RCAやclaim判断に時間がかかる。

解決:

> EPS側の事実を、保証解析に入れやすいfield schemaにする。

成果物:

- EPS evidence schema
- driver symptom to ECU facts mapping
- local readout / remote payload boundary

### 3. 8D / SCAR evidence attachment

市場需要:

> 8DやSCARで、root causeや是正効果を説明する証拠が必要。

解決:

> 8D回答を自動化するのではなく、D2/D4/D5に添付できる確認済み事実を整理する。

成果物:

- customer quality fact summary
- confirmed / unconfirmed / do-not-infer table
- next evidence request list

## これなら何が違うか

前回の弱い形:

> 市場にはこういうEPS事例があります。

今回の形:

> 市場ではNTF/返却品/RCA/8Dで証拠不足が痛みになっている。EPSサプライヤは、公開caseを使って典型scenarioを作り、既存診断で説明できるfactと足りないfactを棚卸しし、品質報告やRCAに接続できるEvidence Readiness Packを作れる。

この違いは大きい。

- 市場需要が `ケースの存在` ではなく `証拠不足による解析/説明コスト` になる
- 解決策が `調査レポート` ではなく `RCA/品質報告で使う成果物` になる
- 買い手が `なんとなくEPS関係者` ではなく `warranty / supplier quality / diagnostic engineering` になる
- Kill条件も `面白くない` ではなく `RCA/8D/品質報告に転記できない` になる

## Chain-of-Verification

| 検証質問 | 確認結果 | Confidence | 修正 |
|---|---|---:|---|
| 市場需要は本当にscenario cardなのか | いいえ。需要はNTF、保証、返却品、RCA、8Dで使える証拠に近い。 | High | scenario libraryを前段に下げた |
| EPSサプライヤが解決側に立てるか | OEM保証DBやfleet dataは持たないが、ECU-local product-side factsと既存診断レビューはサプライヤ領域。 | Medium-High | Supplier-owned scopeを限定 |
| 既存DTC/freeze frameと重複しないか | 重複の可能性が高い。だから追加証跡ではなく、既存診断で足りる/足りないを確認するreadiness packにする。 | High | 追加ログ提案を主商品から外した |
| 8D回答という言い方は危ないか | 危ない。root cause自動化ではなく、D2/D4/D5に添付するfact summaryに限定する。 | High | Evidence attachment kitに修正 |
| Connected diagnosticsは本命か | 需要はあるがOEM platform依存が強い。初期はoptional extension。 | Medium | DMD004を後段に下げた |

## 推奨する次の提示

次にユーザへ見せるなら、BMR001/BMR002ではなく、以下の1枚にする。

> **EPS Warranty / RCA Evidence Readiness Pack**

1ページの構成:

1. 市場需要: NTF/返却品/RCA/8Dでサプライヤ側の証拠不足が痛い
2. 解決: EPS scenario別に必要factを定義し、既存診断でカバーできるか確認する
3. 成果物: NTF checklist、DTC coverage matrix、fact summary、next evidence request
4. 初期PoC: SCN001 low-speed high effortを1ケースとして模擬レビュー
5. Kill条件: RCA/8D/顧客品質報告に転記できないなら事業化しない

## 次アクション

`SCN001 low-speed high effort` で、30分の模擬reviewではなく、以下を作る。

> NTF / returned-part RCA向けのEvidence Readiness Pack sample

必要な出力:

- market demand statement
- case narrative
- required product-side facts
- existing diagnostic coverage check
- confirmed / unconfirmed / do-not-infer table
- customer quality / 8D D2-D4 attachment sample
- kill criteria

これでようやく、`市場にはこの需要がある。その解決はこれ` という形になる。
