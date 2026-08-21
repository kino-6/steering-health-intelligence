# SOTIF Contribution Prospect Deep Dive

## 結論

「SOTIFに乗っかれるプロダクト」の見込みを、3つの意味に分解して判定した。

| # | 「SOTIFに乗る」の意味 | 判定 | 理由 |
|---|---|---|---|
| a | SOTIFプロセス支援商品(分析代行、適合支援、教育) | **No-Go** | 既存Kill(汎用安全支援はISO 26262 / SOTIF / CSMS既存業務と被る)と同一。持ち主が既にいる |
| b | SOTIF論証への部品側証拠(安全コンセプト回答の一部) | **既存業務。新商品ではない** | FMEA、safety case、UN R79適合証拠として既に安全担当が出している。SPDが足すものは(c)の運用フェーズ側だけ |
| c | SOTIF運用フェーズのフィールド監視への部品側インプット | **条件付きで検証候補に追加** | ISO 21448:2022は市場投入後のフィールド監視を要求する。車両レベルデータでは「fault未満だが機能影響あり」の部品内部contextが見えない。これはSPD008が特定済みの差分と同じ穴であり、**新プロダクトではなくSPD008 payloadの宛先追加**として乗れる |

あわせて、故障予測(RUL / 交換時期 / 故障発生予測)の判定は**Kill維持**である。
今回の(c)は故障予測の看板掛け替えではない。「いつ壊れるか」を当てる話ではなく、「fault未満で機能が細った瞬間の記録を、安全側の監視ループに観測事実として渡す」話である。当てる要素はどこにもない。

詳細表は [data/steering_predictive_diagnostics_sotif_contribution_prospect.tsv](../data/steering_predictive_diagnostics_sotif_contribution_prospect.tsv) に置く。

## 何を判断しているか

自然言語で言うと、次を判断している。

> OEMは、ADAS / 自動運転 / by-wireの機能について「故障していないのに性能限界や想定外シナリオで危険になる」リスク(SOTIF)を、市場投入後も監視し続ける義務を負いつつある。EPSサプライヤが検証中の「DTC未満だが機能影響があった瞬間の記録」(SPD008)は、その監視ループに部品側から差し込む価値になるか。それとも、既存の安全成果物や車両レベル監視で足りていて、差分がないか。

誰のどの業務の話か:

- OEM側: 機能安全 / SOTIF担当の、市場投入後フィールド監視と安全論証の維持業務
- EPSサプライヤ側: 安全担当のRFQ / 安全要件回答業務、製品企画のRFQ差別化業務。**OEM安全チームに直接売る話ではない**

## Rule Check

