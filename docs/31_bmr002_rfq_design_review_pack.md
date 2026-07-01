# BMR002 RFQ / Design Review Evidence Pack

## 結論

BMR001のscenario card単体は、まだ弱い。

理由は簡単で、scenario cardは `調査したもの` に見えやすく、誰かの業務成果物に直接ならないから。

そこでBMR002では、scenario cardを次の1ページに変換する。

> OEM向けRFQや社内設計レビューでそのまま使える `Scenario Readiness Page`

この形にすると、価値は少し見えやすくなる。

## 何が嬉しいのか

BMR002の価値は、`新しい診断機能を提案すること` ではない。

価値は、

> EPSサプライヤが、市場で揉めた操舵文脈に対して、評価・診断・品質説明をどう確認しているかを1枚で説明できること。

つまり、売る相手はエンドユーザではない。
初期の売り先は、EPSサプライヤ内の以下の人たち。

| User | 嬉しいこと |
|---|---|
| Sales engineering | RFQ回答が、単なる機能表ではなく市場ペイン起点の説明になる |
| EPS validation | 既存HILS/bench/vehicle testに、市場文脈と優先度理由を付けられる |
| Diagnostic engineering | DTC/freeze frame/extended dataがdriver-visible painを説明できるか確認できる |
| Customer quality | warning/DTC付きloss assistを、原因断定せず事実整理できる |
| Program manager | OEM領域とサプライヤ領域を分けて、過大主張を避けられる |

## 1ページサンプルの構成

| Block | 役割 |
|---|---|
| Market Pain Coverage Statement | RFQ/DR冒頭で使う短い主張 |
| Scenario Readiness Matrix | 3つの市場ペインを評価・診断・品質説明に分解 |
| Supplier-Owned Boundary | サプライヤが言える範囲とOEM領域を分ける |
| Diagnostic Explainability Checklist | 既存診断snapshotで説明できるかを見る |
| Validation Scenario Hook | 公開proxy windowを試験条件の理由付けに使う |
| Customer Quality Fact Summary Skeleton | 顧客品質説明で、事実/未確認/推定禁止を分ける |

## サンプル文言

RFQ/設計レビューに貼るなら、最初の文言はこの程度が安全。

> 当社EPS提案では、公開市場で問題化した低速高操舵時のincreased effort、緩旋回時のassist continuity、warning/DTC付きloss assistをscenario readiness対象として扱い、評価条件、診断snapshot、顧客品質説明の観点を設計レビューで確認する。

この文言の良い点:

- `故障予測できます` と言っていない
- `既存診断が不足しています` と言っていない
- OEMデータを初期前提にしていない
- それでも、評価/診断/品質説明のレビュー対象が明確になる

## Scenario Readiness Page

| Scenario | 評価で見ること | 診断で見ること | 品質説明で見ること |
|---|---|---|---|
| Low-speed high effort | 低速高操舵時のmanual effort、assist limitation、safe-state | 速度、操舵角、assist state、limit/derating reason、電源、温度 | ドライバー症状とDTC/warning時点の対応 |
| Gradual turn sticking | 緩旋回時のassist continuity、state transition、復帰時の操舵感 | DTCなし/一過性時に状態遷移とdriver demandを説明できるか | 調査段階の公開事例として、root causeを断定しない |
| Warning plus effort | Warning/MIL/DTC発生前後のassist stateとdriver-visible context | component codeだけでなく、直前状態と発生条件を説明できるか | 確認済み事実、未確認、推定禁止を分ける |

## ここで価値が出る条件

BMR002は、以下の反応が取れれば前に進める。

- 営業技術が `この1ページをRFQ回答に貼れる` と言う
- 評価担当が `既存試験に市場文脈を付けられる` と言う
- 診断担当が `このチェック表ならDTC仕様をレビューできる` と言う
- 品質担当が `顧客説明の事実整理に使える` と言う

逆に言うと、これが出ないなら弱い。

## Chain-of-Verification

| 検証質問 | 確認結果 | Confidence | 修正 |
|---|---|---:|---|
| BMR002はOEMの領分に踏み込みすぎるか | 保証DB相関、サービス施策、fleet実績はOEM領域。BMR002は提案/評価/診断レビュー材料に限定すればサプライヤ側に残る。 | High | Supplier-Owned Boundaryを追加 |
| これは単なる調査レポートではないか | その危険がある。RFQ文言、matrix、checklist、fact summaryへ変換して初めて業務成果物になる。 | High | 1ページsample化 |
| 既存FMEA/DRBFMと差分があるか | 差分は市場ペインと公開proxyを評価/診断/品質説明に結び直す点。ただし既存資料に同等のものがあれば弱い。 | Medium | Kill条件に反映 |
| EPSサプライヤが初期に使えるか | 内部DTC仕様やOEM保証DBなしでも、RFQ/設計レビュー用の説明材料は作れる。 | Medium | 初期用途をsales engineering/validationへ寄せる |
| 故障予測や保証費削減を言えるか | 言えない。公開データだけでは証明できない。 | High | 禁止主張を明記 |

## Kill条件

BMR002は、次ならKillまたはHold。

- RFQ回答、設計レビュー、DRBFM、評価計画に転記できない
- 既存資料と差分がない
- OEMから `それは保証DB/サービスツールがないと意味がない` と返される
- サプライヤ内の評価/診断/品質のどの部門も使わない
- 1ページが抽象的で、具体的な確認項目に落ちない

## 次アクション

次は、このBMR002 sampleを使ってBMR003の前段を作る。

やること:

1. `SCN001 low-speed high effort` に絞る
2. 30分の模擬design review agendaを作る
3. 入力として必要な内部資料を `必須` と `あると良い` に分ける
4. 出力を `Proceed / Hold / Kill` ではなく、`RFQに貼れるか / 評価項目に落ちるか / 診断レビューに使えるか` で判定する

ここまでやっても価値が薄ければ、BMR001/BMR002は調査支援止まりで、事業の本命にはしにくい。
