# EPS Coverage Benchmark Business Value Deep Dive

## 結論

`EPS Diagnostic / Robustness Coverage Benchmark` は、**単独SaaSや汎用HILツールとしては筋が悪い**。
その領域には既にHIL、simulation、validation tool、log analysis、test automationの強い既存プレイヤーがいる。

ただし、以下の形ならビジネス価値が出る可能性はある。

> EPSサプライヤ向けに、公開市場で繰り返すEPS pain familyを、既存DTC/freeze frame/extended data、reader、HILS/bench/vehicle evaluationのcoverage matrixへ変換し、program横断の診断・評価・ソフトrelease gateで使える短期assessmentにする。

つまり売り物は `ツール` ではなく、最初は **市場pain-to-coverage変換の専門assessment**。
RCA/8Dは副産物に下げる。

現時点の評価:

| 観点 | 評価 |
|---|---|
| 市場需要 | ある。SDV化、E/E複雑化、HIL/virtual validation需要、EPS software/failsafe recall文脈と接続できる。 |
| EPSサプライヤ適合 | ある。診断仕様、calibration/failsafe、HILS/bench、reader、DTC semanticsはサプライヤ側の手札。 |
| 差別化 | 条件付き。HILツールではなく、EPS公開市場painを診断/評価coverageへ翻訳する点に限定すれば差分が出る。 |
| スケール | 中。個別caseよりは良いが、最初はNRE/assessment。platform化は複数program採用後。 |
| 最大リスク | 既存の診断設計レビュー、validation plan、safety case、HILS test planと差分がないこと。 |

## 市場需要

外部ソースから見える市場需要は、直接には `EPS coverage benchmarkが欲しい` ではない。
より大きな需要は以下。

| 市場需要 | 外部シグナル | この仮説への意味 |
|---|---|---|
| SDV化でE/E architectureとsoftware validationが複雑化 | AVL HiLはSDV、複雑E/E、CI/CD、automated test factoryを前提にHIL validation需要を訴求している | 開発・評価チームは早く、安全に、繰り返し検証する圧力を受けている |
| HIL/virtual validationで早期検証したい | AVL、NI、Ansys、IPG、MTSなどがHIL/SIL/virtual validationを訴求 | validation budgetは存在するが、ツール市場は既に混雑 |
| steering/EPSはHIL/bench対象として明確 | MTS mHIL Steer、EPS/SBW HIL systemsなどが存在 | EPS/SBW固有の評価市場はある |
| software/calibration起因のrecallが続く | NHTSA/公開recallでEPS software calibration/failsafe、stop-start low-speed power steering assist lossが見える | software/failsafe coverageやrelease gateに接続しやすい |

参照:

- AVL HiL: https://www.avl.com/en/development-speed-and-methodology/avl-hil
- IPG Automotive Fail Safe Tester: https://www.ipg-automotive.com/en/products-solutions/hardware/fail-safe-tester/
- MTS mHIL Steer: https://www.mts.com/en/products/automotive/hybrid-simulation-solutions/mhil-steer
- NI virtual validation: https://www.ni.com/en/solutions/transportation/hardware-in-the-loop/veristand-virtual-validation.html
- Ansys autonomous vehicle validation: https://www.ansys.com/content/ansysincprogram/en-us/home/applications/autonomous-vehicle-validation.html
- NHTSA 2024 Annual Recalls Report: https://www.nhtsa.gov/sites/nhtsa.gov/files/2025-04/2024-annual-recalls-report.pdf

## 未解決の痛み

この事業仮説の痛みは、`データをもっと取る` ではない。

本当の痛みはこれ。

> 公開市場で繰り返し問題化するEPS scenarioが、自社EPSの診断仕様、HILS/bench評価、software/failsafe release gateでどこまでcoverageされているか、program横断で説明しにくい。

これは、既存HILツールや既存DTC仕様書だけでは埋まりにくい可能性がある。

なぜなら、HILツールは試験環境を提供するが、`どの市場painを、どのEPS factsで、どこまで説明すべきか` まではEPSサプライヤ側のドメイン判断になるからである。

