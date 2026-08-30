# 224. 現在の結論(2026-08-30)

**このRepoに戻ってきたら、まずここを読む。**
[docs/188](188_the_line.md) 以降の2週間で、事前登録した検証を**15件**実行し、**記録器の仕様([docs/225](225_recorder_specification.md))まで到達した。**
**結論は非対称である。**

## 一行

> **「外からは見えない」は完全に立証できた。**
> **「中からは見える」は立証できていない。**
> **そして立証に必要なデータは公開されていない。**

---

## 立証できたこと

### 1. 外部観測は6系統すべてが盲目である

| 観測系統 | 見えない理由 | doc |
|---|---|---|
| NHTSA苦情 | 消費者の自己申告、故障後 | [143](143_recall_detection_results_v2.md) |
| NHTSAリコール | 欠陥確定後 | [143](143_recall_detection_results_v2.md) |
| 英国車検(一般操舵項目) | 目視・保安基準。機構が混ざる | [148](148_dvsa_mot_denominator_verification.md) |
| 英国車検(EPS固有9項目) | 現場が使わない(2,177万台中64台) | [189](189_five_limits_tested.md) |
| commaSteeringControl | 正常走行のみ。重い裾が無い | [221](221_real_vehicle_granularity_results.md) |
| **英国車検(機能系項目)** | **兆候の区分が制度に存在しない** | **[207](207_mot_cause_breakdown_results.md)** |

**6番目が最も強い。**`inoperative` / `malfunctioning` / `warning lamp` には advisory の文言が無い。
**機能は「半分動く」を記録できない。**データが少ないのではなく、**その記録が制度上作られない。**
そして本研究が対象とする断続故障は、まさにこの `malfunctioning` の側にある。

### 2. 現場の痛みは定量できている

- **原因不明・再現せずの言及が 5.0倍**(EPS×断続 vs 全苦情)([185](185_misdiagnosis_quantified.md))
- **134万台**の交換/非交換が、**ECU内部の2値記録**(故障コードの有無)だけで決まっている([190](190_assembly_replacement_meaning.md))
- 車検の実車連結で、兆候のみ→翌年不合格が **24.1倍**(操舵系全体)([150](150_advisory_precedence_verification.md))、
  **33.9倍**(パワーステアリング固有)([207](207_mot_cause_breakdown_results.md))、
  油圧を除いても **22.0倍**([209](209_mot_nonhydraulic_results.md)、ただし中身は腐食1族)

### 3. 個体・セッション基準は必須である(方法上、唯一残った柱)

**全データを通って残った唯一の方法上の主張。**

| 証拠 | doc |
|---|---|
| 母集団閾値が健全な個体を誤警報(NASA Test_10) | [193](193_str_capability_rule_results.md) |
| 測定キャンペーンの段差が故障効果を潰す(KAIST 3機体6セル全部) | [203](203_cross_machine_replication_results.md) |
| 段差はファイルのメタデータ(録音日)から一意に復元できる | [203](203_cross_machine_replication_results.md) |
| 配布データそのものに同じ構造(正常クラスだけ非定常) | [215](215_inverter_dataset_acquisition.md) |
| **実車でも床が車種間1.3倍・同一車種内1.2倍ひらく** | [221](221_real_vehicle_granularity_results.md) [223](223_window_and_firmware_results.md) |

### 4. 実車の観測床が数値になった

EooC仮定シート([data/sotif_eooc_assumption_sheet.tsv](../data/sotif_eooc_assumption_sheet.tsv)、**51項目**)の粒度欄は、
これまで実験室の数字しか持っていなかった。

| 項目 | 値 | doc |
|---|---|---|
| 標本あたりの床(3σ) | **0.19 〜 0.25 m/s²** | [221](221_real_vehicle_granularity_results.md) |
| **0.10 m/s² に必要な窓** | **2.0 〜 5.0 秒** | [223](223_window_and_firmware_results.md) |
| 平均の効き | 白色雑音比 **1.6〜2.3倍 悪い** | [223](223_window_and_firmware_results.md) |

**[docs/144](144_synthetic_sensitivity_results.md) の粒度主張は、実車の雑音構造でも支持された。**
支持されたのは**床が下がること**であり、検出確率90%は合成注入のままである。

### 5. 記録の窓は広く取れる

**「再始動で復帰する」12.5% 対「瞬間的」2.8%**([213](213_trigger_conditions_results.md))。
事象がマイクロ秒のグリッチではなくキーサイクルまで保持されるなら、記録の窓は広く取れる。
**捕捉について得た、唯一の有利な事実である。**

---

## 立証できなかったこと(すべて事前登録つき)