今回の判断では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Steering Predictive Diagnostics Value Rule`
5. `Mandatory Rule Check Before Stop / Kill / Archive`

特に次を自己点検した。

- **過去にKillした仮説を名前だけ変えて再提案していないか**: (a)は再提案にあたるためNo-Goを維持した。(c)は「故障予測」でも「汎用安全支援」でもなく、SPD008で検証中のartifactの宛先追加であり、新規の売り物を作らない
- **禁止主張に寄っていないか**: 安全保証、SOTIF適合の証明、unknown riskの消滅宣言は言わない。言えるのは「EPSが観測した事実」まで
- **主語がOEM領域に入っていないか**: SOTIF論証の主語はOEM。EPSサプライヤはcomponent boundaryの観測提供者に徹する
- **Killの理由**: (a)のNo-Goは「内部事実が見えないから」ではなく「既存業務に持ち主がいるから」であり、ルールに整合する

## 市場需要

公開情報で確認できる範囲:

1. **ISO 21448:2022(SOTIF)は、運用フェーズの活動を規格本文に含む**。市場投入後にフィールド挙動を観測し、新たなSOTIF課題を検知し、更新や対策につなげるプロセスが求められる。SOTIFは一度の適合で終わらず、監視し続ける義務になった
2. **UN R79(操舵装置)は、SbWを含む操舵の正常時・故障時要求を規定し、電源など支援システムも対象に含む**。操舵の機能低下は型式認証レベルの関心事である
3. L3以上の自動運転(UN R157系)では、走行データの記録と市場投入後の報告の枠組みが強化されており、「市場で何が起きたかを説明できること」への要求は増える方向にある
4. by-wire / motion-domain化で、操舵はADASや自動運転のintended functionの実行部品になる。**「fault未満のアシスト制限・fallback」は、車両機能から見ると性能不足(SOTIFの主題)として現れる**

つまり市場需要は、「操舵の故障予測」ではなく、「**市場投入後に、故障未満の機能低下を観測・説明し続ける能力**」である。

## 未解決の痛み

OEMのフィールド監視が実際に使えるデータは、車両レベルに寄る。

- テレマティクス: 車両レベルの電圧・DTC・走行データ(docs/125で確認済み。既存商品)
- DTC / freeze frame: 故障確定の証拠として設計されている(docs/125で確認済み)
- 走行記録(DSSAD等): 車両挙動と操作の記録であり、部品内部状態ではない

一方、SOTIFが本当に見たい「faultなしで機能が細った瞬間」は、部品内部にしか痕跡がない。
[docs/125](125_steering_predictive_diagnostics_unverified_delta_check.md) で特定したSPD008の3つの本物の差分は、そのままSOTIFフィールド監視の穴でもある。

1. デバウンス閾値未満のevent(短い電圧dip、散発的timeout)はどこにも残らない
2. 機能影響(assist limitation / fallback)との同時性は残らない設計が多い
3. DTC未満eventのkey cycle横断の再発は数えられない

## 仮説

> EPSサプライヤは、SPD008で検証中の最小payload(「EPSがassist制限近傍で短い電源不安定を観測した」等)を、vehicle health基盤向けだけでなく、**OEMのSOTIF運用フェーズ監視への部品側インプット**として同じ形で提供できる。売り物は変わらない。宛先と言い方が1つ増えるだけである。

SOTIFの言葉で言うと、EPSが観測できる電源不安定、通信validity揺らぎ、熱deratingは、操舵機能の性能低下を引き起こす**triggering condition候補のうち、部品内部でしか観測できないもの**である。ここはテレマティクスにもOEMにも見えない。EPSサプライヤだけが出せる。

## 解決策 / 初期提供物

新しいものは作らない。既存artifactへの追記3点に限定する。

1. [docs/122](122_steering_predictive_diagnostics_power_monitor_payload_sample.md) のminimum payloadに、SOTIF文脈で使う場合のboundary行を追加する(「観測事実の提供であり、安全論証・SOTIF適合の証明ではない」)
2. EPS視点のtriggering condition候補リスト: 電圧dip(SPD008 power monitor)、依存signal揺らぎ(SPD008 comm input validity)、熱derating(SPD004系)。既にSPDの対象と一致しており、リストの再編だけ
3. RFQ / 安全要件の確認質問(KQ)を、下の検証方法の形で質問表化する

## 買い手 / 利用者

- 初期の利用者はEPSサプライヤ**サプライヤ内**の安全担当と製品企画である。RFQや安全コンセプト回答で、SOTIF由来の監視・通知要求が来たときに、SPD008 payloadを回答の部品として使う
- OEMのSOTIF / 機能安全チームは接続先であり、直接の販売先ではない
- 診断企画・品質改善・顧客技術説明(既存のSPD008買い手)は変わらず主宛先。安全側は**5番目の宛先**として追加する

## EPSサプライヤとして言えること / 言ってはいけないこと

言ってよいこと:

> EPSは、fault確定未満の機能影響context(電源不安定とassist制限の近接、依存signal揺らぎとfallbackの近接)を、部品内部の観測事実として残し、OEMの運用フェーズ監視へ提供できる。これは車両レベルデータでは得られない観測点である。

言ってはいけないこと:

> SOTIF適合を証明できる。安全性を保証できる。unknownリスクを潰せる。

> この監視で事故や故障を予防できる。

> EPS交換時期が分かる。故障を予測できる。root causeを断定できる。

## 検証方法(KQ)

| KQ | 質問 | Yesなら | Noなら |
|---|---|---|---|
| KQ1 | 対象OEMのRFQ / 安全要件に、SOTIF / 運用フェーズ監視に由来する要求(fault未満の機能低下の記録・通知・報告)が実際に含まれ始めているか | 続行 | **この枝はKill**(vehicle health宛先だけ残す) |
| KQ2 | docs/123の照合で、既存設定では残らない差分が確認できたか(前提条件) | 続行 | SPD008ごとHold / Stop(docs/122のGate) |
| KQ3 | その要求に、既存安全成果物(FMEA、safety case、UN R79適合証拠、既存監視仕様)で既に答えられていないか | **Kill**(重複) | 続行 |
| KQ4 | 安全保証・適合証明を主張せずに、観測事実の提供だけで価値説明が成立するか | 続行 | **Stop**(禁止主張が必要になる) |
| KQ5 | サプライヤ内安全担当が、この転記を自業務の重複ではなく回答部品として使うと言うか | Proceed | Hold(宛先リストから安全側を外す) |

KQ1が入口である。**SOTIF由来の要求が部品側RFQまで降りてきている事実が確認できない限り、この枝に工数を割かない。**

## Kill条件

- KQ1がNo: SOTIF要求が部品に降りてこない → この枝をKillし、SPD008はvehicle health / 診断・品質宛先のみで続ける
- KQ3がYes: 既存安全成果物で足りる → Kill
- 価値説明に安全保証・SOTIF適合証明・故障予測が必要になる → Stop
- 作業が(a)のプロセス支援・分析代行へ滑り始める → 既存Killへ接続して止める

## 故障予測の判定維持について

今回の検討は、故障予測の見込みを変えない。**厳しい、のままである。**

理由(既往結論の再確認):

1. 当てるために必要なデータ(交換結果、市場故障履歴、フィールドoutcome)はOEM / サービス側にあり、EPSサプライヤ単独では検証も主張もできない
2. 「交換時期が分かる」「故障を予測できる」は本Repoの禁止主張であり、言った瞬間に安全保証・保証費削減の責任問題に接続する
3. 予測メンテナンス商品は、fleet / テレマティクス / OEMプラットフォーム側に既存プレイヤーが厚い

SOTIF転記(c)は、この代替ではない。予測(いつ壊れるか)を捨てて、**説明(何が起きていたか)**に価値を置き直した現行路線の、宛先が1つ増える話である。

## 実施条件(内部資料の扱い)

KQ1(RFQ / 安全要件の中身)とKQ2([docs/123](123_steering_predictive_diagnostics_power_monitor_program_question_sheet.md) の照合)は、いずれも内部資料への接触が必要である。
現行方針(公開情報は使う、内部資料は使わない)では、これらを次アクションに置かず、**内部資料を使える条件になった場合だけの実施条件**として保存する。

## 次の作業

1. KQ1 / KQ2は実施条件として保存する。専用の調査は起こさない
2. 現行方針で進められるのは、SOTIF運用フェーズ要求が部品サプライヤへ降り始めているかの公開情報(業界動向、規格解説、OEM公開要件)の観測だけである。これも専用調査ではなく、SPD本線の公開情報確認のついでに見る
3. 内部資料を使える条件でKQ1がYesになった場合のみ、docs/122 payloadへのboundary行追加とtriggering condition候補リストの再編を実施する

## Sources

- [ISO 21448:2022 Road vehicles — Safety of the intended functionality](https://www.iso.org/standard/77490.html): SOTIF規格本体。設計・検証・妥当性確認に加え、運用フェーズの活動を含む
- [ISO 21448:2022 preview (ANSI webstore)](https://webstore.ansi.org/preview-pages/ISO/preview_ISO+21448-2022.pdf): 規格構成の公開プレビュー
- [UNECE R157 (ALKS) 概説](https://efs.consulting/en/insights/article/information-security/unece-r157/): L3自動運転の要求枠組み
- [UN R79 / SbW homologation 概説 (ATIC)](https://www.atic-ts.com/european-assisted-driving-systems/): 操舵装置の正常時・故障時要求。電源等の支援システムも対象
- [Standardization for a Steer-by-Wire vehicle (Springer)](https://link.springer.com/content/pdf/10.1007/978-3-662-71064-7_11): SbWの標準化動向
