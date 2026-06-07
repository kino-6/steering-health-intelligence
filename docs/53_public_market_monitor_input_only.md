# 公開recall / ODI / TSB市場要求モニタの位置づけ

## 結論

公開recall、ODI、TSBのモニタは、**単体商品にしない**。

過去に見た通り、公開事例を集めるだけでは「こんな事例がある」で止まる。
これはEPSサプライヤの予算や業務成果物に入りにくい。

ただし、Steer-by-wireとSOVDを検証するための入力としては有効である。

使い方は次の3つに限定する。

1. steer-by-wireで説明すべき安全・冗長・異常時状態の市場トリガを見つける
2. SOVDで公開すべき診断コンテンツ、制限すべき診断コンテンツを見つける
3. RFQ / design review / OEM問い合わせで聞かれそうな質問を作る

## なぜ単体商品にしないか

公開市場情報は便利だが、それだけでは対象EPSの既存診断、既存評価、既存安全設計との差分を示せない。
これはCoverage Benchmarkで既に詰まった。

したがって、公開市場モニタは以下を主張しない。

- 自社EPSの故障予測
- 保証費削減
- 既存診断不足の断定
- recall予測
- 有償レポート単体の価値

## 入力としての使い方

| 入力先 | public caseから作るもの | 使い道 |
|---|---|---|
| Steer-by-wire | assist loss、warning、software/failsafe、steering feel、driver effortの市場トリガ | redundancy / fail-operational / driver feedbackの設計レビュー質問 |
| SOVD | DTC、warning lamp、freeze frameで説明すべきdriver-visible symptom | DTC/DID/freeze frame/exposure policyの診断コンテンツ質問 |
| RFQ / design review | 市場で問題化しやすい質問文 | OEM向け「このEPSはどう扱うか」の回答準備 |

## 初期artifact

作るなら、公開事例の要約ではなく、以下の形にする。

| Field | 内容 |
|---|---|
| public signal | recall / ODI / TSBで見えるdriver-visible pain |
| candidate link | Steer-by-wire / SOVDのどちらに効くか |
| design question | 設計レビューで聞く質問 |
| diagnostic question | 診断コンテンツで見る質問 |
| supplier boundary | EPSサプライヤが説明できる範囲 |
| do-not-claim | 言ってはいけないこと |
| kill if | どのartifactにも接続できない場合 |

## Kill条件

- 公開事例の要約だけで終わる
- Steer-by-wireまたはSOVDのartifactに接続できない
- 設計レビュー質問、診断コンテンツ質問、RFQ質問のいずれにも変換できない
- 対象EPSの既存資料なしに価値を断定し始める

## 現時点判断

現時点では **Input only**。

次にSteer-by-wireを掘る時に、公開市場モニタから質問を引く。
SOVDを掘る時も同じく、DTCやwarning、driver-visible symptomを診断コンテンツ設計の入力にする。

単体レポートやサブスクリプションとしては追わない。
