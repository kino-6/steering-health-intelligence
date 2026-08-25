# Sources and Attribution

このリポジトリの分析は、すべて**公開データ**だけで行っている。

**方針: 生データは再配布しない。** 取得した元データ（合計約18GB）は `.gitignore` で除外してあり、
リポジトリに含まれるのは (1) 自分で計算した集計値 `data/*.tsv`、(2) 再取得・再現用のスクリプト `scripts/*.py`、
(3) レポート `generated/*.html`、(4) 判断の記録 `docs/*.md` だけである。
元データが必要な場合は、下記の出典から各自で取得すること。

## 一覧

| # | ソース | 提供者 | ライセンス | 出典表示 | 取得日 | ローカル（gitignored） |
|---|---|---|---|---|---|---|
| S1 | MOT test results / test item extracts (2024, 2025) | DVSA / DfT（英国） | **Open Government Licence v3.0** | **必須** | 2026-07-11 | `.dvsa_mot/` (約17GB) |
| S2 | ODI FLAT files: complaints, recalls | NHTSA（米国運輸省） | 米国政府著作物・パブリックドメイン | 任意 | 2026-07-09 | `.nhtsa_flat/` (約2.1GB) |
| S3 | ODI complaints API (`complaintsByVehicle`) | NHTSA | 同上 | 任意 | 2026-07-07 | `.nhtsa_cache/` (約19MB) |
| S4 | commaSteeringControl | comma.ai | **MIT License** | **必須** | 2026-07-11 | `.public_log_cache/` (約651MB) |
| S5 | リコール届出内容の分析結果／不具合情報（集計PDF） | 国土交通省 | 政府標準利用規約（第2.0版） | 必須 | 2026-07-12 | `.jp_mlit/` (約28MB) |
| S6 | ODI recall / TSB / investigation 個別文書（PDF） | NHTSA | 米国政府著作物・パブリックドメイン | 任意 | 随時 | （キャッシュなし。URLのみ記録） |
| S7 | 三相PMSM 固定子故障データセット（1.0 kW） | KAIST（Data in Brief 2023） | **CC BY 4.0** | **必須** | 2026-08-22 | `.pmsm_fault/` (約1.7GB) |
| S8 | MOSFET Thermal Overstress Aging（run-to-failure） | NASA PCoE | 米国政府著作物・パブリックドメイン | 任意 | 2026-08-23 | `.nasa_pcoe/` (約7.5GB) |
| S9 | SOReDD（電磁リレーの run-to-failure） | Uni Stuttgart IAS | **CC BY 4.0** | **必須** | 2026-08-23 | `.soredd/` (約3.1GB) |

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
  | `data/dvsa_mot_mode_split_2025.tsv` | `scripts/dvsa_mot_mode_split.py` | モデル×故障モード別（5行） |
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
  | `data/steering_mode_split.tsv` | `scripts/steering_mode_split.py` | 車種×モード別（13行） |
  | `data/spd008_payload_replay_cases.tsv` | `scripts/spd008_payload_replay.py` | 公開ケース3件 |
  | `data/eps_wearout_mechanism_scan.tsv` | `scripts/eps_wearout_mechanism_scan.py` | 機構グループ別の出現率（6行） |
  | `data/misdiagnosis_rate_scan.tsv` | `scripts/misdiagnosis_rate_scan.py` | 誤診関連語の出現率（6行） |
  | `data/replacement_no_fix_scan.tsv` | `scripts/replacement_no_fix_scan.py` | 交換後に直らない率（6行） |
  | `generated/steering_cohort_curve.html`, `steering_cohort_backtest*.html`, `recall_detection_report.html`, `spd008_payload_replay.html` | 同上 | 同上 |

  `scripts/build_cohort_monthly.py` が生成する中間ファイル `cohort_monthly.tsv` は `.nhtsa_flat/` 配下に置かれ、コミットしていない。

- 個別に参照した一次文書（本文は転記せず、URLと要旨のみ `data/eps_public_market_pain_cases.tsv` 等に記録）:
  Ford 15V-340 / 15S18、GM 17V-414 / 17276、GM TSB 17-NA-158、Ford SSM 49530、
  NHTSA EPS report (13501_812575)、ODI investigation EA11014 / PE25009 ほか。

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

  波形そのもの（CSV）は再配布していない。含まれるのは波形から計算した統計量のみ。
  なお、このデータセットは**正常動作中の車両のログ**であり、故障データではない。故障検知の実証には使えない。

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

- 内容: 三相PMSM 1.0 kW / 3000 rpm、巻線間短絡（severity 0〜21.69%、8段階）とコイル間短絡。電流100 kHz・振動25.6 kHz、各120秒
- 派生（すべて**集計値**。波形は再配布していない）:

  | 出力 | スクリプト | 粒度 |
  |---|---|---|
  | `data/pmsm_measured_signature.tsv` | `scripts/pmsm_measured_signature.py` | severity別の不平衡・逆相比（8行） |
  | `data/pmsm_model_vs_measured.tsv` | `scripts/pmsm_model_vs_measured.py` | モデルとの比較（3行） |

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
  | `data/thermal_headroom_translation.tsv` | `scripts/thermal_headroom_translation.py` | 熱余裕損失への換算（54行） |

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
