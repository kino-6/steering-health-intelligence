# Sources and Attribution

このリポジトリの分析は、すべて**公開データ**だけで行っている。

**方針: 生データは再配布しない。** 取得した元データ（合計約18GB）は `.gitignore` で除外してあり、
リポジトリに含まれるのは (1) 自分で計算した集計値 `data/*.tsv`、(2) 再取得・再現用のスクリプト `scripts/*.py`、
(3) レポート `generated/*.html`、(4) 判断の記録 `docs/*.md` だけである。
元データが必要な場合は、下記の出典から各自で取得すること。

### ISO 21448:2022 公開プレビュー

- 入手元: [iTeh 公開サンプル](https://cdn.standards.iteh.ai/samples/77490/d9843a45e11947e0aa79aaf2f00b65a8/ISO-21448-2022.pdf)(2026-09-01取得)
- **読めるのは目次(全条項の番号と表題)と、3章の用語定義のうち 3.1〜3.12 まで。**
- **本文(5〜13章の要求文)は有償であり読んでいない。**[docs/266](docs/266_sotif_conformance_protocol.md) 以降の
  対応付けは、**この範囲だけを根拠とする。**条項レベルの適合主張はしない。

## 一覧

| # | ソース | 提供者 | ライセンス | 出典表示 | 取得日 | ローカル（gitignored） |
|---|---|---|---|---|---|---|
| S1 | MOT test results / test item extracts (2024, 2025) | DVSA / DfT（英国） | **Open Government Licence v3.0** | **必須** | 2026-07-11 | `.dvsa_mot/` (約17GB) |
| S2 | ODI FLAT files: complaints, recalls | NHTSA（米国運輸省） | 米国政府著作物・パブリックドメイン | 任意 | 2026-07-09 | `.nhtsa_flat/` (約2.1GB) |
| S3 | ODI complaints API (`complaintsByVehicle`) | NHTSA | 同上 | 任意 | 2026-07-07 | `.nhtsa_cache/` (約19MB) |
| S4 | commaSteeringControl | comma.ai | **MIT License** | **必須** | 2026-07-11 | `.public_log_cache/` (約651MB) |
| S5 | リコール届出内容の分析結果／不具合情報（集計PDF） | 国土交通省 | 政府標準利用規約（第2.0版） | 必須 | 2026-07-12 | `.jp_mlit/` (約28MB) |
| S6 | ODI recall / TSB / investigation 個別文書（PDF） | NHTSA | 米国政府著作物・パブリックドメイン | 任意 | 随時 | （キャッシュなし。URLのみ記録） |
| S7 | 三相PMSM 固定子故障データセット（**1.0 / 1.5 / 3.0 kW**） | KAIST（Data in Brief 2023） | **CC BY 4.0** | **必須** | 2026-08-22 / **1.5・3.0 kWは2026-08-26** | `.pmsm_fault/` (約7GB) |
| S8 | MOSFET Thermal Overstress Aging（run-to-failure） | NASA PCoE | 米国政府著作物・パブリックドメイン | 任意 | 2026-08-23 | `.nasa_pcoe/` (約7.5GB) |
| S9 | SOReDD（電磁リレーの run-to-failure） | Uni Stuttgart IAS | **CC BY 4.0** | **必須** | 2026-08-23 | `.soredd/` (約3.1GB) |
| S12 | Capacitor Electrical Stress（コンデンサ run-to-failure、10/12/14 V） | NASA PCoE | 米国政府著作物・パブリックドメイン | 任意 | 2026-09-01 | `.nasa_cap/` (約4.7GB) |

---

## S1. DVSA MOT testing data（英国車検）

- 取得元: <https://www.gov.uk/government/collections/anonymised-mot-tests-and-results>
- ファイル: `dft_test_result_extracts_2024.zip`, `dft_test_result_extracts_2025.zip`,
  `dft_test_item_extracts_2024.zip`, `dft_test_item_extracts_2025.zip`, `item_detail.csv`, `item_group.csv`
- ライセンス: [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)

> Contains public sector information licensed under the Open Government Licence v3.0.
> Source: MOT testing data, Driver and Vehicle Standards Agency (DVSA) / Department for Transport.

- 派生（このリポジトリに含まれるもの、すべて**集計値**）:
  | 出力 | スクリプト | 粒度 |
  |---|---|---|
  | `data/dvsa_mot_steering_2025.tsv` | `scripts/dvsa_mot_steering_rates.py` | 車齢別（65行） |
  | `data/dvsa_mot_concentration_2025.tsv` | `scripts/dvsa_mot_concentration.py` | メーカー／モデル別（97行） |
  | `data/mot_advisory_longitudinal.tsv` | `scripts/mot_advisory_longitudinal.py` | グループ×車齢帯別（12行） |
  | `data/mot_cause_breakdown.tsv` | `scripts/mot_cause_breakdown.py` | パワーステアリング原因族別の先行率（10行） |
  | `data/dvsa_mot_mode_split_2025.tsv` | `scripts/dvsa_mot_mode_split.py` | モデル×故障モード別（5行） |
  | `data/eps_specific_precedence.tsv` | `scripts/eps_specific_precedence.py` | EPS固有項目の群×車齢帯（12行） |
  | `generated/dvsa_mot_steering_2025.html` | `scripts/dvsa_mot_steering_rates.py` | 同上 |

  個々の検査記録は一切含まない。元データ自体が匿名化済みだが、本リポジトリはさらに集計後の値のみを保持する。

## S2 / S3 / S6. NHTSA（米国運輸省道路交通安全局）

- 取得元: <https://www.nhtsa.gov/nhtsa-datasets-and-apis>
- ファイル: `FLAT_CMPL.zip`（苦情）, `FLAT_RCL_POST_2010.zip`（リコール）, 各 layout ファイル
- API: `https://api.nhtsa.gov/complaints/complaintsByVehicle?make={make}&model={model}&modelYear={year}`
- ライセンス: 米国連邦政府の著作物であり、著作権による保護を受けない（パブリックドメイン）。出典表示は義務ではないが記載する。
- 派生（すべて**集計値**。苦情本文は一切転記していない）:
  | 出力 | スクリプト | 粒度 |
  |---|---|---|
  | `data/steering_cohort_curve_summary.tsv` | `scripts/steering_cohort_curve.py` | コホート別（5行） |
  | `data/recall_detection_results.tsv` | `scripts/recall_detection_model.py` | 判定サマリ（27行） |
  | `data/steering_cohort_backtest.tsv`, `data/steering_cohort_backtest_silverado.tsv` | `scripts/steering_cohort_backtest.py` | バックテスト結果 |
  | `data/recall_miss_structure.tsv` | `scripts/recall_miss_structure.py` | 学習era見逃し構造（12行） |
  | `data/eps_assembly_remedy_split.tsv` | `scripts/eps_assembly_remedy_split.py` | EPS系Assy交換リコール（11行。是正文はリコール公式文でありパブリックドメイン） |
  | `data/eps_sotif_shape_scan.tsv` | `scripts/eps_sotif_shape_scan.py` | SOTIF形状の目印を持つ操舵系リコール（47行） |
  | `data/steering_mode_split.tsv` | `scripts/steering_mode_split.py` | 車種×モード別（13行） |
  | `data/spd008_payload_replay_cases.tsv` | `scripts/spd008_payload_replay.py` | 公開ケース3件 |
  | `data/eps_wearout_mechanism_scan.tsv` | `scripts/eps_wearout_mechanism_scan.py` | 機構グループ別の出現率（6行） |
  | `data/misdiagnosis_rate_scan.tsv` | `scripts/misdiagnosis_rate_scan.py` | 誤診関連語の出現率（6行） |
  | `data/replacement_no_fix_scan.tsv` | `scripts/replacement_no_fix_scan.py` | 交換後に直らない率（6行） |
  | `data/trigger_conditions.tsv` | `scripts/trigger_conditions.py` | 断続故障の発生条件カテゴリ別（10行） |
  | `generated/steering_cohort_curve.html`, `steering_cohort_backtest*.html`, `recall_detection_report.html`, `spd008_payload_replay.html` | 同上 | 同上 |

  `scripts/build_cohort_monthly.py` が生成する中間ファイル `cohort_monthly.tsv` は `.nhtsa_flat/` 配下に置かれ、コミットしていない。

- 個別に参照した一次文書（本文は転記せず、URLと要旨のみ `data/eps_public_market_pain_cases.tsv` 等に記録）:
  Ford 15V-340 / 15S18、GM 17V-414 / 17276、GM TSB 17-NA-158、Ford SSM 49530、
  NHTSA EPS report (13501_812575)、ODI investigation EA11014 / PE25009 ほか。

## 本Repoが手で維持している表

- [data/sotif_eooc_assumption_sheet.tsv](data/sotif_eooc_assumption_sheet.tsv): **手動維持(hand-maintained)。**
  SOTIF-EooC 仮定シート。個々の行は [docs/153](docs/153_sotif_eooc_assumption_sheet.md) 以降の各検証結果を
  EooCの様式へ転記したものであり、単一のスクリプトが生成するものではない。各行の `source` 列が根拠文書を指す。
- [data/dataset_prospect.tsv](data/dataset_prospect.tsv): **手動維持(hand-maintained)。**
  取得前の見どころ評価。何に答えるか、動作点を保持するかランプするか、対照の有無、取得可否と理由([CHECKS.md](CHECKS.md))。
- [data/dataset_coverage.tsv](data/dataset_coverage.tsv): `scripts/dataset_coverage.py` が列挙し、
  **状態の判断は手動**で入れる([CHECKS.md](CHECKS.md))。

## S12. 誤検知の線を不揮発の予算で引くための公開数値（docs/355 → 356、2026-09-13）

**取得したのは数値だけである。データセットのダウンロードはしていない。**

| 量 | 値 | 出所 | 確認日 |
|---|---|---|---|
| 年間運転時間（米） | 60.2 分/日（2022 年） → 366 時間/年 | AAA Foundation for Traffic Safety, American Driving Survey 2022. https://aaafoundation.org/american-driving-survey-2022/ | 2026-09-13 |
| 年間運転時間（英） | 自動車運転者としての trip 363 回/人/年 × 平均 21 分/trip → 127 時間/年 | DfT National Travel Survey 2023（NTS0303 / 本文）。https://www.gov.uk/government/statistics/national-travel-survey-2023 | 2026-09-13 |
| 同、参考 | 全移動手段の移動時間 353 時間/人/年（約 58 分/日） | 同上、NTS 2023 factsheet（NTS0101） | 2026-09-13 |
| データフラッシュ（Infineon AURIX TC3xx） | DF0 128 KB（TC33x〜TC36x）〜 1,024 KB（TC39x）。DF1 は全品種 128 KB | emmtrix の AURIX TC3xx 一覧表（Infineon 資料の転記）。https://www.emmtrix.com/wiki/Infineon_AURIX_TC3xx | 2026-09-13 |
| データフラッシュ（NXP S32K3） | 128 KB（S32K344、S32K312） | NXP AN13388 S32K3 Memories Guide、NXP Community。https://www.nxp.com/docs/en/data-sheet/S32K3xx.pdf | 2026-09-13 |
| データフラッシュ（Renesas RH850） | 256 KB（RH850/F1KH-D8。datasheet 1 ページ目「Data Flash with a capacity of 256 KB」） | RH850/F1KH, F1KM datasheet R01DS0442EJ0100 Rev.1.00 (2023-09-15)。https://www.renesas.com/en/document/dst/rh850f1kh-rh850f1km-datasheet | 2026-09-13 |

**限界。**AURIX の値は一次資料ではなく転記表から取った。NTS の 127 時間は公表値 2 つの積で、DfT が直接公表した「運転者としての年間時間」ではない。

## S13. 仮想回路の損失・熱の式の出典（docs/337 → 338、明記は 2026-09-13）

| 資料 | 何に使ったか | 入手 |
|---|---|---|
| Graovac, Pürschel, Kiep: *MOSFET Power Losses Calculation Using the Data-Sheet Parameters*, Infineon Application Note 2006-07 V1.1 | 導通損 I²R_on、スイッチング損、接合部温度 Tj = T_amb + P·Rth の式 | Infineon の資料ページ（登録が要る gated 配布）。https://www.infineon.com/gated/infineon-70-41484-applicationnotes-en_f72138ac-8173-4b5c-8c8e-63dd1e039074 |

**限界。**スイッチング損は周波数と E_on/E_off からではなく、導通損に対する割合で与えた（docs/337）。
仮想パワーモジュールの漂流の形（ランダムウォーク）はこちらが置いたもので、出典は無い。実素子の漂流は傾向（docs/348）。

## S14. 報告書の様式の出典（docs/359、2026-09-13）

| 資料 | 確認した範囲 |
|---|---|
| Sollaci LB, Pereira MG. The IMRaD structure: a fifty-year survey. J Med Libr Assoc 2004. PubMed 15243643 | 要旨 |
| Nature: How to construct a Nature summary paragraph. https://www.nature.com/documents/nature-summary-paragraph.pdf | 全文 |
| ISO/IEC/IEEE 29119-3:2021 Software testing — Part 3: Test documentation | 目次（§5.2、§7.4）と定義 3.9。standards.iteh.ai のサンプル PDF |
| ISO 26262-8:2018 Road vehicles — Functional safety — Part 8 | 目次（§9.4.3、§9.5）。同上 |
| IEEE 829-2008 test summary report の 8 節 | 二次資料（ISTQB 系の解説） |

## S15. 仮想回路の条件を前提から導くための公開一次資料（docs/360、2026-09-13）

| 資料 | 取った値 | 入手 |
|---|---|---|
| ISO 16750-2（12 V 系の試験電圧） | UB = 12 V、UA = 14 V | 二次資料（Intertek 解説、standards.iteh.ai サンプル）。https://cdn.standards.iteh.ai/samples/76119/f42b46cc6aef47daa9c6612e225b6f35/ISO-16750-2-2023.pdf |
| AEC-Q100 Rev J, Table 1（動作温度グレード） | Grade 0/1/2/3 = 150/125/105/85 °C | http://www.aecouncil.com/Documents/AEC_Q100_Rev_J_Base_Document.pdf |
| Infineon IAUC60N04S6N050H datasheet Rev 1.1（2025-02-13） | 40 V、RDS(on) 4.0 typ / 5.0 max mΩ（VGS 10 V）、ID 60 A（DC）、Tj 175 °C、RthJC 2.9 K/W max、RthJA 35 K/W | 一次資料（PDF 本文を抽出）。https://www.infineon.com/assets/row/public/documents/10/49/infineon-iauc60n04s6n050h-datasheet-en.pdf |
| Infineon IPB70P04P4-09 製品ページ | -40 V、RDS(on) 9.1 mΩ max、RthJC 2 K/W max、-55〜175 °C | https://www.infineon.com/cms/en/product/power/mosfet/automotive-mosfet/ipb70p04p4-09/ |
| onsemi NXV04V120DB1 / SEC-EPS-12V-APM19-GEVB | 「12 V 三相インバータ用の車載パワーモジュール」「EPS 用三相インバータ評価基板」。数値は取れず | https://www.onsemi.com/design/evaluation-board/SEC-EPS-12V-APM19-GEVB |

**限界。**EPS モータの相電流の公開一次資料は見つからず、設計電流は素子の直流定格（60 A）を上限として置いた。
ISO 16750-2 は本文を有償で見ていない。

## S4. comma.ai commaSteeringControl（公開走行ログ）

- 取得元: <https://huggingface.co/datasets/commaai/commaSteeringControl>
- ライセンス: **MIT License**（comma.ai）
- 使用プラットフォーム: `AUDI_Q3_2ND_GEN`, `HONDA_CR-V_2016`, `FORD_MAVERICK_1ST_GEN`, `GENESIS_G70_2018`
- 派生:
  | 出力 | スクリプト | 内容 |
  |---|---|---|
  | `data/steering_log_sign_extraction.tsv` | `scripts/steering_log_sign_extraction.py` | セグメント別の**算出特徴量**（bias / drift / asymmetry / lag / gain_dev / hf_noise とそのz値、938行） |
  | `data/steering_fw_group_comparison.tsv` | `scripts/steering_fw_group_comparison.py` | 特徴量別の群間比較（18行） |
  | `data/steering_window_recurrence*.tsv` | `scripts/steering_window_recurrence.py` | 窓長×再発則の検出率（各126行、4車種） |
  | `data/low_speed_high_steering_proxy_*.tsv` | `scripts/extract_low_speed_high_steering_proxy.py` | 抽出窓の要約 |
  | `data/sotif_eooc_monitor_demo.tsv`, `generated/sotif_eooc_monitor_demo.html` | `scripts/sotif_eooc_monitor_demo.py` | EooC監視デモの実行結果 |
  | `generated/steering_log_sign_extraction.html`, `steering_synthetic_sensitivity*.html` | 上記＋`scripts/steering_synthetic_sensitivity.py` | レポート |
  | `data/real_vehicle_granularity.tsv` | `scripts/real_vehicle_granularity.py` | 車種別の粒度と逸脱の裾（4行） |
  | `data/window_and_firmware.tsv` | `scripts/window_and_firmware.py` | 窓長別の床とfirmware群比較（4行） |
  | `data/intermittent_injection.tsv` | `scripts/intermittent_injection.py` | 注入振幅×継続別の検出率（25行） |
  | `data/internal_signal_injection.tsv` | `scripts/internal_signal_injection.py` | 部品内部信号での検出率（210行。NASA S8と共同） |
  | `data/false_alarm_tradeoff.tsv` | `scripts/false_alarm_tradeoff.py` | 誤検出水準別の検出限界（8行） |
  | `data/fill_spec_blanks.tsv` | `scripts/fill_spec_blanks.py` | 動作点範囲と車検間隔（5行。MOT S4′と共同） |
  | `data/field_timescale.tsv` | `scripts/field_timescale.py` | 断続的アシスト喪失の経過時間・持続・復帰（1,697行。NHTSA FLAT_CMPLと共同） |
  | `data/persistent_event.tsv` | `scripts/persistent_event.py` | 事象の長さ別の最小検出振幅（6行） |
  | `data/step_detector.tsv` | `scripts/step_detector.py` | 段差型検出器の最小検出振幅と走査の代償（4行） |
  | `data/thermal_index.tsv` | `scripts/thermal_index.py` | 動作点を合わせた熱の非対称指数（18行） |
  | `data/no_data_decisions.tsv` | `scripts/no_data_decisions.py` | 必要なADC分解能と、部品内部での持続の効き（KAIST 3機体と NASA S8 共同） |
  | `data/temperature_span.tsv` | `scripts/temperature_span.py` | 出荷時基準値の直線1本が持つ温度幅（6素子×8幅。NASA S8と共同） |
  | `data/element_v2.tsv` | `scripts/element_v2.py` | 記録器の実装検証（6素子。バイト数・沈黙・量子化耐性） |
  | `data/sotif_sheet_audit.tsv` | `scripts/sotif_sheet_audit.py` | EooCシートが実装より強い主張をしていないかの照合 |
  | `data/real_degradation.tsv` | `scripts/real_degradation.py` | 本物の劣化に記録器を通した結果（NASA 6素子＋KAIST 3機体） |
  | `data/slow_channel.tsv` | `scripts/slow_channel.py` | 遅い時間尺度を足した場合の発火（平均長6段階） |
  | `data/power_stage_observables.tsv` | `scripts/power_stage_observables.py` | 過渡記録の3量。記録順と温度の両方で当てた結果 |
  | `data/field_mechanism.tsv` | `scripts/field_mechanism.py` | 断続症状の苦情が名指しする機構（6分類。NHTSA FLAT_CMPLと共同） |
  | `data/inverter_recorder.tsv` | `scripts/inverter_recorder.py` | 実インバータ8故障×8チャネルの発火と誤報 |
  | `data/fingerprint_interval.tsv` | `scripts/fingerprint_interval.py` | 定常性で選んだ出荷時基準値区間と、その誤報・検出 |
  | `data/igbt_recorder.tsv` | `scripts/igbt_recorder.py` | スイッチ動作IGBT 4素子×3観測量の交差検証と発火 |
  | `data/calibration_budget.tsv` | `scripts/calibration_budget.py` | 各データセットが刻める最小の誤報率（5行） |
  | `data/capacitor_recorder_ES10.tsv` | `scripts/capacitor_recorder.py` | コンデンサ10V群7個体の交差検証・発火・誤報 |
  | `data/capacitor_recorder_ES12.tsv` | `scripts/capacitor_recorder.py` | 同 12V群8個体 |
  | `data/capacitor_recorder_ES14.tsv` | `scripts/capacitor_recorder.py` | 同 14V群8個体 |
  | `data/common_mode.tsv` | `scripts/common_mode.py` | 同種チャネル差分での誤報と検出（8チャネル） |
  | `data/demo_recorder.tsv` | `scripts/demo_recorder.py` | 記録器を端から端まで動かした結果（9行） |
  | `data/ml_comparison.tsv` | `scripts/ml_comparison.py` | 線形と one-class 学習3手法の比較（4行） |
  | `data/demo_sotif_signal.tsv` | `scripts/demo_sotif_signal.py` | 宣言しない割合・関係破壊の検出・送信する1件 |
  | `data/n_bank.tsv` | `scripts/n_bank.py` | 平均長バンク {100,200,500}、素子自身の閾値での発火と誤報（6行） |
  | `data/eis_sync.tsv` | `scripts/eis_sync.py` | コンデンサ発火点と最寄り EIS 測定との時間差（個体ごと） |
  | `data/multivariate_spc.tsv` | `scripts/multivariate_spc.py` | 7 特徴の PCA・T²/SPE、run 5 で動く主成分と負荷（6行） |
  | `data/capacitor_regression.tsv` | `scripts/capacitor_regression.py` | コンデンサ 23 個体の劣化状態回帰（個体 LOO、Ridge/HGB、P0/P1） |
  | `data/capacitor_baseline.tsv` | `scripts/capacitor_baseline.py` | 何もしない基準 3 つと Ridge/HGB の比較（23 行） |
  | `data/slow_refusal.tsv` | `scripts/slow_refusal.py` | 遅い側の宣言しない・漂流項の 5 モード比較（6 素子 × 5） |
  | `data/stress_axis.tsv` | `scripts/stress_axis.py` | 漂流の軸を暦時間・累積エネルギー・累積熱負荷で比べた残差（6 行） |
  | `data/boundary_vs_refresh.tsv` | `scripts/boundary_vs_refresh.py` | 境界案と採り直し案の誤報・発火（6 素子 × 4 モード） |
  | `data/changepoint.tsv` | `scripts/changepoint.py` | 傾きの変化による検出。誤報と初発火（6 素子） |
  | `data/unit_ledger.tsv` | `scripts/unit_ledger.py` | 1 個体の不揮発・通信の量と書き込み回数（実測パック） |
  | （画面出力のみ） | `scripts/unit_trace.py` | 1 個体の出荷時基準値・バスフレーム・記録の実バイト列 |
  | `data/enrolment_length.tsv` | `scripts/enrolment_length.py` | 登録標本数を変えたときの実測誤報率と発火（6 素子） |
  | `data/test_count.tsv` | `scripts/test_count.py` | 検定数を絞ったときの検出・誤報・ライン時間（実インバータ） |
  | `data/extrapolation_direction.tsv` | `scripts/extrapolation_direction.py` | 応力群を抜いたときの符号付き偏り（23 個体） |
  | `data/supply_tolerance.tsv` | `scripts/supply_tolerance.py` | 電源変動を注入したときの誤報・検出（3 本 vs 8 本） |
  | `data/lone_sibling.tsv` | `scripts/lone_sibling.py` | 4 本目を入れ替えたときの誤報と、除去の相手だけ与えた場合 |
  | `data/assist_capability.tsv` | `scripts/assist_capability.py` | 測った R_on から計算したアシスト能力（6 素子 × 7 run） |
  | `data/power_module_model.tsv` | `scripts/power_module_model.py` | 30 バイトの記録・2 バイトのバスからの能力復元と誤差 |
  | `data/capability_trace.tsv` | `scripts/capability_trace.py` | バスフレームから連続で出した能力の軌跡（6 素子） |
  | `data/alarm_rate_relevance.tsv` | `scripts/alarm_rate_relevance.py` | 誤報の目標を振ったときの記録件数と分離（6 素子 × 5 水準） |
  | `data/virtual_circuit.tsv` | `scripts/virtual_circuit.py` | 仮想回路 54 条件での出力低下と、拘束の種類 |
  | `data/lifetime_simulation.tsv` | `scripts/lifetime_simulation.py` | 累積ストレス軸での検知・故障の位置（軸の欠陥を発見した実行、docs/340） |
  | `data/virtual_module.tsv` | `scripts/virtual_module.py` | 仮想モジュール 200 個体での検出率と誤検知（劣化速度 7 水準） |
  | `data/drift_removal.tsv` | `scripts/drift_removal.py` | 漂流を消す 3 つの手立ての検出率と誤検知（仮想 200 個体） |
  | `data/drift_shape.tsv` | `scripts/drift_shape.py` | 健全区間の漂流の形（α・自己相関・動作点との相関、実 6 素子と仮想） |
  | `data/reference_channel.tsv` | `scripts/reference_channel.py` | 第 2 の温度を基準に足したときの α・誤報・発火（6 素子） |
  | `data/shared_drift.tsv` | `scripts/shared_drift.py` | 同種チャネルが共有する傾向の割合（実測）と、共有率を振った検知・誤検知（仮想） |
  | `data/capability_threshold.tsv` | `scripts/capability_threshold.py` | 能力の閾値を逸脱の閾値に翻訳したときの、個体ごとの信号対雑音・誤検知・検出 |
  | `data/byte_quality_curve.tsv` | `scripts/byte_quality_curve.py` | バスフレーム・事象記録・出荷時基準値のバイト数を振ったときの復元誤差と、不揮発の割り当てごとの許せる率 |
  | `data/nvm_budget_line.tsv` | `scripts/nvm_budget_line.py` | 誤検知の水準ごとに 397 日で要する不揮発と、割り当てから逆算した許せる率（公開統計 S12 と共同） |
  | `data/recorder_simulation.tsv` | `scripts/recorder_simulation.py` | 出荷時基準値倍率別の沈黙割合（4行） |

  波形そのもの（CSV）は再配布していない。含まれるのは波形から計算した統計量のみ。
  なお、このデータセットは**正常動作中の車両のログ**であり、故障データではない。故障検知の実証には使えない。


## S12. NASA Capacitor Electrical Stress

- 取得元: <https://phm-datasets.s3.amazonaws.com/NASA/12.+Capacitor+Electrical+Stress.zip>（PHM Society ミラー、2026-09-01取得）
- ライセンス: 米国政府著作物・パブリックドメイン
- 内容: **電圧を 10 / 12 / 14 V で保持**したままのコンデンサ run-to-failure。
  10 V 群は **8個体、充放電の過渡波形を1個体あたり 75,826 回、176日間**。EIS も同梱。
- **取得理由**: [docs/282](docs/282_igbt_recorder_results.md) が出した律速
  （誤報1件/時を刻むには判定36,000回分が要る）を満たす、本Repoで初めてのデータ。
  2026-08-30に2回 decline したが、その理由（docs/224の空欄を埋めない）は空欄が閉じたため無効
  （[docs/283](docs/283_method_verification_protocol.md)）。

## S5. 国土交通省（日本）

- 取得元: <https://www.mlit.go.jp/jidosha/carinf/rcl/>
- ファイル: `r06recallbunseki.pdf`（リコール届出内容の分析結果）, `r6-defects.pdf`, `quarter_r7_3.pdf`
- ライセンス: 政府標準利用規約（第2.0版）。出典表示のうえ複製・翻案が可能。
- 派生: なし。個票データが公開されていないため、集計PDFの記載内容を `docs/149` 等で言及したのみ。

---

## 使わなかったデータ

| データ | 理由 |
|---|---|
| Bosch Production Line Performance (Kaggle) | **未使用**。`scripts/generate_pre_shipment_quality_proxy_demo.py` は `SEED=20260609` による**完全な合成データ**を生成しており、Kaggleの実データは取得も使用もしていない。`data/pre_shipment_quality_proxy_*.tsv` は合成データの出力である。 |
| OBD-II / CAN driving behavior ほかKaggle各種 | 候補として `data/public_steering_dataset_inventory.tsv` に列挙のみ。ダウンロード・分析はしていない。 |

## 再現手順

1. 上記 S1〜S5 から元データを取得し、表の「ローカル」列のディレクトリ名で配置する
2. `scripts/` 内の該当スクリプトを実行する（`python scripts/<name>.py`）
3. `data/*.tsv` と `generated/*.html` が再生成される

取得日以降に元データが更新されている場合、数値は本リポジトリの値と一致しないことがある。
各表の値は「取得日」列の時点のスナップショットに対する結果である。

## S7. KAIST 三相PMSM 固定子故障データセット

- 取得元: <https://data.mendeley.com/datasets/rgn5brrgrn/5>（DOI 10.17632/rgn5brrgrn.5）
- ファイル: `1.0kW.zip`（他に 1.5kW / 3.0kW あり。本リポジトリは 1.0 kW 機のみ取得）
- ライセンス: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

> Vibration and current dataset of three-phase permanent magnet synchronous motors with stator faults.
> Data in Brief (2023), KAIST. Licensed under CC BY 4.0.

- 内容: 三相PMSM **3機体（1.0 / 1.5 / 3.0 kW）**、巻線間短絡とコイル間短絡。電流3相100 kHz・振動1ch 25.6 kHz、各120秒
  - 1.0 kW: 2026-08-22取得。層間短絡 severity 0〜21.69%（8段階）、コイル間短絡 0〜7.56%（8段階）
  - **1.5 kW / 3.0 kW: 2026-08-26取得**（[docs/202](docs/202_cross_machine_replication_protocol.md) の再現用。取得前に事前登録をコミット済み）
- 派生（すべて**集計値**。波形は再配布していない）:

  | 出力 | スクリプト | 粒度 |
  |---|---|---|
  | `data/pmsm_measured_signature.tsv` | `scripts/pmsm_measured_signature.py` | severity別の不平衡・逆相比（8行） |
  | `data/pmsm_model_vs_measured.tsv` | `scripts/pmsm_model_vs_measured.py` | モデルとの比較（3行） |
  | `data/capability_second_mechanism.tsv` | `scripts/capability_second_mechanism.py` | severity別 capability 指標と宣言粒度（8行） |
  | `data/motor_fault_types_and_vibration.tsv` | `scripts/motor_fault_types_and_vibration.py` | 故障種×チャネル別の指標と粒度（16行） |
  | `data/cross_machine_replication.tsv` | `scripts/cross_machine_replication.py` | 1.5/3.0 kW の機体別・故障種別指標（13行） |
  | `data/sign_free_deviation.tsv` | `scripts/sign_free_deviation.py` | 3機体5セルの符号なし逸脱指標（20行） |
  | `data/eps_health_element_run.tsv` | `scripts/eps_health_element.py` | 要素の宣言記録（機構別・合成、58行。NASA S8と共同） |

  `data/pmsm_interturn_model.tsv` は物理モデルの出力であり、本データセット由来ではない。

## S8. NASA PCoE — MOSFET Thermal Overstress Aging

- 取得元: <https://phm-datasets.s3.amazonaws.com/NASA/13.+MOSFET+Thermal+Overstress+Aging.zip>（一覧: <https://data.phmsociety.org/nasa/>）
- ライセンス: NASA は米国連邦政府の著作物であり、著作権による保護を受けない（パブリックドメイン）
- 内容: パワーMOSFET の熱過負荷加速劣化。42テスト・106ファイル（.mat）。**うち7 run 揃った6デバイス（Test_8/9/10/11/12/14）が run-to-failure**
- 信号: steadyState（supplyVoltage / packageTemperature / drainSourceVoltage / drainCurrent / flangeTemperature）、transient（500点・dt=2µs の波形4ch）
- 派生（すべて**集計値**。波形は再配布していない）:

  | 出力 | スクリプト | 粒度 |
  |---|---|---|
  | `data/mosfet_precursor.tsv` | `scripts/mosfet_precursor.py` | デバイス×run（42行） |
  | `data/mosfet_precursor_v2.tsv` | `scripts/mosfet_precursor_v2.py` | 同上、温度除去後（42行） |
  | `data/instability_precursor.tsv` | `scripts/instability_precursor.py` | run別の水準逸脱とばらつき（42行） |
  | `data/str_capability_rule.tsv` | `scripts/str_capability_rule.py` | STR capability 指標と3監視の発火run（42行） |
  | `data/capability_declaration_limits.tsv` | `scripts/capability_declaration_limits.py` | 出荷時基準値幅の要求とRth仮定の感度（20行） |
  | `data/pulse_thermal_path.tsv` | `scripts/pulse_thermal_path.py` | パルス自己発熱による熱経路指標（42行） |
  | `data/thermal_headroom_translation.tsv` | `scripts/thermal_headroom_translation.py` | 熱余裕損失への換算（54行） |
  | `data/thermal_resistance_measured.tsv` | `scripts/thermal_resistance_measured.py` | 熱抵抗の直接測定（42行、分離不能の記録） |

## S9. SOReDD — Stuttgart Open Relay Degradation Dataset

- 取得元: <https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/darus-2785>（論文 [arXiv:2204.01626](https://arxiv.org/abs/2204.01626)）
- ライセンス: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

> Stuttgart Open Relay Degradation Dataset (SOReDD), Institute of Industrial Automation and
> Software Engineering, University of Stuttgart. Licensed under CC BY 4.0.

- 内容: 電磁リレー100個体（種別A〜E）を負荷条件別に故障まで開閉。開閉サイクルごとの接触抵抗と波形
- **配布ファイルの不備**: 3ファイルが末尾カンマで不正JSON（読み込み時に修復）、1ファイルが末尾で切断（修復不能）。サイズは配布元マニフェストと一致
- 派生（**集計値のみ**。波形・生時系列は再配布していない）:

  | 出力 | スクリプト | 粒度 |
  |---|---|---|
  | `data/contact_variance_lead.tsv` | `scripts/contact_variance_lead.py` | 個体×窓の水準・変動（13行） |
  | `data/excursion_event_precursor.tsv` | `scripts/excursion_event_precursor.py` | 個体別の突発事象発生率（13行） |

## S10. インバータ駆動PMSM 故障データセット

- 取得元: <https://zenodo.org/records/13974503>（DOI 10.5281/zenodo.13974503）/ 論文 Data in Brief 58 (2025), DOI [10.1016/j.dib.2025.111286](https://doi.org/10.1016/j.dib.2025.111286)
- ライセンス: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — **出典表示が必須**

> Bacha, A., El Idrissi, R., Janati Idrissi, K., Lmai, F.
> "Comprehensive dataset for fault detection and diagnosis in inverter-driven permanent magnet
> synchronous motor systems", Data in Brief 58 (2025). Licensed under CC BY 4.0.

- 取得日: 2026-08-30
- 内容: 三相インバータ（MOSFET IRF540N）+ PMSM（DENSO製オルタネータ改造）+ Arduino制御の実機。
  9条件（正常 / 開放故障2 / 短絡故障3 / 過熱3、いずれもハーフブリッジ単位）。
  ADC生値8列（Ia, Ib, Vdc, Idc, T1〜T3, Vd）、10 Hz、タイムスタンプ付き。合計 10,892 サンプル
- 保存先: `.pmsm_inverter/`（約1.4 MB、gitignore）
- **本Repoが初めて持つインバータ側の故障データ**（KAISTはモータのみ、NASAは単体MOSFET）
- 派生（**集計値のみ**）:

  | 出力 | スクリプト | 粒度 |
  |---|---|---|
  | `data/inverter_signal_requirement.tsv` | `scripts/inverter_signal_requirement.py` | 条件×相の非対称比（9行） |
  | `data/inverter_settled_baseline.tsv` | `scripts/inverter_settled_baseline.py` | 同上、末尾60%基準（9行） |

## S11. NASA PCoE — IGBT Accelerated Aging

- 取得元: <https://phm-datasets.s3.amazonaws.com/NASA/8.+IGBT+Accelerated+Aging.zip>（一覧: <https://data.phmsociety.org/nasa/>）
- ライセンス: NASA は米国連邦政府の著作物であり、著作権による保護を受けない（パブリックドメイン）
- 取得日: **2026-08-30**
- 内容: IGBT(IRG4BC30K) と MOSFET(IRF520Npbf) の熱過負荷加速劣化。
  **ゲートに矩形波を与えたスイッチ動作**と、**ゲートDCの能動領域動作**の**両方**を含む。
  信号は GATE_VOLTAGE / COLLECTOR_VOLTAGE / GATE_CURRENT / COLLECTOR_CURRENT /
  HEAT_SINK_TEMP / PACKAGE_TEMP / TIME。個体別劣化run(Device 2〜5)と、
  区間ごとのパラメトリック特性(Turn On / LeakageIV / Breakdown)
- 保存先: `.nasa_igbt/`（約480MB、gitignore）
- **[docs/199](docs/199_pulse_thermal_results.md) が S8(MOSFET) で見つけた「素子がスイッチとして動いていない」という欠陥は、
  このデータセットのsquare signal側には当てはまらない**
- 派生（**集計値のみ**）:

  | 出力 | スクリプト | 粒度 |
  |---|---|---|
  | `data/pristine_unit_spread.tsv` | `scripts/pristine_unit_spread.py` | 部品族×パラメータ別の個体差と測定ノイズ（6行） |
  | `data/igbt_switching_precursor.tsv` | `scripts/igbt_switching_precursor.py` | 個体×観測量のスイッチング指標（12行） |
  | `data/within_condition_precursor.tsv` | `scripts/within_condition_precursor.py` | 同一条件内での観測量（12行） |
