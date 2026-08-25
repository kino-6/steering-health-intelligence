# 153. SOTIF-EooC 仮定シート(本研究の実データで埋める)

## 判断

**EooCが部品側に要求する仮定は3つに分かれ、そのうち2つは本研究のデータで数値まで埋まり、1つは原理的に埋まらない。**

| EooCが要求する仮定 | 本研究で埋まるか |
|---|---|
| A. 使われ方の前提(assumptions of use) | **埋まる**。英国車検2,800万件の分母つき分布、車齢曲線、用途2型の分離まで |
| B. 機能不足(functional insufficiency)の観測粒度 | **埋まる。数値で言える**。特徴量別の設計で、応答遅れ0.3s / ゲイン0.10 / バイアス0.10 を90%検出([docs/155](155_window_recurrence_verification.md)で更新) |
| C. 機能不足の許容発生率の目標値 | **埋まらない。OEMが埋める欄**。車両レベル安全目標からの配分であり、公開情報では原理的に届かない。ここで問いを閉じる |

シート本体: [data/sotif_eooc_assumption_sheet.tsv](../data/sotif_eooc_assumption_sheet.tsv)(**33項目**。[docs/179](179_eooc_sheet_completion.md)でE節/F節を追加、[docs/180](180_eooc_sheet_all_filled.md)で残る4空欄を充填、[docs/195](195_capability_rule_second_mechanism_results.md)でG節「Capability決定則」7項目を追加。**うち1項目 EOOC033 は空欄でありOEMが埋める**)

> **追記(2026-08-22)**: [docs/162](162_pmsm_model_validation_results.md) の結果を2行反映した。
> **EOOC018** は本シート初の**実測に基づく行**である(合成注入ではない)——EPSアシストモータと同型・同出力帯のPMSMで、
> 巻線間短絡severityに対する相電流不平衡の実測関係。
> **EOOC019** は物理モデルによる外挿が**検証に失敗した**ことの記録であり、空欄として残す。

この作業は新規のデータ取得を伴わない。既存の [docs/144](144_synthetic_sensitivity_results.md) / [147](147_multiplatform_and_variant_verification.md) / [148](148_dvsa_mot_denominator_verification.md) / [150](150_advisory_precedence_verification.md) / [121](121_steering_predictive_diagnostics_power_monitor_case.md) の結果を、EooCの様式へ転記したものである。

## 何を判断しているか

自然言語で言うと、次を判断している。

> ISO 21448 は、部品サプライヤが全体システムを知らずに開発する場合の参加形式として SOTIF-EooC を定義している([docs/128](128_steering_predictive_diagnostics_sotif_public_signal_watch.md))。そこで部品側が差し出すのは「この使われ方の前提で、この種の機能不足はこの発生率以下」という仮定である。この仮定の各欄を、公開情報だけでどこまで具体的な数値で埋められるか。埋まらない欄はどれで、それはなぜか。

誰のどの業務の話か:

- OEM側: 機能安全 / SOTIF担当の、市場投入後フィールド監視と安全論証の維持業務
- EPSサプライヤ側: 安全担当のRFQ / 安全要件回答業務、製品企画のRFQ差別化業務

## 埋まる欄が意味すること

EooC で価値が出るのは「監視できます」という言明ではなく、**粒度を数値で宣言できること**である。

> 60秒の観測時間を特徴量ごとに配分すれば、0.3秒級の応答遅れ(15秒窓・4窓中2窓、誤検出3.6%)、10%級のアシスト特性変化(60秒窓・単発)、0.10 m/s² の定常オフセット(15秒窓・4窓中3窓)を90%検出できる。逆に0.1秒の遅れ・2%のゲイン変化はどの設計でも見えず、左右非対称はこの方式では宣言しない。

**検出できない領域を同じ精度で宣言できることが、仮定シートとしての質**である。EooCの仮定は市場で検証される前提なので、過大に書けば市場で外れる。[docs/144](144_synthetic_sensitivity_results.md) が非検出領域を対等に記録していたことが、そのまま様式上の強みになった。

さらに [docs/155](155_window_recurrence_verification.md) により、**設計則の優劣が4車種で一致する**ことが分かった。これは EooC の仮定を2階建てで書けることを意味する——**閾値は program 固有(NREで較正)、設計則は車種不変(製品仕様として宣言)**。単一の窓長で全特徴量を扱う当初案より、宣言できる範囲が広がった。

## 埋まらない欄と、その扱い

### C-1. 許容発生率の目標値([EOOC011](../data/sotif_eooc_assumption_sheet.tsv))

車両レベルの安全目標から部品へ配分される数値であり、OEMの安全コンセプトの内側にある。公開情報では届かない。

