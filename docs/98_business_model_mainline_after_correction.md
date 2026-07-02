# Business Model Mainline After Correction

## 結論

ビジネスモデルの本線は、故障予測ではない。
EPSの交換時期を当てることでも、fleet監視サービスでも、remote diagnostics platformでもない。

本線に戻すべきものは、OEMが想定する車両用途や使われ方を、EPSサプライヤ側の確認観点、提案観点、説明境界へ翻訳できるかを見る固定スコープの検証である。

公開proxyは、OEMの車両コンセプトを決めるために使うものではない。
RFQ前後や顧客技術説明の前に、次のような観点をEPSサプライヤ側で準備するための材料として使う。

1. OEMが想定する用途では、低速、反復操舵、大舵角、段差、路面外乱がどの程度重要になるか
2. その用途想定を、EPSの製品価値、評価観点、診断説明、顧客説明のどの質問に変えるか
3. 通信異常があるとき、操舵系の説明で何を信用してよいか、何を言ってはいけないか

これらは、EPSが壊れるかどうかの予測ではない。
公開proxyだけで、OEM用途想定を代替したり、平均的な乗用車と厳しい用途を勝手に線引きしたりする話でもない。
EPSサプライヤが、OEMの用途想定を受け取ったときに、自社側の製品企画、診断企画、品質改善、評価企画、顧客技術説明へどう翻訳するかを見る。

したがって、初期のビジネスモデルはSaaSではない。
外部fleet向けの監視商品でもない。

最初は、EPSサプライヤ向けの固定スコープassessmentである。
2週間程度で、公開proxyと既存調査を使い、OEM用途想定をEPS側の確認観点へ翻訳する1枚資料、見えるproxy、言ってよい価値、禁止主張、部署別のProceed/Kill質問をまとめる。

詳細表は [data/business_model_mainline_after_correction.tsv](../data/business_model_mainline_after_correction.tsv) に置く。

この結論を受けた4枚の最小パックは、[docs/100_oem_usage_translation_minimum_pack.md](100_oem_usage_translation_minimum_pack.md) と [data/oem_usage_translation_minimum_pack.tsv](../data/oem_usage_translation_minimum_pack.tsv) に置く。
その4枚を社内で確認する質問票は、[docs/101_oem_usage_translation_review_questions.md](101_oem_usage_translation_review_questions.md) と [data/oem_usage_translation_review_questions.tsv](../data/oem_usage_translation_review_questions.tsv) に置く。

追加で、Boschの公開情報から、by-wire、vehicle motion management、vehicle computer、AI活用が同じSDV文脈で語られていることを確認した。
これはEPS故障予測の根拠ではないが、上位motion-domain制御から操舵側へ来る要求を、EPSサプライヤの受け入れ境界、制限境界、診断境界、禁止主張へ翻訳する必要が増える可能性を示す。
この枝は [docs/102_bosch_motion_domain_ai_signal_review.md](102_bosch_motion_domain_ai_signal_review.md) と [data/bosch_motion_domain_ai_signal_review.tsv](../data/bosch_motion_domain_ai_signal_review.tsv) に置く。

さらに2026年のBosch / Uptake発表とBosch Predictive Diagnosticsを確認すると、fleet / connected vehicle / cloud diagnosticsの文脈では、AI-driven predictive maintenance、vehicle health services、component-specific load and diagnostic featuresが明確に出ている。
この予測はEPS単体の交換時期予測だけではない。EPSサプライヤがsteering predictive diagnosticsとして何を予測対象にでき、predictive maintenance actionやvehicle health outputへどうつなげられるかを見る根拠になる。
この補正は [docs/103_bosch_predictive_diagnostics_meaning_review.md](103_bosch_predictive_diagnostics_meaning_review.md) と [data/bosch_predictive_diagnostics_meaning_review.tsv](../data/bosch_predictive_diagnostics_meaning_review.tsv) に置く。
公開情報から抽出した操舵系predictive state候補は、[docs/104_steering_predictive_state_candidate_scan.md](104_steering_predictive_state_candidate_scan.md) と [data/steering_predictive_state_candidates.tsv](../data/steering_predictive_state_candidates.tsv) に置く。