| 落ちたもの | 結果 | doc |
|---|---|---|
| 機体をまたぐ capability **値** | 符号が機体で逆(−1.000 / **+1.000** / +0.400) | [203](203_cross_machine_replication_results.md) |
| 早期警報(個体基準は早く鳴る) | 6中3で不成立。差は0〜1 run | [193](193_str_capability_rule_results.md) |
| 熱経路の劣化 | 6中0。比 0.909〜0.996 | [199](199_pulse_thermal_results.md) |
| 不安定さが水準に先行 | **6中0。**同着3・遅れ2・不発1 | [211](211_instability_precursor_results.md) |
| 相電流だけで故障の場所を特定 | 2回とも不成立。**B相が5/8で最大** | [217](217_inverter_signal_requirement_results.md) [219](219_inverter_settled_baseline_results.md) |
| 動作点正規化 | 実車で **0/4**(2車種は悪化) | [221](221_real_vehicle_granularity_results.md) |
| 振動の向きで故障種を区別 | 4件中2件が逆向き | [203](203_cross_machine_replication_results.md) |

**加えて、観測量の取り違えを1件見つけた。**
docs/165〜197 が「オン抵抗」と呼んでいた量は、能動領域の動作点抵抗だった([199](199_pulse_thermal_results.md))。
NASA試験機は素子をスイッチとして一度も動かしていない。

---

## 到達できないこと

**断続故障そのものである。**

「出たり消えたりする故障」を含む公開データが**1件も存在しない。**

| 探索した先 | 結果 |
|---|---|
| 接点・コネクタの接触抵抗劣化 | **無し**(2026-08-30に再探索。8日前と変わらず) |
| 断続故障の検出ベンチマーク | **無し**(手法の論文はあるがデータ非公開) |
| KAIST PMSM | **恒久**の人工短絡 |
| NASA MOSFET | **恒久**のドリフト |
| インバータ故障データ(新規取得) | **恒久**。遷移も記録されていない([215](215_inverter_dataset_acquisition.md)) |

---

## そして仕様になった(2026-08-30 追記)

**上の「立証できなかったこと」は、捨てるためではなく拘束として使えた。**

[docs/188](188_the_line.md) の一文——「その瞬間の記録を持てるのは部品の中だけ」——を、
**確立済みの数字だけで実装可能な仕様に落とした**([docs/225](225_recorder_specification.md))。
新しいデータは使っていない。

| 仕様項目 | 値 | 根拠 |
|---|---|---|
| **トリガ** | **条件で絞らない。**アシスト有効中は常時武装 | [213](213_trigger_conditions_results.md) — 公正な分母で2.0倍超の条件が1件も無い |
| **窓長** | **5秒以上** | [223](223_window_and_firmware_results.md) — 平均は白色雑音より1.6〜2.3倍効きが悪い |
| **保持** | **不揮発。最低397日(約13か月)** | [213](213_trigger_conditions_results.md) [227](227_filling_spec_blanks_results.md) — 車検2,234万台のp90 |
| **個体基準** | **36バイト。**firmware更新後は取り直す | [196](196_eps_health_element.md) [223](223_window_and_firmware_results.md) |
| **指紋の掃引幅** | **1走行の6.5〜34.8倍** | [227](227_filling_spec_blanks_results.md) |
| **不足したときの代償** | **時間の65.6〜80.7%を黙る** | [229](229_recorder_simulation_results.md) |
| **出力** | **1件24バイト。**容量は障害にならない | [229](229_recorder_simulation_results.md) |
| **主張しないこと** | **7件**(早期警報・能力値・場所特定ほか) | [225](225_recorder_specification.md) |
| **空欄** | **4件**(うち2件は断続故障のデータが出ない限り原理的に埋まらない) | [225](225_recorder_specification.md) |

**落ちた7件が「主張してはならないこと」を決めている。**
仕様が過剰にならないのは、それらを潰したからである。

> **結論は変わらない——解法には届いていない。**
> **しかし「届いていない」の中身が、空欄4件と非主張7件として具体化した。**
> **次に誰かが作るとき、どこが埋まっていてどこが空いているかが分かる。**

---

## この研究の性格

**問題は精密に記述でき、解法の候補は片っ端から潰せたが、解法そのものには届いていない。**

これは失敗ではなく、**公開情報だけで到達できる限界に当たった**ということである。
[AGENTS.md](../AGENTS.md) 1条のとおり、公開情報のみという制約は
**「調査に嘘をつけなくする」ための装置**であり、その装置が正しく働いた結果である。

**潰した候補の一覧(上表)は、同じ道を辿る者の時間を節約する。**これが本研究の主要な資産である。

## 何があれば動くか

**断続故障の瞬間が記録されたデータ**——それだけである。
接点の間欠的な不通、または実車の故障発生時のECU内部記録。**どちらも公開されていない。**

---

## 導線

| 目的 | 行き先 |
|---|---|
| **現在の結論** | **本文書** |
| **記録器の仕様** | **[225](225_recorder_specification.md)** |
| 売るものと言えないことの一覧 | [188](188_the_line.md) |
| 全ドキュメント索引 | [INDEX.md](INDEX.md) |
| セッション復帰 | [Memory.md](../Memory.md) |
| 出典・ライセンス | [SOURCES.md](../SOURCES.md) |
| **自動チェックと再発防止** | **[CHECKS.md](../CHECKS.md)** |
| SOTIF-EooC 仮定シート(51項目) | [data/sotif_eooc_assumption_sheet.tsv](../data/sotif_eooc_assumption_sheet.tsv) |
