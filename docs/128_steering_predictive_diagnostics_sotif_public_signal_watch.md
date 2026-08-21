# SOTIF Public Signal Watch

## 結論

[docs/126](126_steering_predictive_diagnostics_sotif_contribution_prospect.md) のKQ1(SOTIF由来の監視要求が部品サプライヤへ降りてきているか)を、公開情報の範囲で観測した。

結果は次である。

1. **規格そのものに、部品サプライヤの参加経路が公式に存在した**。ISO 21448は、サプライヤが全体システムを知らずに部品を開発する場合の扱いとして **SOTIF-EooC**(SOTIF-related Element out of Context)を定義している。部品の使われ方の前提(assumptions of use)と、機能不足(functional insufficiency)の**許容発生率の目標**を仮定として置き、OEM統合時に検証する形である。つまりSOTIF要求は構造的に部品側へ降りる設計になっている
2. **Tier 1最大手(Bosch)が、SOTIF定量化をサプライヤの武器として公開し始めている**。Boschは運転者状態eventとシステムfault severityから故障率を式で計算する定量SOTIF手法の特許(US12330693B2)を公開しており、2026年はL3自動運転の実路試験ライセンス取得(中国・無錫、2026年3月〜)、steer-by-wireの量産開始(中国複数OEM)、brake-by-wireの5社供給契約と、by-wire×L3の展開を加速している
3. ただし、**「SOTIF由来のfault未満監視要求が、EPSサプライヤのRFQに実際に書かれている」ことの公開確認はできなかった**。KQ1の最終確認は引き続き内部資料条件である

判定: SOTIF枝(docs/126のoption c)の位置づけを、「受け身の実施条件待ち」から「**KQ1がYesになる公算が公開情報で補強された実施条件待ち**」へ半歩上げる。ただしProceedにはしない。

なお、ユーザ指摘の「Bosch 2026展示会でのSOTIF展示」は、今回参照できた公開情報(CES 2026プレス、Auto China 2026プレス)では**展示項目としてのSOTIFを直接確認できなかった**。確認できたのは特許と、by-wire / L3の事業展開である。展示での言及を確認できる一次情報が見つかれば、この表に追記する。

追加行は [data/steering_predictive_diagnostics_sotif_contribution_prospect.tsv](../data/steering_predictive_diagnostics_sotif_contribution_prospect.tsv)(SOTIF013〜016)に置く。

## Rule Check

今回の観測では、[AGENTS.md](../AGENTS.md) の次を適用する。

1. `Market Demand First`
2. `Natural Language First`
3. `EPS Supplier Lens`
4. `Mandatory Rule Check Before Stop / Kill / Archive`

確認結果:

- 公開情報のみを使用した(内部資料は使っていない)
- 公開シグナルは、KQ1の公算を補強する材料であり、KQ1の確認そのものではないと明記した
- Boschのシグナルは市場変化を示す材料として扱い、商品価値の証明には使わない(SbW調査時と同じ扱い)
- 判定をProceedへ上げず、実施条件待ちを維持した

## 観測したシグナルの意味

### SOTIF-EooC: 部品サプライヤの公式な参加形式

EPSサプライヤの言葉で言うと、次である。

> OEMがSOTIF対象システム(ADAS / AD / by-wire操舵)にEPSを組み込むとき、規格上、EPS側は「この使われ方の前提で、この種の機能不足はこの発生率以下」という仮定を差し出す形で参加する。

ここからSPD008への含意が1つ出る。
仮定した発生率は、市場投入後に本当にその範囲に収まっているかを誰かが確認し続ける必要がある。
**EPS内部でしか観測できないfault未満の機能影響context(SPD008 payload)は、この「仮定の市場検証」への部品側インプットになり得る。**
これは docs/126 の option (c) の言い直しであり、規格上の受け皿(EooCの仮定)が具体的に特定できたことが今回の前進である。

### Boschシグナル: 競合環境の変化

- 定量SOTIF手法の特許公開は、「SOTIF定量化はOEMの仕事」から「Tier 1が武器として持つ能力」への移行を示す
- steer-by-wire量産開始とL3実路試験は、操舵がSOTIF対象システムの中核部品になる流れを裏付ける
- 競合リスクも同時に示す: Boschが手法(methodology)で先行しているため、EPSサプライヤが今から手法で勝負するのは筋が悪い。差分は引き続き「**サプライヤEPS内部の観測事実**」に限定する(docs/126の禁止事項と整合)

## 判定への反映

| 項目 | 変更前 | 変更後 |
|---|---|---|
| SOTIF枝の位置づけ | 実施条件待ち(受け身) | 実施条件待ち(KQ1 Yesの公算が公開情報で補強) |
| KQ1 | 未確認 | 未確認のまま。ただし規格構造(EooC)と競合動向は降りてくる方向を支持 |
| 差分の言い方 | 観測事実の提供 | 変更なし。手法勝負はしない(Bosch先行) |
| 次の観測トリガ | ついで観測 | Bosch/Tier 1のSOTIF関連の展示・発表、EooC実務の公開事例が出たら追記 |

## 次の作業

1. SPD本線の実施条件待ちは変わらない(docs/123の照合が最優先のまま)
2. 内部資料を使える条件になったら、KQ1の確認質問に「RFQまたは安全要件にSOTIF-EooCの仮定(assumptions of use、機能不足の許容発生率)の提出・検証要求が含まれるか」という具体形を使う(docs/126のKQ1を1段具体化した)
3. Bosch 2026展示でのSOTIF言及の一次情報が見つかれば本表へ追記する

## Sources

- [ISO 21448 SOTIF解説(Jama Software)](https://www.jamasoftware.com/requirements-management-guide/automotive-engineering/sotif/): SOTIF-EooC(部品サプライヤの参加形式)、assumptions of use、機能不足の許容発生率
- [Bosch ADAS patents 2026 trends(PatSnap)](https://www.patsnap.com/resources/blog/articles/bosch-adas-patents-11745-filings-reveal-2026-trends/): 定量SOTIF手法特許 US12330693B2 の解説(二次情報)
- [Auto China 2026: Bosch pushes ahead with Level 3(Bosch公式プレス)](https://www.bosch-presse.de/pressportal/de/en/auto-china-bosch-pushes-ahead-with-level-3-highly-automated-driving-282491.html): L3実路試験ライセンス(無錫、2026年3月〜)、steer-by-wire量産、brake-by-wire供給契約
- [CES 2026: Bosch(Bosch公式プレス)](https://us.bosch-press.com/pressportal/us/en/press-release-29504.html): CES 2026出展内容(SOTIF展示の直接言及は確認できず)
- [Bosch showcases Level 3 automated driving in China(electrive)](https://www.electrive.com/2026/04/24/bosch-showcases-level-3-automated-driving-in-china/): L3展開の二次情報