改めてBoschの予測ビジネスを収集・分析した結果、Boschの本線はAIモデル単体ではなく、接続、クラウド診断、predictive diagnostics、predictive maintenance、vehicle health、整備計画、保証・品質判断までを束ねる業務パッケージであると整理した。
EPSサプライヤ側では、Bosch型platformを自前で作るのではなく、操舵系をpredictive diagnostics / predictive maintenance / vehicle healthの対象として扱うためのstate、必要データ、整備action、禁止主張を切ることが次の論点になる。
この分析は [docs/105_bosch_predictive_business_analysis.md](105_bosch_predictive_business_analysis.md) と [data/bosch_predictive_business_analysis.tsv](../data/bosch_predictive_business_analysis.tsv) に置く。
次に実施するscreening計画は [docs/106_steering_predictive_diagnostics_screening_plan.md](106_steering_predictive_diagnostics_screening_plan.md) に置く。
Phase 1/2の実行結果として、Bosch型予測ビジネスの要求を操舵系screening要求へ変換し、既存の操舵系predictive state候補を再整理した。
結果は [docs/107_steering_predictive_diagnostics_state_screening.md](107_steering_predictive_diagnostics_state_screening.md)、[data/steering_predictive_diagnostics_screening_requirements.tsv](../data/steering_predictive_diagnostics_screening_requirements.tsv)、[data/steering_predictive_diagnostics_state_screening.tsv](../data/steering_predictive_diagnostics_state_screening.tsv) に置く。
Proceed候補を深掘りし、低/高電圧または過温度によるreduced assist、複合電気症状、外部信号/通信validity、熱保護近傍、DTC履歴再発監視の順でPhase 3対象に置いた。
この深掘りは [docs/108_steering_predictive_diagnostics_proceed_deep_dive.md](108_steering_predictive_diagnostics_proceed_deep_dive.md) と [data/steering_predictive_diagnostics_proceed_deep_dive.tsv](../data/steering_predictive_diagnostics_proceed_deep_dive.tsv) に置く。
Phase 3では、5件について必要データと権限境界を切った。
EPSサプライヤ単独で言える範囲は、state定義、診断読み順、EPS内部故障と外部contextを混同しない説明境界であり、RUL、交換時期、failure prediction、保証費削減、安全保証はrepair feedbackやOEM/fleet/platform dataなしでは言わない。
この結果は [docs/109_steering_predictive_diagnostics_data_boundary.md](109_steering_predictive_diagnostics_data_boundary.md) と [data/steering_predictive_diagnostics_data_boundary.tsv](../data/steering_predictive_diagnostics_data_boundary.tsv) に置く。
Phase 4では、Phase 3のdata boundaryをEPSサプライヤ内の部署別成果物へ転記できるかを見た。
診断企画、顧客技術説明、service / aftermarket連携、品質改善には具体用途が残る。
この結果は [docs/110_steering_predictive_diagnostics_supplier_workflow_fit.md](110_steering_predictive_diagnostics_supplier_workflow_fit.md) と [data/steering_predictive_diagnostics_supplier_workflow_fit.tsv](../data/steering_predictive_diagnostics_supplier_workflow_fit.tsv) に置く。
Phase 5では、操舵系predictive diagnosticsを固定スコープの内部/顧客技術向けassessmentとしてProceedにした。
ただし、これはEPS RUL、交換時期予測、Bosch型fleet predictive maintenance platform、安全保証、root cause / warranty cost reductionとしてProceedする判断ではない。
最終判断は [docs/111_steering_predictive_diagnostics_screening_decision.md](111_steering_predictive_diagnostics_screening_decision.md) と [data/steering_predictive_diagnostics_screening_decision.tsv](../data/steering_predictive_diagnostics_screening_decision.tsv) に置く。
追加で、SPD002だけに閉じず、SPD003、SPD004、SPD001、SPD007、内部重要モジュールのruntime deviation案を並列に深掘りした。
runtime deviation案は、EPS製品全体E2Eでは外乱が多すぎるため、torque / angle sensor plausibility、motor / inverter response、power monitor、thermal derating、communication input validityのような内部重要モジュール単位に限定する。
この並列深掘りは [docs/112_steering_predictive_diagnostics_parallel_continuation_deep_dive.md](112_steering_predictive_diagnostics_parallel_continuation_deep_dive.md) と [data/steering_predictive_diagnostics_parallel_continuation.tsv](../data/steering_predictive_diagnostics_parallel_continuation.tsv) に置く。
その中で見込みがある候補をさらに深掘りした結果、伸びしろはSPD008、実証しやすさはSPD002、実務価値はSPD003、vehicle health接続はSPD004にあると整理した。
SPD001は二番手以下、SPD007はrepair feedback loopが見える場合だけ条件付きで扱う。
この整理は [docs/113_steering_predictive_diagnostics_promising_candidate_deep_dive.md](113_steering_predictive_diagnostics_promising_candidate_deep_dive.md) と [data/steering_predictive_diagnostics_promising_candidate_deep_dive.tsv](../data/steering_predictive_diagnostics_promising_candidate_deep_dive.tsv) に置く。

