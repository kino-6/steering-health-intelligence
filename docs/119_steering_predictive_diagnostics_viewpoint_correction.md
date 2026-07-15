# Steering Predictive Diagnostics Viewpoint Correction

## 結論

直近のSPD008のNext Actionは、診断企画向け1枚schemaを作ることではない。

次に判断すべきことは、EPS内部重要モジュールがruntimeで「普段と違う」状態に入りつつあることを検知、分類、説明できるか、そしてそれがpredictive diagnostics / vehicle healthの部品側contributionになるかである。

診断読み順、追加ログschema、品質feedback、顧客説明は、この価値仮説を検証するために必要な場合だけ作る副次artifactである。

## なぜ補正するか

Log上の起点は、次の仮説だった。

> EPSがruntimeで、過去一定期間や標準データに対して普段と違うことを検知できれば、付加価値になるのではないか。

ただし、その直後に重要な補正があった。

> EPS製品全体をE2Eで見ると、路面、タイヤ、車両重量、運転者、上位制御、外部ECU、電源、温度などの外乱が混ざり、外乱を特定できない。したがって、内部の重要モジュール単位に限定した方がよい。

このため、SPD008の中心は、診断資料ではなく、内部重要モジュール単位のruntime状態説明である。

## Market Demand

市場需要は、故障確定後にDTCを読むことだけではない。

製品企画、診断企画、品質改善、顧客技術説明の実務では、故障確定前または原因未確定の段階で、次を早く知りたい。

1. EPS内部重要モジュールが、通常範囲内だが普段と違う挙動に入りつつあるか
2. それが既存monitorやDTCだけでは残らない状態説明か
3. その状態説明が、vehicle healthやpredictive diagnosticsに渡せる部品側contributionになるか
4. それを使って、製品価値、診断価値、品質改善価値、顧客技術説明価値のどれを作れるか

## Rule Check

今回の補正では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Kaggle / Public Proxy Predictive Value Rule`
5. `Steering Predictive Diagnostics Value Rule`
6. `Mandatory Rule Check Before Stop / Kill / Archive`

確認結果:

- 市場需要は、故障確定後のDTC読解ではなく、故障確定前または原因未確定の段階で状態変化を早く知りたいことである
- EPS製品全体E2Eではなく、内部重要モジュール単位に限定する
- 診断読み順、追加ログ、品質feedback、顧客説明を最終目的にしない
- EPS RUL、交換時期、安全保証、root cause、保証費削減を主張しない
- 既存monitorで十分ならHoldまたはStopにする
- 内部事実不足は、原因断定や交換時期予測を禁止する境界であり、公開proxyやruntime状態説明の価値を即Killする理由にしない

## 洗い直した箇所

| Document | 以前のズレ | 補正後の読み方 |
|---|---|---|
| [AGENTS.md](../AGENTS.md) | SPD系の成果物が診断読み順や追加ログschemaへ寄りやすかった | `Steering Predictive Diagnostics Value Rule` を追加し、診断資料は副次artifactだと明記 |
| [docs/117](117_steering_predictive_diagnostics_spd008_vs_spd002_decision.md) | SPD008の価値を、追加ログ、診断読み順、品質feedback、顧客説明への転記に寄せすぎていた | runtime状態検知、既存monitorとの差分、vehicle healthへの部品側contributionを先に見る |
| [docs/118](118_steering_predictive_diagnostics_spd008_first_samples.md) | Next Taskが診断企画向け1枚schemaになっていた | power monitorとcommunication input validityをpredictive value checkとして洗う |
| [README.md](../README.md) | 次アクションが診断企画向け1枚schemaと読めた | 次アクションを、内部重要モジュールのruntime状態説明がpredictive diagnostics / vehicle healthの部品側contributionになるかの確認に修正 |
| [docs/98](98_business_model_mainline_after_correction.md) | SPD008 first samplesの目的が副次artifactへ寄っていた | runtime状態説明とpredictive value checkを中心に戻した |

## 正しいNext Action

次は、power monitorとcommunication input validityの2サンプルについて、次を確認する。

1. 何をruntimeで普段と違う状態として見るのか
2. 既存DTC、既存monitor、freeze frame、extended data、service manualだけで十分ではないか
3. EPSサプライヤが定義できる内部重要モジュール単位の状態説明は何か
4. それはpredictive diagnostics / vehicle healthの部品側contributionになるか
5. 製品企画、診断企画、品質改善、顧客技術説明のどの業務成果物に転記できるか
6. 診断読み順、追加ログschema、品質feedback、顧客説明は、その検証に必要な副次artifactとして何が必要か
7. どこからが原因断定、交換時期予測、安全保証、保証費削減、外乱原因断定に見えるため禁止か

## EPSサプライヤとしての言い方

言ってよいこと:

> EPS内部重要モジュールのruntime contextから、DTC未満または原因未確定の段階で、普段と違う状態を検知、分類、説明できるかを見る。既存monitorとの差分があり、vehicle healthやpredictive diagnosticsへ部品側の状態説明として渡せるなら、EPSサプライヤの付加価値候補になる。

まだ言ってはいけないこと:

> EPS交換時期が分かる。

> RULが分かる。

> 安全保証ができる。

> root causeを断定できる。

> 保証費削減を主張できる。

> E2E製品全体の外乱原因をEPS内部だけで特定できる。

## 次に作るもの

次に作るべきものは、診断企画向け1枚schemaではなく、次の2つである。

1. `SPD008 predictive value check`
   - power monitor
   - communication input validity
   - 既存monitorとの差分
   - runtime状態説明
   - vehicle healthへの部品側contribution
   - 買い手業務
   - 禁止主張

2. `supporting artifact list`
   - 上の価値検証に必要な場合だけ、trigger condition、snapshot fields、reading order、explanation boundary、quality feedback requirementを書く
