# 258. Kaggle再調査と、新しい候補1件の取得前評価

> 「あれだけKaggleにあってないのかな？」(2026-09-01)

**指摘は正しかった。**最近の再調査3本([docs/214](214_dataset_reinventory_2026_08.md),
[235](235_pre_acquisition_survey.md), [242](242_survey_appendix_read.md))に **Kaggleは1件も出てこない。**
Kaggleを見たのは事業フェーズの [docs/87](87_kaggle_each_id_deep_dive.md)〜[95](95_predictive_value_continue_final_decision.md) であり、
**R12・R13という要件が [docs/238](238_data_requirement.md) で立つ前である。**

## 結論

> **Kaggleからは、R12(故障が出たり消えたりする)・R13(発現時刻の正解)を満たすものは出なかった。**
> **ただしKaggle経由の検索で、別の要件を満たす新しい候補が1件出た。**

## Kaggle側で当たったもの

| 候補 | 判定 |
|---|---|
| Car ECU Datalogs | **説明を読めず。**Kaggleのページは動的生成でreadmeが取れない |
| Electrical Wiring Faults Detection | 同上 |
| Engine Failure / Fault Detection Data 各種(同一投稿者) | 表形式の予知保全データ。**R1(実機)を満たす記述が無い** |
| Induction Motor Fault Dataset | 既知の軸受・誘導機系。**R12不成立** |
| IoT-Integrated Predictive Maintenance | 同上 |
| Power System Faults / Power Grid Fault Detection | 系統故障。**対象機構が違う** |
| EV Battery and Drivetrain Fault Diagnosis | 電池・駆動系。**EPSのパワー段ではない** |

**手順上の限界を記録する: Kaggleのデータセット説明は、認証なしの取得では読めない。**
検索結果の要約からしか判断できておらず、**これは [docs/174](174_contact_variance_results.md) で
「検索結果の要約だけで採用を決めた」と是正したのと同じ弱さである。**
断定は「R12を満たすものは**見つからなかった**」までであり、「**存在しない**」ではない。

## 新しい候補 — 産業用電動機、100 kHzの三相電流

Data in Brief 掲載、CC BY 4.0、約60 GB([PMC12361783](https://pmc.ncbi.nlm.nih.gov/articles/PMC12361783/))。

| 要件 | 判定 |
|---|---|
| R1 実機 | **満たす。**現代電機・暁星の実機 |
| R2 スイッチ動作 | **満たす。**インバータ駆動の三相誘導機 |
| R3 動作点が実測で記録 | **満たす。**トルクを25.6 kHzで測定 |
| **R11 スイッチングが見える速度** | **満たす。三相電流 100 kHz。** 本Repoで初めてである |
| R5 同型3台以上 | **満たさない。**1/3/5/7.5 HP と出力が全部違う |
| R7 健全な対照 | **満たす。**機体ごとにNormal条件あり |
| **R12 断続** | **満たさない。**故障は人為的に作り込み、試験中は恒久 |
| **R13 発現時刻の正解** | **満たさない。**run-to-failureが無く、固定した重症度の断面のみ |

> **R12・R13は満たさない。**したがって**本研究の中心の問いには答えない。**

**ただし、本Repoが一度も測れていない問いには答えうる:**

> **動作点を意図的にランダムに振り、かつ実測で記録した実機で、
> 個体基準＋動作点正規化は機能するか。**

[docs/205](205_sign_free_deviation_results.md) は実車で動作点正規化を取り下げた。
[docs/237](237_within_condition_results.md) は、動作点を保持した区間が短すぎて測れなかった。
**この候補は「4%と16%のランダム変動」を意図的に加えており、トルクで実測している。**

**取得は保留する。**60 GBであり、[AGENTS.md](../AGENTS.md) の「取得前に見どころを評価する」に従って
[data/dataset_prospect.tsv](../data/dataset_prospect.tsv) に記録するに留める。
**中心の問い(R12/R13)には答えないので、優先度は高くない。**

## Rule Check

- **ユーザの指摘が正しかったこと(Kaggleが再調査から抜けていた)を先頭に書いた**
- Kaggleのreadmeを読めなかったという**手順上の限界を記録し、「存在しない」と書かなかった**
- 新候補を、**R12/R13を満たさないと明記したうえで**、別の問いに使えると分けて書いた
- 60 GBを**取得せずに評価だけ記録した**