## Logからの補正: 駐車場ではなくOEM用途の翻訳

直近の議論で補正すべき点は、「駐車場 + 低速 + 大舵角 + 凹凸」を有望用途として先に置くと、意味がぼやけることである。
駐車場はほぼすべての乗用車に関係する既知の使われ方であり、それ自体を見つけてもEPSサプライヤの差分にはなりにくい。

また、「平均的な乗用車ではなく使われ方が厳しい用途を特定する」という言い方も、そのままだとOEMの車両コンセプト定義に近い。
OEMがどの用途、車格、サービス、運行シーンを狙うかはOEM側の仕事であり、EPSサプライヤが公開proxyだけでそれを決める話ではない。

EPSサプライヤ側の価値は、OEMから用途想定や車両コンセプトが出てきたときに、それを次の業務観点へ翻訳することである。

1. RFQで確認すべき低速取り回し、反復操舵、路面外乱、温度、電源、通信の質問
2. 評価企画で厚く見るべき使用条件と、既存評価で足りる条件の切り分け
3. 診断企画で使用contextとして説明してよいことと、DTCや内部状態がないと説明してはいけないこと
4. 顧客技術説明で、EPSの製品価値として言えることと、故障予測や原因断定に見えるため避けること

したがって、正しい表現は次である。

> OEMが想定する低速、反復操舵、路面外乱を含む用途を、EPSサプライヤ側の確認観点、提案観点、説明境界へ翻訳できるかを見る。

公開proxyは、この翻訳観点を事前に用意する材料である。
公開proxyが用途を決めるのではなく、OEM用途想定を受けたときに、EPS側がどんな問いを返すべきかを準備する。

## Rule Check