## Future Need

| Field | Answer |
|---|---|
| Stated need | 市場で揉めるEPS共通scenarioに対して、診断・評価coverageが足りているか知りたい |
| Current workaround | 過去不具合、DTC仕様、HILS test plan、OEM要求、品質報告を個別にレビューする |
| 5-10 year worst future | software updateや新platformで似たEPS painが繰り返し出て、後から「なぜこのscenarioを評価していなかったか」と問われる |
| Best future | program reviewやRFQ/DRで、公開市場pain familyごとに「既存診断/評価でここまでcover済み」と説明できる |
| Desired emotion | 防御可能性、安心、説明責任を果たせる感覚、後手に回らない感覚 |
| True need | EPS市場painを、program横断の診断coverage/評価coverage/release gateへ変換する標準化された比較表 |
| Buyer / user | Diagnostic engineering、validation/HILS、software calibration、platform/program management |
| Budget path | Program NRE、diagnostic design review、validation planning、software release gate改善 |
| Proposed offer | EPS Diagnostic / Robustness Coverage Benchmark |
| Proof demo | FAM08またはFAM02の1ページcoverage benchmark sample |
| Kill criteria | 既存HILS plan / diagnostic review / safety caseと差分がない |

## 価値が出る条件

この線で価値が出るのは、以下の条件を満たす場合だけ。

| Condition | Why it matters |
|---|---|
| Public pain familyが評価scenarioへ落ちる | `市場事例集` で止まると価値が弱い |
| 既存DTC/freeze frame/extended dataのcoverage判断に使える | 既存診断との差分確認が主価値 |
| HILS/bench/vehicle evaluationの試験項目に変換できる | validation budgetに接続できる |
| 複数program / generationで比較できる | 個別NREで終わらず、再利用性が出る |
| release gate / design review / RFQ / customer qualityのどこかに転記できる | 業務成果物にならないと買われにくい |

逆に、以下なら価値は薄い。

- ただの公開caseリスト
- HIL test vendorの機能紹介
- 既存DTC仕様の焼き直し
- 既存validation planの言い換え
- RCA/8D転記だけ
- ECUログ追加候補だけ

## 初期オファー

### Offer 1: Stop-Start Low-Speed Robustness Benchmark

最初に試すなら `FAM08 stop-start low-speed` がよい。

理由:

- public pain scaleが大きい
- low-speed / stop-start / assist lossというdriver-visible painが明確
- power transient、motor drive、assist state、software/calibrationに落とせる
- EPSサプライヤのbench/HILS/diagnostic手札に近い

成果物:

| Artifact | 内容 |
|---|---|
| Market pain summary | 停止後発進/低速旋回でのassist loss文脈 |
| Expected EPS facts | power transient、motor drive voltage/current、assist command/current、failsafe state、calibration version |
| Coverage matrix | 現行DTC/freeze frame/extended data/reader/HILSでcover済みか |
| Robustness scenario | 0-5 m/s、stop-start、操舵入力、電源/制御遷移 |
| Decision | already covered / gap / no action |

### Offer 2: Software/Failsafe Coverage Benchmark

`FAM11 software/failsafe calibration` も有力。

理由:

- software/calibration起因は今後も増えやすい
- EPSサプライヤがcalibration、failsafe、version、release gateを持つ
- SDV/OTA時代の文脈に接続しやすい

弱点:

- 既存のsafety caseやrelease checklistと重複しやすい
- 内部calibration processを見ないと価値検証できない

### Offer 3: DTC-to-Driver Symptom Coverage Matrix

`FAM03 warning plus effort` は品質/診断に近い。

理由:

- DTC/warningとdriver symptomの接続は説明価値がある
- 既存診断を否定しない
- customer qualityやservice liaisonにも使える

弱点:

- DTC documentationが既に十分なら不要
- 主価値が品質報告に寄ると、またRCA/8D人月に戻る

## ビジネスモデル

初期はSaaSではない。

