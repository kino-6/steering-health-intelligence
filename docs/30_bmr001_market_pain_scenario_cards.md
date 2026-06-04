# BMR001 Market Pain Scenario Cards

## 結論

`BMR001 EPS Market Pain Scenario Library` は、現時点で最も進めやすい。

ただし売るものは、故障予測でも、ECU追加ログでも、既存診断不足の断定でもない。

売るものは、

> 公開市場で問題化したdriver-visible EPS painを、EPSサプライヤの評価、設計レビュー、RFQ、顧客品質説明で使えるscenario cardに変換すること。

つまり、公開データでできるのは `診断価値の証明` ではなく、`市場文脈を持った評価/レビュー材料の生成` である。

## 作ったもの

| File | 内容 |
|---|---|
| `data/bmr001_market_pain_scenario_cards.tsv` | 初期3枚のscenario card |
| `generated/bmr001_market_pain_scenario_cards.html` | scenario cardのブラウザ表示 |

## 初期3シナリオ

| ID | Scenario | 主な売り先 | 買われる理由 |
|---|---|---|---|
| SCN001 | low_speed_high_effort | validation; diagnostic engineering; sales engineering | 低速高操舵時のincreased steering effortを、評価項目とRFQ説明に変換できる |
| SCN002 | gradual_turn_sticking_oversteer | controls; validation; diagnostic engineering | 緩旋回時のassist continuity / state transition / driver feelを設計レビュー論点にできる |
| SCN003 | warning_plus_low_speed_effort | diagnostic engineering; customer quality; sales engineering | warning/DTC付きloss assistを、DTC snapshotと顧客品質説明のレビューに接続できる |

## 誰が嬉しいか

### EPS validation

嬉しいこと:

- 公開市場で揉めた文脈を評価シナリオへ落とせる
- HILS/bench/vehicle testの説明力が上がる
- `なぜこの評価をするのか` を市場文脈で説明できる

売れる成果物:

- scenario card
- public proxy window
- evaluation condition
- validation checklist

### EPS diagnostic engineering

嬉しいこと:

- DTC/freeze frame/extended dataが、driver-visible painを説明できるかをレビューできる
- 追加証跡の前に、既存診断で十分かを潰せる
- root cause断定ではなく、説明可能性の穴を確認できる

売れる成果物:

- diagnostic evidence question list
- DTC snapshot review checklist
- Proceed / Hold / Kill判定表

### Sales engineering / advanced development

嬉しいこと:

- RFQや設計レビューで、単なる機能表ではなく市場痛みへの備えを説明できる
- `health-ready` のような曖昧な主張を避け、`scenario readiness` として言える
- OEMにデータを要求する前に、サプライヤ側の提案材料を作れる

売れる成果物:

- RFQ paragraph
- design review page
- scenario readiness pack

### Customer quality

嬉しいこと:

- 公開事例ベースで、顧客説明に必要な事実項目を整理できる
- 何が確認済みで、何が未確認で、何を推定してはいけないかを分けられる

売れる成果物:

- customer-quality fact summary skeleton
- warning/DTC scenario checklist

## 収益モデル仮説

最初に売るなら、機能ライセンスよりサービス/パックが自然。

| Offer | 内容 | 初期価格感の考え方 |
|---|---|---|
| Paid research pack | 公開市場case 20-50件をscenario card化 | 調査/設計レビュー支援費 |
| 2-4 week workshop | 顧客の既存評価/DTC仕様にscenario cardを当てる | 固定費NRE |
| Quarterly update | 新規NHTSA/recall/ODI/TSBを定期分類 | subscription research |
| RFQ support add-on | RFQ/DRBFM/FMEA向けの説明ページを作る | 提案支援費 |

## Chain-of-Verification

| 検証質問 | 確認結果 | Confidence | 修正 |
|---|---|---:|---|
| 公開データだけでEPS故障予測を売れるか | 売れない。公開データは故障/劣化の内部状態を示さない。 | High | 故障予測主張を削除 |
| low-speed high-steering windowは故障再現か | いいえ。正常走行のproxy windowであり、評価文脈の例にすぎない。 | High | `representative proxy window` と明記 |
| BMR001は誰向けか | validation、diagnostic engineering、sales engineering、customer qualityに用途がある。 | Medium | カードごとにbuyer/jobを明記 |
| OEMデータが必要か | 初期scenario card作成には不要。ただし保証効果や実車相関の証明には必要。 | High | OEM dataは初期前提から外す |
| 既存FMEA/DRBFMと何が違うか | 違いは公開市場文脈と代表proxyを結び、RFQ/評価/診断レビューに再利用できる形にする点。 | Medium | Kill条件に「既存資産との差分なし」を追加 |
| SCN002で欠陥やroot causeを言えるか | 言えない。公開調査は文脈を示すだけ。 | High | assist continuity / state transitionレビューへ修正 |

## ここで言ってはいけないこと

- このカードで故障予測できる
- 劣化兆候を検出できる
- 既存DTC/freeze frameが不足している
- 公開走行windowがEPS故障を再現している
- OEM保証費を削減できる
- OEMサービスツール領域をサプライヤ単独で解決できる

## Kill条件

BMR001は、以下なら弱い。

- 既存FMEA/DRBFM/validation scenarioと差分がない
- 評価/診断/営業技術の誰も成果物を実務に転記しない
- 公開市場文脈が曖昧すぎて評価条件に落ちない
- RFQ/設計レビューで `public market pain scenario` の説明が刺さらない
- 追加調査しても、20-50件の市場caseを再利用可能なscenario familyへ分類できない

## 次アクション

次は、BMR001をさらに商品に近づけるため、`BMR002 RFQ / Design Review Evidence Pack` の1ページサンプルを作る。

狙いは、

> このscenario cardが、実際に提案資料や設計レビュー資料に転記できるか

を確かめること。

見るべき反応は、技術的な正しさだけではない。

- 評価担当が `この条件なら試験項目にできる` と言うか
- 診断担当が `このsnapshot項目はレビューできる` と言うか
- 営業技術が `RFQの差別化文言にできる` と言うか
- 品質担当が `顧客説明の事実整理に使える` と言うか

ここで反応が薄ければ、BMR001は調査レポート止まりであり、商品化は弱い。