今回の判断では、[AGENTS.md](../AGENTS.md) の次の上位ルールを適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Kaggle / Public Proxy Predictive Value Rule`
5. `Mandatory Rule Check Before Stop / Kill / Archive`

この文書では、`Stop` や `Kill` を主結論にしていない。
ただし、Kill条件を書くため、次を確認する。

- Kill理由を「EPS内部状態、DTC、freeze frame、交換結果が見えないから」にしない
- 公開proxy価値を、EPS内部故障事実の代替にしない
- 判断軸を、EPSサプライヤの業務成果物へ転記できるかに置く
- 汎用テレマティクス、路面分類、ADAS、IDSと区別できるかを見る
- 故障予測、交換時期、保証費削減、原因断定に寄せず価値説明できるかを見る

## 市場需要

低速取り回し、駐車、狭い場所での大舵角操作、段差、荒れた路面、振動、stop-start、通信異常は、ユーザやサービス現場に見えやすい困りごとである。
OEMは、それらを車両コンセプト、用途想定、評価条件、サービス要件として整理する。

EPSサプライヤにとって重要なのは、これらを故障原因として扱うことではない。
OEMの用途想定を受けたときに、低速取り回し、操舵感、路面外乱下の違和感、診断説明の難しさを、EPS側の確認観点、提案観点、説明境界へ変換できることである。

その言葉があれば、製品企画、診断企画、品質改善、評価企画、顧客技術説明が、OEM用途想定を同じ前提で読み替えて会話できる。

## 未解決の痛み

Kaggleや公開データには、操舵角、速度、stop-start、路面・振動、traffic、凹凸、通信異常のproxyがある。

しかし、それをそのまま出すと、一般的な運転行動分析、路面分類、ADAS制御、汎用IDSに見える。
EPSサプライヤが主語になりにくい。

未解決の痛みは、公開proxyそのものが足りないことではない。
また、OEMの用途想定をEPSサプライヤが代わりに決めることでもない。
公開proxyやOEM用途想定を、EPSサプライヤの業務成果物に貼れる言葉へ変換できていないことである。

例えば、次のように変換できるかが論点になる。

| 公開proxy | そのままだと | EPSサプライヤ向けに変換するなら |
|---|---|---|
| 低速、大舵角、凹凸 | 運転行動分析 | OEM用途想定を低速取り回しのRFQ/評価/説明質問へ変換 |
| 荒れた路面、操舵入力 | 路面分類 | OEM用途想定を品質改善や評価代表性の確認観点へ変換 |
| 通信異常、spoofing、DoS | 汎用IDS | 操舵系説明で信用してよい情報と禁止主張を分ける境界 |

## 仮説

公開proxyだけでも、低速、反復操舵、路面外乱、通信異常contextのような観点を事前に整理できる。

その整理が、OEM用途想定を受けたときに、EPSサプライヤの製品価値説明、診断説明境界、品質改善、評価代表性確認、顧客技術説明へ翻訳する助けになるなら、予測のような付加価値候補になる。

ここでいう「予測のような付加価値」は、個車のEPS故障や交換時期を当てることではない。

先に準備できると嬉しいのは、次のようなことである。

1. OEMがその用途を狙うなら、低速、反復操舵、大舵角、段差、路面外乱のどれをRFQで確認すべきか
2. その使われ方では、DTCの有無とは別に、体感説明が難しくなる可能性をどう説明境界に置くか
3. その路面・操舵contextを、品質改善や評価代表性の見直しに転記できるか
4. その通信異常contextでは、操舵系の説明で使ってよい情報と使ってはいけない情報をどう分けるか

## 解決策

初期提供物は、OEM用途想定をEPS側の確認観点へ翻訳する検証パックである。

これは商品名ではなく、やる仕事の説明である。
公開proxyを使い、EPSサプライヤの各部署が判断できる1枚資料へ落とす。

最初のパックは4枚に絞る。

| Artifact | 目的 | 初期利用者 |
|---|---|---|
| 低速・反復操舵・路面外乱の製品企画向け1枚 | OEM用途想定をEPS価値説明とRFQ確認質問へ変換できるかを見る | 製品企画、商品企画 |
| 低速・反復操舵・路面外乱の診断企画向け1枚 | DTC有無にかかわらず、使用context説明の境界を作れるかを見る | 診断企画、サービス技術 |
| 荒れた路面と操舵の品質・評価向け1枚 | OEM用途想定を品質改善や評価代表性の見直しに使えるかを見る | 品質改善、評価企画 |
| 通信異常contextの説明境界1枚 | EPS故障と通信異常を混同しないための禁止主張を作れるか見る | 診断企画、サイバー担当、顧客技術説明 |

## 買い手 / 利用者

初期の利用者は、外部fleetやエンドユーザではない。

初期利用者は、EPSサプライヤ内の次の部署である。

- 製品企画
- 診断企画
- 品質改善
- 評価企画
- 顧客技術説明
- サイバー担当

買い手として置くなら、商品企画またはprogram technical leadに近い。
ただし、現時点では独立予算があるとは言わない。
最初は、特定programまたは社内検討の固定スコープassessmentとして扱う。

## Why Supplier Can Play

EPSサプライヤが持つべき手札は、EPS内部故障事実でも、OEM車両コンセプトの代替定義でもない。

この本線で持つ手札は、OEMが示す用途想定を、低速取り回し、操舵感、路面外乱、診断説明、顧客技術説明、品質改善、評価代表性という自社製品の言葉へ翻訳できることである。

公開proxyを、EPS内部stressや故障原因へ変換しようとすると破綻する。
しかし、公開proxyを、OEM用途想定を読むための確認質問や説明境界へ変換するなら、EPSサプライヤの部品境界に残れる。

## ビジネスモデル

初期の形は、固定スコープassessmentである。

| 項目 | 内容 |
|---|---|
| 提供形態 | 2週間程度の固定スコープassessment |
| 入力 | Kaggle / 公開proxy、既存の公開調査、OEM用途想定を読むための使用条件family、禁止主張 |
| 出力 | 4枚の部署別判断資料、OEM用途想定からEPS側確認観点への翻訳表、ID別Proceed/Kill表、禁止主張リスト |
| 初期利用者 | 製品企画、診断企画、品質改善、評価企画、顧客技術説明 |
| 価値 | OEM用途想定を受けたRFQ質問、用途別価値説明、診断説明境界、品質改善の見方、評価代表性、通信異常時の説明境界 |
| 売らないもの | 故障予測、交換時期予測、保証費削減、fleet監視、remote diagnostics platform |

このassessmentで2部署以上に具体的な使い道が出るなら、次に特定program向けの短期支援へ進める。
使い道が出ないなら、この方向は止める。

## 検証方法

次にやるべきことは、外部データをさらに掘ることではない。
4枚の判断資料を作り、次の質問に答えられるかを見ることである。

1. 製品企画は、OEM用途想定に含まれる低速・反復操舵・路面外乱を、EPS価値説明とRFQ確認質問に変換できるか
2. 診断企画は、同じ用途想定を、DTC有無にかかわらず使用context説明の境界に変換できるか
3. 品質改善または評価企画は、荒れた路面と操舵contextを、既存NVH/耐久/評価とは違う確認観点として使えるか
4. 診断企画またはサイバー担当は、通信異常contextを、操舵系説明の信用境界として使えるか
5. これらが、汎用テレマティクス、路面分類、ADAS、IDSと区別できるか

## Proceed条件

この本線を進めてよい条件は、以下である。

1. 少なくとも2部署が、既存成果物に貼れる具体用途を挙げる
2. `ULC008` が製品企画または診断企画のどちらかで具体用途を持つ
3. `ULC004` が品質改善または評価企画で既存分類と違う見方を出す
4. `PVC004` が汎用IDSではなく、操舵系説明の禁止主張に使える
5. 故障予測、交換時期、保証費削減、原因断定に寄らず価値説明できる

## Kill条件

この本線を止める条件は、以下である。

1. OEM用途想定から作った確認観点が、どの部署の成果物にも転記できない
2. 一般的な運転行動分析、路面分類、ADAS、IDSと区別できない
3. 価値説明に、故障予測、交換時期、保証費削減、原因断定が必要になる
4. EPSサプライヤが主語になれず、OEM fleet platformやサービス事業者の領域に吸収される
5. 既存の製品説明、診断説明、品質分類、評価代表性確認と同じ言葉にしかならない

重要なのは、次である。

> EPS内部状態やDTC、freeze frame、交換結果が見えないこと自体は、この本線のKill理由ではない。

それらは、故障予測や原因断定をしないための境界である。

## EPSサプライヤとしての言い方

言ってよいこと:

> 公開proxyから、低速、反復操舵、大舵角、段差、荒れた路面、操舵要求、通信異常contextのような確認観点を事前に準備できる可能性がある。これはEPS故障予測でも、OEM用途コンセプトの代替でもない。OEM用途想定を受けたときに、EPSサプライヤの製品企画、診断企画、品質改善、評価企画、顧客技術説明へ翻訳できるかを見る固定スコープの検証である。

まだ言ってはいけないこと:

> 公開proxyからEPS故障、残寿命、交換時期、保証費削減、安全性、root causeが分かる。

> 駐車操作、低速高操舵、荒れた路面、通信異常がEPS故障原因である。

> EPSサプライヤが公開proxyだけでOEMの車両コンセプトや厳しい用途を定義できる。

> 使用条件classを作れば、fleet downtimeや保証費を削減できる。

## CoVe

| 検証質問 | 回答 | Confidence | 反映 |
|---|---|---:|---|
| 上位ルールに戻っているか | Yes。Kaggle/Public Proxyでは内部事実不足を主Kill理由にしない。 | High | Rule Checkに明記 |
| 市場需要から始まっているか | Yes。低速取り回し、駐車、荒れた路面、通信異常の困りごとと、OEM用途想定をEPS側へ翻訳する必要から始めている。 | Medium | 市場需要に反映 |
| EPSサプライヤの業務成果物に戻っているか | Yes。製品企画、診断企画、品質改善、評価企画、顧客技術説明に戻した。 | Medium | 初期利用者と検証方法に反映 |
| 外販商品として言いすぎていないか | Yes。SaaSや故障予測ではなく、固定スコープassessmentに縮めている。 | High | ビジネスモデルに反映 |
| まだ弱い点は何か | 汎用テレマティクス、路面分類、ADAS、IDSとの差分と、OEM用途想定を受けたときに既存RFQ/評価/診断業務を超える差分があるかは未検証。 | Medium | Kill条件に反映 |