| Phase | Offer | Revenue model | Goal |
|---|---|---|---|
| P0 | 1-page sample | 無償/低コストdemo | 診断/評価担当が使うか確認 |
| P1 | 2-4 week coverage benchmark assessment | Fixed-fee NRE | 1 programでcoverage matrixを作る |
| P2 | Multi-program comparison | Program/platform NRE | 複数program間のcoverage差分を比較 |
| P3 | Market pain watch update | 軽量retainer | 公開recall/ODI/TSBを四半期更新し、coverage更新候補を出す |
| P4 | Internal toolkit/schema | License/internal platform | 採用後にだけtool化 |

P3/P4を最初から売るのは危ない。
まずP1で、実際にdiagnostic engineering / validationが使うかを見るべき。

## 競合/代替

| Alternative | Why strong | この仮説の逃げ道 |
|---|---|---|
| HIL vendors | 既にvalidation環境、automation、fault injection、simulationを提供 | HIL環境ではなく、EPS public pain-to-coverage taxonomyを提供する |
| Internal validation teams | 既にHILS/bench/test planを持つ | 外部公開market painを横断的に取り込み、program比較にする |
| Diagnostic engineering process | DTC/freeze frame設計は既存 | driver-visible painと診断coverageの説明可能性に絞る |
| Safety case / FMEA / DRBFM | 既にhazard/failure analysisがある | field pain scenarioと既存診断/評価coverageの実務matrixに絞る |
| Warranty / quality process | RCA/8Dは既存 | 主商品から外し、副次artifactにする |

## Chain-of-Verification

| Question | Evidence | Confidence | Impact |
|---|---|---:|---|
| HIL/validation市場に需要はあるか | AVL、NI、IPG、MTS、AnsysなどがSDV、E/E複雑化、HIL/virtual validationを訴求している。 | High | Market pullはある |
| ではHILツールとして売れるか | 既存プレイヤーが強く、ツール市場は混雑している。 | High | ツールではなくdomain assessmentへ修正 |
| EPSサプライヤが主語になれるか | DTC semantics、calibration/failsafe、HILS/bench、readerはサプライヤ側で扱える。 | Medium-High | EPS supplier lensに合う |
| スケールするか | 個別RCAよりはスケールするが、内部診断仕様やprogram差分は残る。 | Medium | 初期はNRE、tool化は後 |
| 顧客は払うか | 公開情報だけでは未証明。budget pathはvalidation/diagnostic design reviewと推定。 | Low-Medium | P0/P1で検証必須 |
| 最大のKill条件は何か | 既存validation plan / diagnostic coverage reviewと差分がないこと。 | High | sample reviewで判定 |

## EPSサプライヤとしての判断

### 売る

> EPS Diagnostic / Robustness Coverage Benchmark Assessment

市場で繰り返すEPS pain familyを、対象EPSの既存診断・reader・HILS/bench・software release gateでどこまでcoverageしているかに変換する短期assessment。

### やる

- public EPS pain familyの抽出
- FAM08 / FAM02 / FAM11などのcoverage matrix sample
- DTC/freeze frame/extended data/reader欄の棚卸し
- HILS/bench scenario checklist化
- already covered / gap / no action判定
- 必要時のみcustomer quality/RCA向けsummaryを作る

### やらない

- HILツールを作る
- generic validation platformを売る
- RCA/8Dを主商品に戻す
- ECU追加ログを最初から提案する
- 故障予測/RULを主張する

## 次アクション

最短の検証はこれ。

> `FAM08 stop-start low-speed` で、1ページのcoverage benchmark sampleを作る。

そのsampleを見て、診断設計/評価/HILS担当が以下のどちらを言うかで決める。

Proceed:

- これはprogram reviewやdiagnostic design reviewに使える
- 既存HILS planとの差分確認に使える
- 他programにも横展開できる

Kill:

- これは既存HILS test planに既にある
- DTC/freeze frame仕様書の焼き直しでしかない
- 公開caseから評価条件へ落ちていない
- RCA/8D転記以外の価値がない