**ここで問いを閉じる。** [AGENTS.md](../AGENTS.md) 1条(内部情報・内部資料は使わない)および「内部情報を次アクション・再開条件にしない」に従い、内部資料の取得を次の一手に置かない。シート上は空欄のまま「OEMが埋める欄」と明示する——空欄であること自体が、部品側とOEM側の責任境界の記録である。

### C-2. KQ1 は依然として未確認([EOOC013](../data/sotif_eooc_assumption_sheet.tsv))

SOTIF-EooC という参加経路が規格上存在することは確認できたが、**SOTIF由来のfault未満監視要求がEPSサプライヤのRFQに実際に書かれている公開確認はできていない**([docs/128](128_steering_predictive_diagnostics_sotif_public_signal_watch.md))。[docs/126](126_steering_predictive_diagnostics_sotif_contribution_prospect.md) の「KQ1がYesと確認できない限りこの枝に工数を割かない」は維持する。

本シートは KQ1 を前提にしていない。**KQ1がYesになった時に即座に差し出せる形を、公開情報だけで先に作っておく**ものであり、枝のProceedではない。

## 実務上の制約: 仮定は program 単位でしか置けない

[docs/147](147_multiplatform_and_variant_verification.md) の「**手法は移る、閾値は移らない**」が、EooC の様式と正面から噛み合わない。

- EooC は「この使われ方の前提で、この機能不足はこの発生率以下」と**仮定を1つ**置く形式である
- しかし4車種比較では、健全時の誤検出率が3.4%〜10.2%、ゲイン15%の検出率が63%(CR-V)〜99.7%(Audi)と車種で動いた
- したがって単一の閾値・単一の発生率仮定を車種横断で置くことはできない

**これは弱点ではなく仕様である。** 車種ごとの母集団較正が要るということは、program ごとに較正作業が発生するということであり、[docs/146](146_business_framework_and_roadmap.md) 第1層の「診断コンテンツNRE」の根拠そのものである。汎用ライブラリとして売れないことは既に判定済みで、program付帯で売る形に寄せてある。シートには**制約としてではなく仕様として**書いた([EOOC012](../data/sotif_eooc_assumption_sheet.tsv))。

## 言えること / 言ってはいけないこと

言えること:

> EPSは、fault確定未満の機能影響contextを、部品内部の観測事実として残せる。観測粒度は数値で宣言でき、検出できない領域も同じ精度で宣言できる。これは車両レベルデータでは得られない観測点である。

言ってはいけないこと(既存の禁止事項を継承):

> SOTIF適合を証明できる / 安全性を保証できる / unknownリスクを潰せる / この監視で事故や故障を予防できる / EPS交換時期が分かる / 故障を予測できる / root causeを断定できる

加えて本シート固有の注意:

> [EOOC017](../data/sotif_eooc_assumption_sheet.tsv) の24.1倍は**検査員の目視観察の予測力**であって、ECU内部信号の予測力ではない([docs/150](150_advisory_precedence_verification.md))。「閾値未満の観察に予測情報が乗る」ことの実証であり、EPS内部runtime兆候→故障の直接検証ではない。仮定シート上でこの数字を内部信号の性能として転記しない。

## Rule Check

適用したルール: `Market Demand First` / `Natural Language First` / `EPS Supplier Lens` / `Steering Predictive Diagnostics Value Rule` / `Mandatory Rule Check Before Stop / Kill / Archive`

- 公開情報のみを使用。新規のデータ取得なし(既存結果の様式変換のみ)
- 内部依存の欄(C-1、C-2)は空欄として明示し、**次アクションにも再開条件にもしていない**
- 故障予測はKill維持。本シートに「いつ壊れるか」を当てる要素はない
- 主語がOEM領域に入っていないか: SOTIF論証の主語はOEM。EPSサプライヤは component boundary の観測提供者に徹している
- 手法(methodology)で競わない: Boschが定量SOTIF手法の特許で先行しているため、差分は「サプライヤEPS内部の観測事実」に限定した([docs/128](128_steering_predictive_diagnostics_sotif_public_signal_watch.md))

## 範囲の宣言

本作業は **EooC様式への転記1回きり、新規データ取得なし** で範囲を切る。シートの空欄を埋めるための追加調査は起こさない。

## Sources

- ISO 21448:2022 の SOTIF-EooC(assumptions of use / 機能不足の許容発生率)の理解は [docs/128](128_steering_predictive_diagnostics_sotif_public_signal_watch.md) の観測に基づく
- 数値の出所は [docs/144](144_synthetic_sensitivity_results.md) / [147](147_multiplatform_and_variant_verification.md) / [148](148_dvsa_mot_denominator_verification.md) / [150](150_advisory_precedence_verification.md) / [151](151_high_rate_model_crosscheck.md) / [121](121_steering_predictive_diagnostics_power_monitor_case.md)
- 元データの出典・ライセンスは [SOURCES.md](../SOURCES.md)
